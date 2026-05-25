from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.user.schemas import UserResponse, UserCreate, RefreshTokenRequest, RefreshTokenResponse
from api.user.models import User
from api.user.services import create_user, login_user, refresh_user_token
from api.core.db import get_async_session

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(data:UserCreate, session: AsyncSession = Depends(get_async_session)):
    response = await create_user(data, session)
    return response

@router.post("/login", response_model=UserResponse)
async def login(data:UserCreate, session: AsyncSession = Depends(get_async_session)):
    response = await login_user(data, session)
    return response

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    """
    Refresh access token using a valid refresh token.
    """
    response = await refresh_user_token(data.refresh_token)
    return response


