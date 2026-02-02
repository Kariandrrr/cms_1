from fastapi import APIRouter as auth_router, Depends, Form, HTTPException, status

from ...core.schemas.user import UserSchema, Token
from . import utils_jwt as auth_utils_jwt


router = auth_router(prefix="/jwt", tags=["JWT"])
john = UserSchema(
    username="john", password=auth_utils_jwt.hash_password("qwerty"), role="user"
)
sam = UserSchema(
    username="sam", password=auth_utils_jwt.hash_password("qwerty"), role="user"
)
users_db: dict[str, UserSchema] = {john.username: john, sam.username: sam}


def validate_auth_user(username: str = Form(), password: str = Form()):
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="incorrect username or password",
    )
    if not (user := users_db.get(username)):
        raise unauthed_exp

    if auth_utils_jwt.validate_password(
        password=password, hashed_password=user.password
    ):
        return user
    raise unauthed_exp


@router.post("/login", response_model=Token)
def auth_user_issue_jwt(user: UserSchema = Depends(validate_auth_user)):
    jwt_payload = {
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }
    token = auth_utils_jwt.encode_jwt(jwt_payload)
    return Token(access_token=token, token_type="Bearer")
