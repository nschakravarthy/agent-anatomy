from pydantic import BaseModel, EmailStr

from api.user.models import UserRole

class UserCreate(BaseModel):
    """Registration and login payload. Self-service signups are always given the
    `user` role — there is deliberately no role field to set."""

    email: EmailStr
    password: str

class UserResponse(BaseModel):
    # Deliberately no email: the auth responses carry only what the client needs
    # to hold a session and pick a UI, never account identifiers.
    user_id: str
    role: UserRole
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # in seconds

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
