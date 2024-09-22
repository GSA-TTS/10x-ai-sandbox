import logging

from fastapi import Request  # , UploadFile, File
from fastapi import Depends, HTTPException, status

import requests

from fastapi import APIRouter
from pydantic import BaseModel
import re
import uuid
import jwt

# import csv
import sys
import os


from apps.webui.models.auths import (
    SigninForm,
    SigninFormOauth,
    SignupForm,
    AddUserForm,
    UpdateProfileForm,
    UpdatePasswordForm,
    UserResponse,
    SigninResponse,
    Auths,
    ApiKey,
)
from apps.webui.models.users import Users

from utils.utils import (
    get_password_hash,
    get_current_user,
    get_admin_user,
    create_token,
    create_api_key,
)
from utils.misc import parse_duration, validate_email_format
from utils.webhook import post_webhook
from constants import ERROR_MESSAGES, WEBHOOK_MESSAGES
from config import (
    WEBUI_AUTH,
    WEBUI_AUTH_TRUSTED_EMAIL_HEADER,
    WEBUI_AUTH_TRUSTED_NAME_HEADER,
    OAUTH2_PROVIDERS,
)

router = APIRouter()

logging.basicConfig(stream=sys.stdout, level="INFO")
log = logging.getLogger(__name__)
# log.setLevel(SRC_LOG_LEVELS["MAIN"])

############################
# GetSessionUser
############################


@router.get("/", response_model=UserResponse)
async def get_session_user(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "profile_image_url": user.profile_image_url,
    }


############################
# Update Profile
############################


@router.post("/update/profile", response_model=UserResponse)
async def update_profile(
    form_data: UpdateProfileForm, session_user=Depends(get_current_user)
):
    if session_user:
        user = Users.update_user_by_id(
            session_user.id,
            {"profile_image_url": form_data.profile_image_url, "name": form_data.name},
        )
        if user:
            return user
        else:
            raise HTTPException(400, detail=ERROR_MESSAGES.DEFAULT())
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# Update Password
############################


@router.post("/update/password", response_model=bool)
async def update_password(
    form_data: UpdatePasswordForm, session_user=Depends(get_current_user)
):
    if WEBUI_AUTH_TRUSTED_EMAIL_HEADER:
        raise HTTPException(400, detail=ERROR_MESSAGES.ACTION_PROHIBITED)
    if session_user:
        user = Auths.authenticate_user(session_user.email, form_data.password)

        if user:
            hashed = get_password_hash(form_data.new_password)
            return Auths.update_user_password_by_id(user.id, hashed)
        else:
            raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_PASSWORD)
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# SignIn
############################


@router.post(
    "/signin_oauth/{provider}", response_model=SigninResponse, name="oauth-signin"
)
async def signin_oauth(request: Request, provider: str, form_data: SigninFormOauth):

    log.error(f"header: {request.headers}")
    log.error(f"provider: {provider}")
    log.error(f"form_data: {form_data}")
    log.error(f"session: {request.session}")
    log.error(f"session: {request.session.get('oauth2_state')}")
    log.error(f"form_data.state: {form_data.state}")
    log.error(f"form_data.code: {form_data.code}")
    log.error(f"form_data.provider: {form_data.provider}")

    name = None

    provider_data = OAUTH2_PROVIDERS.get(provider)

    if provider_data is None:
        raise HTTPException(status_code=404)

    if form_data.state != request.session.get("oauth2_state"):
        # Handle state mismatch error
        raise HTTPException(
            status_code=401, detail=f"oauth2_state does not match expectation"
        )

    if not form_data.code:
        # Handle missing code error
        raise HTTPException(status_code=401, detail=f"code is missing")

    # TODO: use better params for environement detection
    redirect_uri = os.environ.get(
        "CODESPACE_URL", request.url_for("oauth2_callback", provider=provider)
    )

    # Exchange the authorization code for an access token
    token_response = requests.post(
        provider_data["token_url"],
        data={
            "client_id": provider_data["client_id"],
            "client_secret": provider_data["client_secret"],
            "code": form_data.code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
        headers={"Accept": "application/json"},
    )

    if token_response.status_code != 200:
        # Handle token exchange error
        raise HTTPException(
            status_code=401, detail=f"token_response: {token_response.json()}"
        )

    oauth2_token = token_response.json().get("access_token")

    if not oauth2_token:
        # Handle missing access token error
        log.error(
            f"oauth2_token is missing or invalid from response: {token_response.json()}"
        )
        raise HTTPException(
            status_code=401,
            detail=f"oauth2_token is missing or invalid from response: {token_response.json()}",
        )

    # Cloud.gov encodes the user's email address into the token itself, so we need to check for validity
    if provider_data["userinfo"]["url"] == "access_token":
        decoded_data = jwt.decode(
            oauth2_token,
            options={"verify_signature": False},
        )  # TODO: replace with sig verification
        # response = httpx.get(url="https://uaa.fr.cloud.gov/token_keys") # get public key from cloud's json web key url
        # jwks = response.json() # should be a dict like {'keys': [{key_one}, {key_two}]}
        # key = jwks['keys'][0] # should be the first key (dict) in the keys array
        # algo = key['alg'] # You can view cloud's json web key structure at the url above, it'll open in a browser
        # decoded_data = jwt.decode(token=oauth2_token, key=key, algorithms=[algo]) # note that algorithms expects an []
        email = decoded_data.get("email")
        all_emails = [email]
    else:
        try:
            response = requests.get(
                provider_data["userinfo"]["url"],
                headers={
                    "Authorization": "Bearer " + oauth2_token,
                    "Accept": "application/json",
                },
                timeout=4,
            )
            if response.status_code != 200:
                err = (
                    f"OAUTH userinfo response request status not 200."
                    + f"Status: {response.status_code}, Response: {response.json()}"
                )
                log.error(err)
                raise HTTPException(status_code=401, detail=err)
            email = provider_data["userinfo"]["email"](response.json())
            all_emails = provider_data["userinfo"]["all_emails"](response.json())
        except Exception as e:
            # Handle email retrieval error
            log.error(f"signin_oauth error: {e}")
            log.error(f"response: {response}")
            err = (
                f"Error: {e} for {provider} provider with token {oauth2_token}"
                + f" and code {form_data.code}"
            )
            log.error(err)
            raise HTTPException(status_code=401, detail=err)

    user_email_domains = []
    user_has_permitted_domain = False

    for this_email in all_emails:
        domain = this_email.split("@")[1]
        user_email_domains.append(domain)
        if domain in ["gsa.gov"]:
            email = this_email
            user_has_permitted_domain = True
            break

    if not user_has_permitted_domain or not email:
        # Handle unauthorized domain error
        raise HTTPException(
            status_code=401, detail=f"Missing email or unauthorized email domain"
        )

    log.error(f"email is: {email}")

    if not name:
        name = email

    if not Users.get_user_by_email(email.lower()):
        await signup(
            request,
            SignupForm(email=email, password=str(uuid.uuid4()), name=name),
        )

    user = Auths.authenticate_user_by_trusted_header(email)
    log.error(f"user is: {user}")

    if user:
        token = create_token(
            data={"id": user.id},
            expires_delta=parse_duration(request.app.state.config.JWT_EXPIRES_IN),
        )

        log.error(f"finally user is: {user}")

        return {
            "token": token,
            "token_type": "Bearer",
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_image_url": user.profile_image_url,
        }
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_CRED)


@router.post("/signin", response_model=SigninResponse, name="auths-signin")
async def signin(request: Request, form_data: SigninForm):

    log.error(f"header: {request.headers}")

    if request.client.host in ["127.0.0.1", "::1"]:
        log.error("Request is coming from the local server")

    if "X-Forwarded-Email" in request.headers:
        trusted_email = request.headers["X-Forwarded-Email"].lower()
        trusted_name = trusted_email
        if WEBUI_AUTH_TRUSTED_NAME_HEADER:
            trusted_name = request.headers.get(
                WEBUI_AUTH_TRUSTED_NAME_HEADER, trusted_email
            )
        if not Users.get_user_by_email(trusted_email.lower()):
            await signup(
                request,
                SignupForm(
                    email=trusted_email, password=str(uuid.uuid4()), name=trusted_name
                ),
            )
        user = Auths.authenticate_user_by_trusted_header(trusted_email)
        log.error(f"user is: {user}")
    elif WEBUI_AUTH_TRUSTED_EMAIL_HEADER:
        if WEBUI_AUTH_TRUSTED_EMAIL_HEADER not in request.headers:
            raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_TRUSTED_HEADER)

        trusted_email = request.headers[WEBUI_AUTH_TRUSTED_EMAIL_HEADER].lower()
        trusted_name = trusted_email
        if WEBUI_AUTH_TRUSTED_NAME_HEADER:
            trusted_name = request.headers.get(
                WEBUI_AUTH_TRUSTED_NAME_HEADER, trusted_email
            )
        if not Users.get_user_by_email(trusted_email.lower()):
            await signup(
                request,
                SignupForm(
                    email=trusted_email, password=str(uuid.uuid4()), name=trusted_name
                ),
            )
        user = Auths.authenticate_user_by_trusted_header(trusted_email)
        print(f"user is: {user}")
    elif WEBUI_AUTH is False:
        admin_email = "admin@localhost"
        admin_password = "admin"

        if Users.get_user_by_email(admin_email.lower()):
            user = Auths.authenticate_user(admin_email.lower(), admin_password)
        else:
            if Users.get_num_users() != 0:
                raise HTTPException(400, detail=ERROR_MESSAGES.EXISTING_USERS)

            await signup(
                request,
                SignupForm(email=admin_email, password=admin_password, name="User"),
            )

            user = Auths.authenticate_user(admin_email.lower(), admin_password)
    else:
        user = Auths.authenticate_user(form_data.email.lower(), form_data.password)

    if user:
        token = create_token(
            data={"id": user.id},
            expires_delta=parse_duration(request.app.state.config.JWT_EXPIRES_IN),
        )

        log.error(f"finally user is: {user}")

        return {
            "token": token,
            "token_type": "Bearer",
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_image_url": user.profile_image_url,
        }
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# SignUp
############################


@router.post("/signup", response_model=SigninResponse)
async def signup(request: Request, form_data: SignupForm):
    if not request.app.state.config.ENABLE_SIGNUP and WEBUI_AUTH:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )

    if not validate_email_format(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT
        )

    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_TAKEN)

    dev_admin_emails_str = os.getenv("DEV_ADMIN_EMAILS", " , ")
    dev_user_emails_str = os.getenv("DEV_USER_EMAILS", " , ")
    log.error(f"dev_admin_emails_str: {dev_admin_emails_str}")
    log.error(f"dev_user_emails_str: {dev_user_emails_str}")
    dev_admin_emails = dev_admin_emails_str.split(",") if dev_admin_emails_str else []
    dev_user_emails = dev_user_emails_str.split(",") if dev_user_emails_str else []
    log.error(f"dev_admin_emails: {dev_admin_emails}")
    log.error(f"dev_user_emails: {dev_user_emails}")
    try:

        if form_data.email.lower() in dev_admin_emails:
            role = "admin"
        elif form_data.email.lower() in dev_user_emails:
            role = "user"
        else:
            role = request.app.state.config.DEFAULT_USER_ROLE

        name = form_data.name

        if form_data.email.lower() and "." in form_data.email.lower():
            names = form_data.email.lower().split("@")
            if names:
                names = names[0].split(".")
                if names and len(names) > 1:
                    first_name = names[0]
                    last_name = names[1]
                    if first_name and last_name:
                        name = first_name.capitalize() + " " + last_name.capitalize()

        log.error(
            f"New user: {form_data.email.lower()} has role: {role} and name {name}"
        )

        hashed = get_password_hash(form_data.password)
        user = Auths.insert_new_auth(
            form_data.email.lower(),
            hashed,
            name,
            form_data.profile_image_url,
            role,
        )

        if user:
            token = create_token(
                data={"id": user.id},
                expires_delta=parse_duration(request.app.state.config.JWT_EXPIRES_IN),
            )
            # response.set_cookie(key='token', value=token, httponly=True)

            if request.app.state.config.WEBHOOK_URL:
                post_webhook(
                    request.app.state.config.WEBHOOK_URL,
                    WEBHOOK_MESSAGES.USER_SIGNUP(user.name),
                    {
                        "action": "signup",
                        "message": WEBHOOK_MESSAGES.USER_SIGNUP(user.name),
                        "user": user.model_dump_json(exclude_none=True),
                    },
                )

            return {
                "token": token,
                "token_type": "Bearer",
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "profile_image_url": user.profile_image_url,
            }
        else:
            raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_USER_ERROR)
    except Exception as err:
        raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT(err))


############################
# AddUser
############################


@router.post("/add", response_model=SigninResponse)
async def add_user(form_data: AddUserForm, user=Depends(get_admin_user)):

    if not validate_email_format(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT
        )

    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_TAKEN)

    try:

        print(form_data)
        hashed = get_password_hash(form_data.password)
        user = Auths.insert_new_auth(
            form_data.email.lower(),
            hashed,
            form_data.name,
            form_data.profile_image_url,
            form_data.role,
        )

        if user:
            token = create_token(data={"id": user.id})
            return {
                "token": token,
                "token_type": "Bearer",
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "profile_image_url": user.profile_image_url,
            }
        else:
            raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_USER_ERROR)
    except Exception as err:
        raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT(err))


############################
# GetAdminDetails
############################


@router.get("/admin/details")
async def get_admin_details(request: Request, user=Depends(get_current_user)):
    if request.app.state.config.SHOW_ADMIN_DETAILS:
        admin_email = request.app.state.config.ADMIN_EMAIL
        admin_name = None

        print(admin_email, admin_name)

        if admin_email:
            admin = Users.get_user_by_email(admin_email)
            if admin:
                admin_name = admin.name
        else:
            admin = Users.get_first_user()
            if admin:
                admin_email = admin.email
                admin_name = admin.name

        return {
            "name": admin_name,
            "email": admin_email,
        }
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.ACTION_PROHIBITED)


############################
# ToggleSignUp
############################


@router.get("/admin/config")
async def get_admin_config(request: Request, user=Depends(get_admin_user)):
    return {
        "SHOW_ADMIN_DETAILS": request.app.state.config.SHOW_ADMIN_DETAILS,
        "ENABLE_SIGNUP": request.app.state.config.ENABLE_SIGNUP,
        "DEFAULT_USER_ROLE": request.app.state.config.DEFAULT_USER_ROLE,
        "JWT_EXPIRES_IN": request.app.state.config.JWT_EXPIRES_IN,
        "ENABLE_COMMUNITY_SHARING": request.app.state.config.ENABLE_COMMUNITY_SHARING,
    }


class AdminConfig(BaseModel):
    SHOW_ADMIN_DETAILS: bool
    ENABLE_SIGNUP: bool
    DEFAULT_USER_ROLE: str
    JWT_EXPIRES_IN: str
    ENABLE_COMMUNITY_SHARING: bool


@router.post("/admin/config")
async def update_admin_config(
    request: Request, form_data: AdminConfig, user=Depends(get_admin_user)
):
    request.app.state.config.SHOW_ADMIN_DETAILS = form_data.SHOW_ADMIN_DETAILS
    request.app.state.config.ENABLE_SIGNUP = form_data.ENABLE_SIGNUP

    if form_data.DEFAULT_USER_ROLE in ["pending", "user", "admin"]:
        request.app.state.config.DEFAULT_USER_ROLE = form_data.DEFAULT_USER_ROLE

    pattern = r"^(-1|0|(-?\d+(\.\d+)?)(ms|s|m|h|d|w))$"

    # Check if the input string matches the pattern
    if re.match(pattern, form_data.JWT_EXPIRES_IN):
        request.app.state.config.JWT_EXPIRES_IN = form_data.JWT_EXPIRES_IN

    request.app.state.config.ENABLE_COMMUNITY_SHARING = (
        form_data.ENABLE_COMMUNITY_SHARING
    )

    return {
        "SHOW_ADMIN_DETAILS": request.app.state.config.SHOW_ADMIN_DETAILS,
        "ENABLE_SIGNUP": request.app.state.config.ENABLE_SIGNUP,
        "DEFAULT_USER_ROLE": request.app.state.config.DEFAULT_USER_ROLE,
        "JWT_EXPIRES_IN": request.app.state.config.JWT_EXPIRES_IN,
        "ENABLE_COMMUNITY_SHARING": request.app.state.config.ENABLE_COMMUNITY_SHARING,
    }


############################
# API Key
############################


# create api key
@router.post("/api_key", response_model=ApiKey)
async def create_api_key_(user=Depends(get_current_user)):
    api_key = create_api_key()
    success = Users.update_user_api_key_by_id(user.id, api_key)
    if success:
        return {
            "api_key": api_key,
        }
    else:
        raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_API_KEY_ERROR)


# delete api key
@router.delete("/api_key", response_model=bool)
async def delete_api_key(user=Depends(get_current_user)):
    success = Users.update_user_api_key_by_id(user.id, None)
    return success


# get api key
@router.get("/api_key", response_model=ApiKey)
async def get_api_key(user=Depends(get_current_user)):
    api_key = Users.get_user_api_key_by_id(user.id)
    if api_key:
        return {
            "api_key": api_key,
        }
    else:
        raise HTTPException(404, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND)
