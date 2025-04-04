import logging
import uuid
import jwt

from datetime import UTC, datetime, timedelta
from typing import Optional, Union, List, Dict

from open_webui.models.users import Users

from open_webui.constants import ERROR_MESSAGES
from open_webui.env import WEBUI_SECRET_KEY
from open_webui.utils.misc import parse_duration

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

logging.getLogger("passlib").setLevel(logging.ERROR)


SESSION_SECRET = WEBUI_SECRET_KEY
ALGORITHM = "HS256"

##############
# Auth Utils
##############

bearer_security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return (
        pwd_context.verify(plain_password, hashed_password) if hashed_password else None
    )


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    payload = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
        payload.update({"exp": expire})

    encoded_jwt = jwt.encode(payload, SESSION_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    return jwt.decode(token, SESSION_SECRET, algorithms=[ALGORITHM])


def extract_token_from_auth_header(auth_header: str):
    return auth_header[len("Bearer ") :]


def create_api_key():
    key = str(uuid.uuid4()).replace("-", "")
    return f"sk-{key}"


def get_http_authorization_cred(auth_header: str):
    try:
        scheme, credentials = auth_header.split(" ")
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
    except Exception:
        raise ValueError(ERROR_MESSAGES.INVALID_TOKEN)


def refresh_jwt(request: Request, response: Response):
    """
    Checks the refresh token from the request cookie. If it's not expired, get data
    and set a fresh jwt on the cookie and return the data.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(status_code=403, detail=ERROR_MESSAGES.UNAUTHORIZED)
    try:
        data = jwt.decode(refresh_token, SESSION_SECRET, algorithms=[ALGORITHM])
    except Exception as e:
        # an invalid or expired refresh cookie leaves us no
        # choice by to send 401.
        raise e

    claim = {"id": data["id"]}
    expires_delta = parse_duration(request.app.state.config.JWT_EXPIRES_IN)
    new_token = create_token(claim, expires_delta)
    response.set_cookie(key="token", value=new_token, httponly=True)
    return data


def get_current_user(
    request: Request,
    response: Response,
    auth_token: HTTPAuthorizationCredentials = Depends(bearer_security),
):
    # handle potential API token in authorization header:
    if auth_token is not None:
        api_key = auth_token.credentials

        # ignore any bearer tokens that don't start with 'sk-'
        if api_key is not None and api_key.startswith("sk-"):
            if not request.state.enable_api_key:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.API_KEY_NOT_ALLOWED
                )

            if request.app.state.config.ENABLE_API_KEY_ENDPOINT_RESTRICTIONS:
                allowed_paths = [
                    path.strip()
                    for path in str(
                        request.app.state.config.API_KEY_ALLOWED_PATHS
                    ).split(",")
                ]

                if request.url.path not in allowed_paths:
                    raise HTTPException(
                        status.HTTP_403_FORBIDDEN,
                        detail=ERROR_MESSAGES.API_KEY_NOT_ALLOWED,
                    )

            return get_current_user_by_api_key(api_key)

    # auth using jwt token in cookie
    token = request.cookies.get("token")

    if token is None:
        raise HTTPException(status_code=403, detail="Not authenticated")

    try:
        data = jwt.decode(token, SESSION_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        try:
            data = refresh_jwt(request, response)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except Exception:
        # Only generate a new token when the old one is valid, but expired.
        # Any other failure should not be allowed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if data is not None and "id" in data:
        user = Users.get_user_by_id(data["id"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.INVALID_TOKEN,
            )
        else:
            Users.update_user_last_active_by_id(user.id)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )


def get_current_user_by_api_key(api_key: str):
    user = Users.get_user_by_api_key(api_key)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.INVALID_TOKEN,
        )
    else:
        Users.update_user_last_active_by_id(user.id)

    return user


def get_verified_user(user=Depends(get_current_user)):
    if user.role not in {"user", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    return user


def get_admin_user(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    return user
