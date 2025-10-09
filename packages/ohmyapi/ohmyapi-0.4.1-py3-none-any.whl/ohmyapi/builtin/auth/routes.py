import time
from enum import Enum
from typing import Any, Dict, List

import jwt
import settings
from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ohmyapi.builtin.auth.models import Group, User

# Router
router = APIRouter(prefix="/auth", tags=["Auth"])

# Secrets & config (should come from settings/env in real projects)
JWT_SECRET = getattr(settings, "JWT_SECRET", "changeme")
JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = getattr(
    settings, "JWT_ACCESS_TOKEN_EXPIRE_SECONDS", 15 * 60
)
REFRESH_TOKEN_EXPIRE_SECONDS = getattr(
    settings, "JWT_REFRESH_TOKEN_EXPIRE_SECONDS", 7 * 24 * 60 * 60
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class ClaimsUser(BaseModel):
    username: str
    email: str
    is_admin: bool
    is_staff: bool


class Claims(BaseModel):
    type: str
    sub: str
    user: ClaimsUser
    roles: List[str]
    exp: str


class AccessToken(BaseModel):
    token_type: str
    access_token: str


class RefreshToken(AccessToken):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenType(str, Enum):
    """
    Helper for indicating the token type when generating claims.
    """

    access = "access"
    refresh = "refresh"


def claims(token_type: TokenType, user: User, groups: List[Group] = []) -> Claims:
    return Claims(
        type=token_type,
        sub=str(user.id),
        user=ClaimsUser(
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            is_staff=user.is_staff,
        ),
        roles=[g.name for g in groups],
        exp="",
    )


def create_token(claims: Claims, expires_in: int) -> str:
    to_encode = claims.model_dump()
    to_encode["exp"] = int(time.time()) + expires_in
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token: str) -> Dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """Dependency: token introspection"""
    payload = decode_token(token)
    return payload


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency: extract user from access token."""
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def require_authenticated(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is an admin."""
    if not current_user:
        raise HTTPException(403, "Authentication required")
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin privileges required")
    return current_user


async def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is a staff member."""
    if not current_user.is_admin and not current_user.is_staff:
        raise HTTPException(403, "Staff privileges required")
    return current_user


async def require_group(
    group_name: str, current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user belongs to the given group."""
    user_groups = await current_user.groups.all()
    if not any(g.name == group_name for g in user_groups):
        raise HTTPException(
            status_code=403, detail=f"User must belong to group '{group_name}'"
        )
    return current_user


@router.post("/login", response_model=RefreshToken)
async def login(form_data: LoginRequest = Body(...)):
    """Login with username & password, returns access and refresh tokens."""
    user = await User.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_token(
        claims(TokenType.access, user), ACCESS_TOKEN_EXPIRE_SECONDS
    )
    refresh_token = create_token(
        claims(TokenType.refresh, user), REFRESH_TOKEN_EXPIRE_SECONDS
    )

    return RefreshToken(
        token_type="bearer",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(refresh_token: str):
    """Exchange refresh token for new access token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    new_access = create_token(
        claims(TokenType.access, user), ACCESS_TOKEN_EXPIRE_SECONDS
    )
    return AccessToken(token_type="bearer", access_token=access_token)


@router.get("/introspect", response_model=Dict[str, Any])
async def introspect(token: Dict = Depends(get_token)):
    return token


@router.get("/me", response_model=User.Schema())
async def me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return await User.Schema().from_tortoise_orm(user)
