from fastapi import HTTPException
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.user.models import User, UserRole
from api.user.schemas import UserCreate
from api.user.utils import get_password_hash, create_access_token, verify_password, refresh_access_token

async def create_user(data: UserCreate, session: AsyncSession):
    statement = select(
        User
    ).where(
        User.email == data.email
    )
    results = await session.execute(statement=statement)
    db_user = results.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(data.password)
    # Create User object. The role is pinned here rather than left to the model
    # default so that self-service registration can never mint an admin, even if
    # the default changes.
    new_user = User(
        email = data.email,
        hashed_password = hashed_password,
        role = UserRole.USER,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    tokens = create_access_token({"user_id": str(new_user.uuid)})

    return {
        "user_id": str(new_user.uuid),
        "role": new_user.role,
        **tokens  # Spread the access_token, refresh_token, token_type, expires_in
    }

async def login_user(data: UserCreate, session: AsyncSession):
    statement = select(
        User
    ).where(
        User.email == data.email
    )
    results = await session.execute(statement=statement)
    db_user = results.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=400, detail="User is not registered")
    hashed_password = db_user.hashed_password
    verified = verify_password(data.password, hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Wrong password")
    tokens = create_access_token({"user_id": str(db_user.uuid)})
    return {
        "user_id": str(db_user.uuid),
        "role": db_user.role,
        **tokens  # Spread the access_token, refresh_token, token_type, expires_in
    }

async def refresh_user_token(refresh_token: str):
    """
    Refresh an access token using a valid refresh token.
    """
    tokens = refresh_access_token(refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    return tokens


