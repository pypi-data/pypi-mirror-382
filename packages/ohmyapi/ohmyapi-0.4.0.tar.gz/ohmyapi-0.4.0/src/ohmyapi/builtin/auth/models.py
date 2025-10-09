import hmac
import hashlib
import base64
from functools import wraps
from secrets import token_bytes
from typing import List, Optional
from uuid import UUID

from passlib.context import CryptContext
from tortoise.contrib.pydantic import pydantic_queryset_creator

from ohmyapi.db import Model, field, Q
from ohmyapi.router import HTTPException

import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = getattr(settings, "SECRET_KEY", "OhMyAPI Secret Key")


def hmac_hash(data: str) -> str:
    digest = hmac.new(SECRET_KEY.encode("UTF-8"), data.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8")


class Group(Model):
    id: UUID = field.data.UUIDField(pk=True)
    name: str = field.CharField(max_length=42, index=True)

    def __str__(self):
        return self.name if self.name else ""


class User(Model):
    id: UUID = field.data.UUIDField(pk=True)
    username: str = field.CharField(max_length=150, unique=True)
    email_hash: Optional[str] = field.CharField(max_length=255, unique=True, index=True)
    password_hash: str = field.CharField(max_length=128)
    is_admin: bool = field.BooleanField(default=False)
    is_staff: bool = field.BooleanField(default=False)
    groups: field.ManyToManyRelation[Group] = field.ManyToManyField(
        "ohmyapi_auth.Group", related_name="users", through="usergroups"
    )

    class Schema:
        exclude = ["password_hash", "email_hash"]

    def __str__(self):
        fields = {
            'username': self.username if self.username else "-",
            'is_admin': 'y' if self.is_admin else 'n',
            'is_staff': 'y' if self.is_staff else 'n',
        }
        return ' '.join([f"{k}:{v}" for k, v in fields.items()])

    def set_password(self, raw_password: str) -> None:
        """Hash and store the password."""
        self.password_hash = pwd_context.hash(raw_password)

    def set_email(self, new_email: str) -> None:
        """Hash and set the e-mail address."""
        self.email_hash = hmac_hash(email)

    def verify_password(self, raw_password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return pwd_context.verify(raw_password, self.password_hash)

    @classmethod
    async def authenticate_username(cls, username: str, password: str) -> Optional["User"]:
        """Authenticate a user by username and password."""
        user = await cls.filter(username=username).first()
        if user and user.verify_password(password):
            return user
        return None
