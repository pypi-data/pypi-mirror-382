# OhMyAPI

OhMyAPI is a web-application scaffolding framework and management layer built around `FastAPI`.
It is a thin layer that tightly integrates TortoiseORM and Aerich migrations.

> *Think: *"Django RestFramework"*, but less clunky and instead 100% async.*

It is ***blazingly fast***, extremely ***fun to use*** and comes with ***batteries included***!

**Features**

- Django-like project structure and application directories
- Django-like per-app migrations (makemigrations & migrate) via Aerich
- Django-like CLI tooling (startproject, startapp, shell, serve, etc)
- Customizable pydantic model serializer built-in
- Various optional built-in apps you can hook into your project (i.e. authentication and more)
- Highly configurable and customizable
- 100% async

**Goals**

- combine FastAPI, TortoiseORM, Aerich migrations and Pydantic into a high-productivity web-application framework
- tie everything neatly together into a concise and straight-forward API
- AVOID adding any abstractions on top, unless they make things extremely convenient

## Installation

```
pipx install ohmyapi
```


## Docs

See `docs/` or:

```
poetry run mkdocs serve
```

Go to: [http://localhost:8000/](http://localhost:8000/)
