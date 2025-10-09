# ohmyapi/core/runtime.py
import importlib
import importlib.util
import json
import pkgutil
import sys
from http import HTTPStatus
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Generator, List, Optional, Tuple, Type

import click
from aerich import Command as AerichCommand
from aerich.exceptions import NotInitedError
from fastapi import APIRouter, FastAPI
from tortoise import Tortoise

from ohmyapi.core.logging import setup_logging
from ohmyapi.db.model import Model

logger = setup_logging()


class Project:
    """
    Project runtime loader + Tortoise/Aerich integration.

    - aliases builtin apps as ohmyapi_<name>
    - loads all INSTALLED_APPS into scope
    - builds unified tortoise config for ORM runtime
    - provides makemigrations/migrate methods using Aerich Command API
    """

    def __init__(self, project_path: str):
        logger.debug(f"Loading project: {project_path}")
        self.project_path = Path(project_path).resolve()
        self._apps: Dict[str, App] = {}
        self.migrations_dir = self.project_path / "migrations"

        if str(self.project_path) not in sys.path:
            sys.path.insert(0, str(self.project_path))

        # Alias builtin apps as ohmyapi_<name>.
        # We need this, because Tortoise app-names may not include dots `.`.
        spec = importlib.util.find_spec("ohmyapi.builtin")
        if spec and spec.submodule_search_locations:
            for _, modname, _ in pkgutil.iter_modules(spec.submodule_search_locations):
                full = f"ohmyapi.builtin.{modname}"
                alias = f"ohmyapi_{modname}"
                if alias not in sys.modules:
                    orig = importlib.import_module(full)
                    sys.modules[alias] = orig
                    try:
                        sys.modules[f"{alias}.models"] = importlib.import_module(
                            f"{full}.models"
                        )
                    except ModuleNotFoundError:
                        pass

        # Load settings.py
        try:
            self.settings = importlib.import_module("settings")
        except Exception as e:
            raise RuntimeError(
                f"Failed to import project settings from {self.project_path}"
            ) from e

        # Load installed apps
        for app_name in getattr(self.settings, "INSTALLED_APPS", []):
            self._apps[app_name] = App(self, name=app_name)

    @property
    def apps(self):
        return self._apps

    def is_app_installed(self, name: str) -> bool:
        return name in getattr(self.settings, "INSTALLED_APPS", [])

    def app(self,
            docs_url: str = "/docs",
    ) -> FastAPI:
        """
        Create and return a FastAPI app.
        """
        import ohmyapi
        return FastAPI(
            title=getattr(self.settings, "PROJECT_NAME", "OhMyAPI Project"),
            description=getattr(self.settings, "PROJECT_DESCRIPTION", ""),
            docs_url=getattr(self.settings, "DOCS_URL", "/docs"),
            version=ohmyapi.__VERSION__,
        )

    def configure_app(self, app: FastAPI) -> FastAPI:
        """
        Attach project middlewares and routes and event handlers to given
        FastAPI instance.
        """
        app.router.prefix = getattr(self.settings, "API_PREFIX", "")
        # Attach project middlewares and routes.
        for app_name, app_def in self._apps.items():
            for middleware, kwargs in app_def.middlewares:
                app.add_middleware(middleware, **kwargs)
            for router in app_def.routers:
                app.include_router(router)

        # Initialize ORM on startup
        @app.on_event("startup")
        async def _startup():
            await self.init_orm(generate_schemas=False)

        # Close ORM on shutdown
        @app.on_event("shutdown")
        async def _shutdown():
            await self.close_orm()

        return app

    # --- Config builders ---
    def build_tortoise_config(self, db_url: Optional[str] = None) -> dict:
        """
        Build unified Tortoise config for all registered apps.
        """
        db = db_url or getattr(self.settings, "DATABASE_URL", "sqlite://db.sqlite3")
        config = {
            "connections": {"default": db},
            "apps": {},
            "tortoise": "Tortoise",
            "migrations_dir": str(self.migrations_dir),
        }

        for app_name, app in self._apps.items():
            modules = list(app.models.keys())
            if modules:
                config["apps"][app_name] = {
                    "models": modules,
                    "default_connection": "default",
                }

        return config

    def build_aerich_command(
        self, app_label: str, db_url: Optional[str] = None
    ) -> AerichCommand:
        """
        Build Aerich command for app with given app_label.

        Aerich needs to see only the app of interest, but with the extra model
        "aerich.models".
        """
        if app_label not in self._apps:
            raise RuntimeError(f"App '{app_label}' is not registered")

        # Get a fresh copy of the config (without aerich.models anywhere)
        tortoise_cfg = self.build_tortoise_config(db_url=db_url)

        # Prevent leaking other app's models to Aerich.
        tortoise_cfg["apps"] = {app_label: tortoise_cfg["apps"][app_label]}

        # Append aerich.models to the models list of the target app only
        tortoise_cfg["apps"][app_label]["models"].append("aerich.models")

        return AerichCommand(
            tortoise_config=tortoise_cfg,
            app=app_label,
            location=str(self.migrations_dir),
        )

    # --- ORM lifecycle ---
    async def init_orm(self, generate_schemas: bool = False) -> None:
        if not Tortoise.apps:
            cfg = self.build_tortoise_config()
            await Tortoise.init(config=cfg)
            if generate_schemas:
                await Tortoise.generate_schemas(safe=True)

    async def close_orm(self) -> None:
        await Tortoise.close_connections()

    # --- Migration helpers ---
    async def makemigrations(
        self, app_label: str, name: str = "auto", db_url: Optional[str] = None
    ) -> None:
        cmd = self.build_aerich_command(app_label, db_url=db_url)
        async with cmd as c:
            await c.init()
            try:
                await c.init_db(safe=True)
            except FileExistsError:
                pass
            try:
                await c.migrate(name=name)
            except (NotInitedError, click.UsageError):
                await c.init_db(safe=True)
                await c.migrate(name=name)

    async def migrate(
        self, app_label: Optional[str] = None, db_url: Optional[str] = None
    ) -> None:
        labels: List[str]
        if app_label:
            if app_label in self._apps:
                labels = [app_label]
            else:
                raise RuntimeError(f"Unknown app '{app_label}'")
        else:
            labels = list(self._apps.keys())

        for lbl in labels:
            cmd = self.build_aerich_command(lbl, db_url=db_url)
            async with cmd as c:
                await c.init()
                try:
                    await c.init_db(safe=True)
                except FileExistsError:
                    pass

                try:
                    # Try to apply migrations
                    await c.upgrade()
                except (NotInitedError, click.UsageError):
                    # No migrations yet, initialize then retry upgrade
                    await c.init_db(safe=True)
                    await c.upgrade()


class App:
    """App container holding runtime data like detected models and routes."""

    def __init__(self, project: Project, name: str):
        self.project = project
        self.name = name

        # Reference to this app's models modules. Tortoise needs to know the
        # modules where to lookup models for this app.
        self._models: Dict[str, ModuleType] = {}

        # Reference to this app's routes modules.
        self._routers: Dict[str, ModuleType] = {}

        # Reference to this apps middlewares.
        self._middlewares: List[Tuple[Any, Dict[str, Any]]] = []

        # Import the app, so its __init__.py runs.
        mod: ModuleType = importlib.import_module(name)

        logger.debug(f"Loading app: {self.name}")
        self.__load_models(f"{self.name}.models")
        self.__load_routes(f"{self.name}.routes")
        self.__load_middlewares(f"{self.name}.middlewares")

    def __repr__(self):
        return json.dumps(self.dict(), indent=2)

    def __str__(self):
        return self.__repr__()

    def __load_models(self, mod_name: str):
        """
        Recursively scan through a module and collect all models.
        If the module is a package, iterate through its submodules.
        """

        # An app may come without any models.
        try:
            importlib.import_module(mod_name)
        except ModuleNotFoundError:
            return

        # Acoid duplicates.
        visited: set[str] = set()

        def walk(mod_name: str):
            mod = importlib.import_module(mod_name)
            if mod_name in visited:
                return
            visited.add(mod_name)

            for name, value in vars(mod).copy().items():
                if (
                    isinstance(value, type)
                    and issubclass(value, Model)
                    and not name == Model.__name__
                ):
                    # monkey-patch __module__ to point to well-known aliases
                    value.__module__ = value.__module__.replace("ohmyapi.builtin.", "ohmyapi_")
                    if value.__module__.startswith(mod_name):
                        self._models[mod_name] = self._models.get(mod_name, []) + [value]
                        logger.debug(f" - Model: {mod_name} -> {name}")

            # if it's a package, recurse into submodules
            if hasattr(mod, "__path__"):
                for _, subname, _ in pkgutil.iter_modules(
                    mod.__path__, mod.__name__ + "."
                ):
                    walk(subname)

        # Walk the walk.
        walk(mod_name)

    def __load_routes(self, mod_name: str):
        """
        Recursively scan through a module and collect all APIRouters.
        If the module is a package, iterate through all its submodules.
        """

        # An app may come without any routes.
        try:
            importlib.import_module(mod_name)
        except ModuleNotFoundError:
            return

        # Avoid duplicates.
        visited: set[str] = set()

        def walk(mod_name: str):
            mod = importlib.import_module(mod_name)
            if mod.__name__ in visited:
                return
            visited.add(mod.__name__)

            for name, value in vars(mod).copy().items():
                if isinstance(value, APIRouter) and not name == APIRouter.__name__:
                    self._routers[mod_name] = self._routers.get(mod_name, []) + [value]
                    logger.debug(f" - Router: {mod_name} -> {name} -> {value.routes}")

            # if it's a package, recurse into submodules
            if hasattr(mod, "__path__"):
                for _, subname, _ in pkgutil.iter_modules(
                    mod.__path__, mod.__name__ + "."
                ):
                    walk(subname)

        # Walk the walk.
        walk(mod_name)

    def __load_middlewares(self, mod_name):
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            return

        getter = getattr(mod, "get", None)
        if getter is not None:
            for middleware in getter():
                self._middlewares.append(middleware)

    def __serialize_route(self, route):
        """
        Convert APIRoute to JSON-serializable dict.
        """
        return {
            "path": route.path,
            "method": list(route.methods)[0],
            "endpoint": f"{route.endpoint.__module__}.{route.endpoint.__name__}",
        }

    def __serialize_router(self):
        return [self.__serialize_route(route) for route in self.routes]

    def __serialize_middleware(self):
        out = []
        for m in self.middlewares:
            out.append((m[0].__name__, m[1]))
        return out

    @property
    def models(self) -> List[ModuleType]:
        """
        Return a list of all loaded models.
        """
        out = []
        for module in self._models:
            for model in self._models[module]:
                out.append(model)
        return {
            module: out,
        }

    @property
    def routers(self):
        out = []
        for routes_mod in self._routers:
            for r in self._routers[routes_mod]:
                out.append(r)
        return out

    @property
    def routes(self):
        """
        Return an APIRouter with all loaded routes.
        """
        out = []
        for r in self.routers:
            out.extend(r.routes)
        return out

    @property
    def middlewares(self):
        """Returns the list of this app's middlewares."""
        return self._middlewares

    def dict(self) -> Dict[str, Any]:
        """
        Convenience method for serializing the runtime data.
        """
        return {
            "models": [
                f"{self.name}.{m.__name__}" for m in self.models[f"{self.name}.models"]
            ],
            "middlewares": self.__serialize_middleware(),
            "routes": self.__serialize_router(),
        }
