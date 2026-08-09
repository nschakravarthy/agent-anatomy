"""Role-aware request dependencies.

`AuthMiddleware` only puts the authenticated user's uuid on `request.state`, so
anything that needs the account itself — its role, most of all — reloads it
here. The role is read from the database on every request rather than carried
in the JWT: a token lives for 24 hours, and a demoted admin should lose access
immediately, not whenever their token happens to expire.
"""

from fastapi import Depends, HTTPException, Request
from fastapi import status as http_status
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.db import get_async_session
from api.user.models import User, UserRole

async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """The account behind the request's access token."""
    user_id = getattr(request.state, "user", None)
    if user_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    statement = select(User).where(User.uuid == user_id)
    results = await session.execute(statement=statement)
    db_user = results.scalar_one_or_none()
    if not db_user:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )
    return db_user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Gate an endpoint behind the admin role.

    Hiding the Configuration and Analytics tabs in the frontend is only a
    convenience; any endpoint that backs those tabs must depend on this so the
    restriction survives someone calling the API directly.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return user
