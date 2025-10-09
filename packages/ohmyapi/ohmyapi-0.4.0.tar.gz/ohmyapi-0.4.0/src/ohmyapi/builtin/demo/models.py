from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ohmyapi_auth.models import User

from ohmyapi.db import Model, field


class Team(Model):
    id: UUID = field.data.UUIDField(primary_key=True)
    name: str = field.TextField()
    members: field.ManyToManyRelation[User] = field.ManyToManyField(
        "ohmyapi_auth.User",
        related_name="tournament_teams",
        through="user_tournament_teams",
    )

    def __str__(self):
        return self.name


class Tournament(Model):
    id: UUID = field.data.UUIDField(primary_key=True)
    name: str = field.TextField()
    created: datetime = field.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(Model):
    id: UUID = field.data.UUIDField(primary_key=True)
    name: str = field.TextField()
    tournament: field.ForeignKeyRelation[Tournament] = field.ForeignKeyField(
        "ohmyapi_demo.Tournament",
        related_name="events",
    )
    participants: field.ManyToManyRelation[Team] = field.ManyToManyField(
        "ohmyapi_demo.Team",
        related_name="events",
        through="event_team",
    )
    modified: datetime = field.DatetimeField(auto_now=True)
    prize: Decimal = field.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Schema:
        exclude = ["tournament_id"]

    def __str__(self):
        return self.name
