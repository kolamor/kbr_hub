from fastapi import Depends

from src.users.users_f import fastapi_users_local, auth_backend
from .. import app_ext
from ..db import User
from ..schemas import UserRead, UserCreate, UserUpdate

current_active_user = fastapi_users_local.current_user(active=True)


app = app_ext.app


app.include_router(
    fastapi_users_local.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users_local.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_local.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_local.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_local.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

