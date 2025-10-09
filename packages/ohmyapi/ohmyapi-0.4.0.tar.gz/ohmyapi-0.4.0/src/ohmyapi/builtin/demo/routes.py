from typing import List

from ohmyapi.db.exceptions import DoesNotExist
from ohmyapi.router import APIRouter, HTTPException, HTTPStatus

from . import models

# Expose your app's routes via `router = fastapi.APIRouter`.
# Use prefixes wisely to avoid cross-app namespace-collisions.
# Tags improve the UX of the OpenAPI docs at /docs.
router = APIRouter(prefix="/tournament")


@router.get("/", tags=["tournament"], response_model=List[models.Tournament.Schema()])
async def list():
    """List all tournaments."""
    return await models.Tournament.Schema().from_queryset(models.Tournament.all())


@router.post("/", tags=["tournament"], status_code=HTTPStatus.CREATED)
async def post(tournament: models.Tournament.Schema(readonly=True)):
    """Create tournament."""
    return await models.Tournament.Schema().from_queryset(
        models.Tournament.create(**tournament.model_dump())
    )


@router.get("/{id}", tags=["tournament"], response_model=models.Tournament.Schema())
async def get(id: str):
    """Get tournament by id."""
    return await models.Tournament.Schema().from_queryset(models.Tournament.get(id=id))


@router.put(
    "/{id}",
    tags=["tournament"],
    response_model=models.Tournament.Schema.model,
    status_code=HTTPStatus.ACCEPTED,
)
async def put(tournament: models.Tournament.Schema.model):
    """Update tournament."""
    return await models.Tournament.Schema().from_queryset(
        models.Tournament.update(**tournament.model_dump())
    )


@router.delete("/{id}", status_code=HTTPStatus.ACCEPTED, tags=["tournament"])
async def delete(id: str):
    try:
        tournament = await models.Tournament.get(id=id)
        return await tournament.delete()
    except DoesNotExist:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="not found")
