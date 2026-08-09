import fnmatch
import re

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from api.user.utils import verify_token

from api.core.db import async_engine
from api.core.stages import load_stage
from api.user.models import User
from api.core.config import PUBLIC_PATHS

# Create a session factory once (no yield, no generator)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

def is_public_path(path: str) -> bool:
    """Check if request path is in the public whitelist (supports wildcards)."""
    print("Checking public path:", path)
    print("Status", any(fnmatch.fnmatch(path, pattern) for pattern in PUBLIC_PATHS))
    return any(fnmatch.fnmatch(path, pattern) for pattern in PUBLIC_PATHS)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for docs or public endpoints
        print("Auth Request URL path:", request.url.path)
        if is_public_path(request.url.path):
            return await call_next(request)
        async with AsyncSessionLocal() as session:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Token "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing or invalid Authorization header"},
                )

            token = auth_header.split(" ")[1]

            try:
                token_data = verify_token(token)
                if not token_data:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid or expired token"},
                    )
                
                # Ensure it's an access token (not a refresh token)
                if token_data.get("type") != "access":
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid token type. Access token required."},
                    )
                
                print("Token data:", token_data)
                request.state.user = token_data  # Store user info for downstream handlers
            except Exception:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"},
                )
            
            statement = select(
                User
            ).where(
                User.uuid == token_data.get("user_id")
            )
            results = await session.execute(statement=statement)
            db_user = results.scalar_one_or_none()
            if not db_user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "User does not exist"},
                )
            if not db_user.is_active:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "User is inactive"},
                )
            print("Authenticated user:", db_user.uuid)
            request.state.user = db_user.uuid
            return await call_next(request)

# Matches the stage segment anywhere in the path, so the router's own prefixes
# ("/api/v1/chat") are preserved when the segment is stripped below.
_STAGE_PATTERN = re.compile(
    r"^(?P<prefix>.*?)/agents/stage-(?P<stage>\d{2})(?P<rest>/.*)?$"
)

class StageSelectorMiddleware(BaseHTTPMiddleware):
    """Route requests to the right stage's SpecAgent based on URL prefix."""

    async def dispatch(self, request: Request, call_next):
        match = _STAGE_PATTERN.match(request.url.path)
        print("Stage Selector Request URL Path", request.url.path)
        if not match:
            # Not a stage-scoped request — let it through.
            return await call_next(request)

        stage_id = match.group("stage")

        try:
            agent = load_stage(stage_id)
        except ModuleNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"error": f"stage-{stage_id} not found"},
            )
        except FileNotFoundError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"stage-{stage_id} found but spec missing",
                    "detail": str(e),
                },
            )
        except Exception as e:
            # Malformed spec, import error inside the stage module, etc.
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"stage-{stage_id} failed to load",
                    "detail": f"{type(e).__name__}: {e}",
                },
            )
 
        request.state.agent = agent
        request.state.stage_id = stage_id

        # Strip the /stage-XX segment so the shared route matches, keeping the
        # router prefix that came before it.
        prefix = match.group("prefix")
        remainder = match.group("rest") or "/"
        request.scope["path"] = f"{prefix}/agents{remainder}"
        print("Stage selector request scope path", request.scope["path"])

        response = await call_next(request)
        # Debug convenience: which stage handled this request?
        response.headers["X-Agent-Stage"] = stage_id
        return response