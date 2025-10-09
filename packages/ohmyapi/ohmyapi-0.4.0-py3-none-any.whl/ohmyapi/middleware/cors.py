from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from typing import Any, Dict, List, Tuple

import settings

DEFAULT_ORIGINS = ["http://localhost", "http://localhost:8000"]
DEFAULT_CREDENTIALS = False
DEFAULT_METHODS = ["*"]
DEFAULT_HEADERS = ["*"]

CORS_CONFIG: Dict[str, Any] = getattr(settings, "MIDDLEWARE_CORS", {})

if not isinstance(CORS_CONFIG, dict):
    raise ValueError("MIDDLEWARE_CORS must be of type dict")

middleware = [
    (CORSMiddleware, {
        "allow_origins": CORS_CONFIG.get("ALLOW_ORIGINS", DEFAULT_ORIGINS),
        "allow_credentials": CORS_CONFIG.get("ALLOW_CREDENTIALS", DEFAULT_CREDENTIALS),
        "allow_methods": CORS_CONFIG.get("ALLOW_METHODS", DEFAULT_METHODS),
        "allow_headers": CORS_CONFIG.get("ALLOW_HEADERS", DEFAULT_HEADERS),
    }),
]

