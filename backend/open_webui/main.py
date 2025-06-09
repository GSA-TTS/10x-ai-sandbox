import asyncio
import inspect
import json
import structlog
import mimetypes
import os
import shutil
import sys
import time
import random
import threading

from contextlib import asynccontextmanager
from urllib.parse import urlencode, parse_qs, urlparse
from pydantic import BaseModel
from sqlalchemy import text
import redis
import jwt

from typing import Optional
from aiocache import cached
import aiohttp
import requests


from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
    applications,
    BackgroundTasks,
)

from fastapi.openapi.docs import get_swagger_ui_html

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response, StreamingResponse

from open_webui.middleware.logs import StructlogContextMiddleware


from open_webui.socket.main import (
    app as socket_app,
    periodic_usage_pool_cleanup,
)
from open_webui.routers import (
    audio,
    images,
    ollama,
    openai,
    retrieval,
    pipelines,
    tasks,
    auths,
    channels,
    chats,
    folders,
    configs,
    groups,
    files,
    functions,
    memories,
    models,
    knowledge,
    prompts,
    evaluations,
    tools,
    users,
    utils,
)

from open_webui.routers.retrieval import (
    get_embedding_function,
    get_ef,
    get_rf,
)

from open_webui.internal.db import Session

from open_webui.models.functions import Functions
from open_webui.models.models import Models
from open_webui.models.users import UserModel, Users

from open_webui.config import (
    # WebUI
    WEBUI_AUTH,
    WEBUI_NAME,
    # Misc
    ENV,
    CACHE_DIR,
    STATIC_DIR,
    FRONTEND_BUILD_DIR,
    AppConfig,
    reset_config,
    config,
)
from open_webui.env import (
    CHANGELOG,
    GLOBAL_LOG_LEVEL,
    SAFE_MODE,
    SRC_LOG_LEVELS,
    VERSION,
    WEBUI_BUILD_HASH,
    WEBUI_SECRET_KEY,
    WEBUI_SESSION_COOKIE_SAME_SITE,
    WEBUI_SESSION_COOKIE_SECURE,
    WEBUI_AUTH_TRUSTED_EMAIL_HEADER,
    WEBUI_AUTH_TRUSTED_NAME_HEADER,
    ENABLE_WEBSOCKET_SUPPORT,
    BYPASS_MODEL_ACCESS_CONTROL,
    RESET_CONFIG_ON_START,
    OFFLINE_MODE,
    WEBSOCKET_REDIS_URL,
)


from open_webui.utils.models import (
    get_all_models,
    get_all_base_models,
    check_model_access,
)
from open_webui.utils.chat import (
    generate_chat_completion as chat_completion_handler,
    chat_completed as chat_completed_handler,
    chat_action as chat_action_handler,
)
from open_webui.utils.middleware import process_chat_payload, process_chat_response
from open_webui.utils.access_control import has_access

from open_webui.utils.auth import (
    decode_token,
    get_admin_user,
    get_verified_user,
    refresh_jwt,
    get_current_user,
)
from open_webui.utils.oauth import oauth_manager
from open_webui.utils.security_headers import SecurityHeadersMiddleware

from open_webui.tasks import stop_task, task_channel_listener

from open_webui.utils.logs import setup_logging


setup_logging(json_logs=False, log_level=GLOBAL_LOG_LEVEL)

log = structlog.get_logger(__name__)

if SAFE_MODE:
    print("SAFE MODE ENABLED")
    Functions.deactivate_all_functions()


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


print(
    rf"""
  ___                    __        __   _     _   _ ___
 / _ \ _ __   ___ _ __   \ \      / /__| |__ | | | |_ _|
| | | | '_ \ / _ \ '_ \   \ \ /\ / / _ \ '_ \| | | || |
| |_| | |_) |  __/ | | |   \ V  V /  __/ |_) | |_| || |
 \___/| .__/ \___|_| |_|    \_/\_/ \___|_.__/ \___/|___|
      |_|


v{VERSION} - building the best open-source AI user interface.
{f"Commit: {WEBUI_BUILD_HASH}" if WEBUI_BUILD_HASH != "dev-build" else ""}
https://github.com/open-webui/open-webui
"""
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if RESET_CONFIG_ON_START:
        reset_config()

    threading.Thread(target=task_channel_listener, daemon=True).start()
    asyncio.create_task(periodic_usage_pool_cleanup())
    yield


app = FastAPI(
    docs_url="/docs" if ENV == "dev" else None,
    openapi_url="/openapi.json" if ENV == "dev" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.config = AppConfig()


########################################
#
# OLLAMA
#
########################################


app.state.config.ENABLE_OLLAMA_API = config.ENABLE_OLLAMA_API
app.state.config.OLLAMA_BASE_URLS = config.OLLAMA_BASE_URLS
app.state.config.OLLAMA_API_CONFIGS = config.OLLAMA_API_CONFIGS

app.state.OLLAMA_MODELS = {}

########################################
#
# OPENAI
#
########################################

app.state.config.ENABLE_OPENAI_API = config.ENABLE_OPENAI_API
app.state.config.OPENAI_API_BASE_URLS = config.OPENAI_API_BASE_URLS
app.state.config.OPENAI_API_KEYS = config.OPENAI_API_KEYS
app.state.config.OPENAI_API_CONFIGS = config.OPENAI_API_CONFIGS

app.state.OPENAI_MODELS = {}

########################################
#
# WEBUI
#
########################################

app.state.config.WEBUI_URL = config.WEBUI_URL
app.state.config.ENABLE_SIGNUP = config.ENABLE_SIGNUP
app.state.config.ENABLE_LOGIN_FORM = config.ENABLE_LOGIN_FORM

app.state.config.ENABLE_API_KEY = config.ENABLE_API_KEY
app.state.config.ENABLE_API_KEY_ENDPOINT_RESTRICTIONS = (
    config.ENABLE_API_KEY_ENDPOINT_RESTRICTIONS
)
app.state.config.API_KEY_ALLOWED_ENDPOINTS = config.API_KEY_ALLOWED_ENDPOINTS

app.state.config.JWT_EXPIRES_IN = config.JWT_EXPIRES_IN
app.state.config.JWT_REFRESH_EXPIRES_IN = config.JWT_REFRESH_EXPIRES_IN


app.state.config.SHOW_ADMIN_DETAILS = config.SHOW_ADMIN_DETAILS
app.state.config.ADMIN_EMAIL = config.ADMIN_EMAIL


app.state.config.DEFAULT_MODELS = config.DEFAULT_MODELS
app.state.config.DEFAULT_PROMPT_SUGGESTIONS = config.DEFAULT_PROMPT_SUGGESTIONS
app.state.config.DEFAULT_USER_ROLE = config.DEFAULT_USER_ROLE

app.state.config.USER_PERMISSIONS = config.USER_PERMISSIONS
app.state.config.WEBHOOK_URL = config.WEBHOOK_URL
app.state.config.WEBUI_BANNERS = config.WEBUI_BANNERS
app.state.config.MODEL_ORDER_LIST = config.MODEL_ORDER_LIST


app.state.config.ENABLE_CHANNELS = config.ENABLE_CHANNELS
app.state.config.ENABLE_COMMUNITY_SHARING = config.ENABLE_COMMUNITY_SHARING
app.state.config.ENABLE_MESSAGE_RATING = config.ENABLE_MESSAGE_RATING

app.state.config.ENABLE_EVALUATION_ARENA_MODELS = config.ENABLE_EVALUATION_ARENA_MODELS
app.state.config.EVALUATION_ARENA_MODELS = config.EVALUATION_ARENA_MODELS

app.state.config.OAUTH_USERNAME_CLAIM = config.OAUTH_USERNAME_CLAIM
app.state.config.OAUTH_PICTURE_CLAIM = config.OAUTH_PICTURE_CLAIM
app.state.config.OAUTH_EMAIL_CLAIM = config.OAUTH_EMAIL_CLAIM

app.state.config.ENABLE_OAUTH_ROLE_MANAGEMENT = config.ENABLE_OAUTH_ROLE_MANAGEMENT
app.state.config.OAUTH_ROLES_CLAIM = config.OAUTH_ROLES_CLAIM
app.state.config.OAUTH_ALLOWED_ROLES = config.OAUTH_ALLOWED_ROLES
app.state.config.OAUTH_ADMIN_ROLES = config.OAUTH_ADMIN_ROLES

app.state.config.ENABLE_LDAP = config.ENABLE_LDAP
app.state.config.LDAP_SERVER_LABEL = config.LDAP_SERVER_LABEL
app.state.config.LDAP_SERVER_HOST = config.LDAP_SERVER_HOST
app.state.config.LDAP_SERVER_PORT = config.LDAP_SERVER_PORT
app.state.config.LDAP_ATTRIBUTE_FOR_USERNAME = config.LDAP_ATTRIBUTE_FOR_USERNAME
app.state.config.LDAP_APP_DN = config.LDAP_APP_DN
app.state.config.LDAP_APP_PASSWORD = config.LDAP_APP_PASSWORD
app.state.config.LDAP_SEARCH_BASE = config.LDAP_SEARCH_BASE
app.state.config.LDAP_SEARCH_FILTERS = config.LDAP_SEARCH_FILTERS
app.state.config.LDAP_USE_TLS = config.LDAP_USE_TLS
app.state.config.LDAP_CA_CERT_FILE = config.LDAP_CA_CERT_FILE
app.state.config.LDAP_CIPHERS = config.LDAP_CIPHERS


app.state.AUTH_TRUSTED_EMAIL_HEADER = WEBUI_AUTH_TRUSTED_EMAIL_HEADER
app.state.AUTH_TRUSTED_NAME_HEADER = WEBUI_AUTH_TRUSTED_NAME_HEADER

app.state.TOOLS = {}
app.state.FUNCTIONS = {}


########################################
#
# RETRIEVAL
#
########################################


app.state.config.RAG_TOP_K = config.RAG_TOP_K
app.state.config.RAG_RELEVANCE_THRESHOLD = config.RAG_RELEVANCE_THRESHOLD
app.state.config.RAG_FILE_MAX_SIZE = config.RAG_FILE_MAX_SIZE
app.state.config.RAG_FILE_MAX_COUNT = config.RAG_FILE_MAX_COUNT

app.state.config.ENABLE_RAG_HYBRID_SEARCH = config.ENABLE_RAG_HYBRID_SEARCH
app.state.config.ENABLE_RAG_WEB_LOADER_SSL_VERIFICATION = (
    config.ENABLE_RAG_WEB_LOADER_SSL_VERIFICATION
)

app.state.config.CONTENT_EXTRACTION_ENGINE = config.CONTENT_EXTRACTION_ENGINE
app.state.config.TIKA_SERVER_URL = config.TIKA_SERVER_URL

app.state.config.TEXT_SPLITTER = config.RAG_TEXT_SPLITTER
app.state.config.TIKTOKEN_ENCODING_NAME = config.TIKTOKEN_ENCODING_NAME

app.state.config.CHUNK_SIZE = config.CHUNK_SIZE
app.state.config.CHUNK_OVERLAP = config.CHUNK_OVERLAP

app.state.config.RAG_EMBEDDING_ENGINE = config.RAG_EMBEDDING_ENGINE
app.state.config.RAG_EMBEDDING_MODEL = config.RAG_EMBEDDING_MODEL
app.state.config.RAG_EMBEDDING_BATCH_SIZE = config.RAG_EMBEDDING_BATCH_SIZE
app.state.config.RAG_RERANKING_MODEL = config.RAG_RERANKING_MODEL
app.state.config.RAG_TEMPLATE = config.RAG_TEMPLATE

app.state.config.RAG_OPENAI_API_BASE_URL = config.RAG_OPENAI_API_BASE_URL
app.state.config.RAG_OPENAI_API_KEY = config.RAG_OPENAI_API_KEY

app.state.config.RAG_OLLAMA_BASE_URL = config.RAG_OLLAMA_BASE_URL
app.state.config.RAG_OLLAMA_API_KEY = config.RAG_OLLAMA_API_KEY

app.state.config.PDF_EXTRACT_IMAGES = config.PDF_EXTRACT_IMAGES

app.state.config.YOUTUBE_LOADER_LANGUAGE = config.YOUTUBE_LOADER_LANGUAGE
app.state.config.YOUTUBE_LOADER_PROXY_URL = config.YOUTUBE_LOADER_PROXY_URL


app.state.config.ENABLE_RAG_WEB_SEARCH = config.ENABLE_RAG_WEB_SEARCH
app.state.config.RAG_WEB_SEARCH_ENGINE = config.RAG_WEB_SEARCH_ENGINE
app.state.config.RAG_WEB_SEARCH_DOMAIN_FILTER_LIST = (
    config.RAG_WEB_SEARCH_DOMAIN_FILTER_LIST
)

app.state.config.ENABLE_GOOGLE_DRIVE_INTEGRATION = (
    config.ENABLE_GOOGLE_DRIVE_INTEGRATION
)
app.state.config.SEARXNG_QUERY_URL = config.SEARXNG_QUERY_URL
app.state.config.GOOGLE_PSE_API_KEY = config.GOOGLE_PSE_API_KEY
app.state.config.GOOGLE_PSE_ENGINE_ID = config.GOOGLE_PSE_ENGINE_ID
app.state.config.BRAVE_SEARCH_API_KEY = config.BRAVE_SEARCH_API_KEY
app.state.config.KAGI_SEARCH_API_KEY = config.KAGI_SEARCH_API_KEY
app.state.config.MOJEEK_SEARCH_API_KEY = config.MOJEEK_SEARCH_API_KEY
app.state.config.SERPSTACK_API_KEY = config.SERPSTACK_API_KEY
app.state.config.SERPSTACK_HTTPS = config.SERPSTACK_HTTPS
app.state.config.SERPER_API_KEY = config.SERPER_API_KEY
app.state.config.SERPLY_API_KEY = config.SERPLY_API_KEY
app.state.config.TAVILY_API_KEY = config.TAVILY_API_KEY
app.state.config.SEARCHAPI_API_KEY = config.SEARCHAPI_API_KEY
app.state.config.SEARCHAPI_ENGINE = config.SEARCHAPI_ENGINE
app.state.config.JINA_API_KEY = config.JINA_API_KEY
app.state.config.BING_SEARCH_V7_ENDPOINT = config.BING_SEARCH_V7_ENDPOINT
app.state.config.BING_SEARCH_V7_SUBSCRIPTION_KEY = (
    config.BING_SEARCH_V7_SUBSCRIPTION_KEY
)

app.state.config.RAG_WEB_SEARCH_RESULT_COUNT = config.RAG_WEB_SEARCH_RESULT_COUNT
app.state.config.RAG_WEB_SEARCH_CONCURRENT_REQUESTS = (
    config.RAG_WEB_SEARCH_CONCURRENT_REQUESTS
)

app.state.EMBEDDING_FUNCTION = None
app.state.ef = None
app.state.rf = None

app.state.YOUTUBE_LOADER_TRANSLATION = None


try:
    app.state.ef = get_ef(
        app.state.config.RAG_EMBEDDING_ENGINE,
        app.state.config.RAG_EMBEDDING_MODEL,
        config.RAG_EMBEDDING_MODEL_AUTO_UPDATE,
    )

    app.state.rf = get_rf(
        app.state.config.RAG_RERANKING_MODEL,
        config.RAG_RERANKING_MODEL_AUTO_UPDATE,
    )
except Exception as e:
    log.error(f"Error updating models: {e}")
    pass


app.state.EMBEDDING_FUNCTION = get_embedding_function(
    app.state.config.RAG_EMBEDDING_ENGINE,
    app.state.config.RAG_EMBEDDING_MODEL,
    app.state.ef,
    (
        app.state.config.RAG_OPENAI_API_BASE_URL
        if app.state.config.RAG_EMBEDDING_ENGINE == "openai"
        else app.state.config.RAG_OLLAMA_BASE_URL
    ),
    (
        app.state.config.RAG_OPENAI_API_KEY
        if app.state.config.RAG_EMBEDDING_ENGINE == "openai"
        else app.state.config.RAG_OLLAMA_API_KEY
    ),
    app.state.config.RAG_EMBEDDING_BATCH_SIZE,
)


########################################
#
# IMAGES
#
########################################

app.state.config.IMAGE_GENERATION_ENGINE = config.IMAGE_GENERATION_ENGINE
app.state.config.ENABLE_IMAGE_GENERATION = config.ENABLE_IMAGE_GENERATION

app.state.config.IMAGES_OPENAI_API_BASE_URL = config.IMAGES_OPENAI_API_BASE_URL
app.state.config.IMAGES_OPENAI_API_KEY = config.IMAGES_OPENAI_API_KEY

app.state.config.IMAGE_GENERATION_MODEL = config.IMAGE_GENERATION_MODEL

app.state.config.AUTOMATIC1111_BASE_URL = config.AUTOMATIC1111_BASE_URL
app.state.config.AUTOMATIC1111_API_AUTH = config.AUTOMATIC1111_API_AUTH
app.state.config.AUTOMATIC1111_CFG_SCALE = config.AUTOMATIC1111_CFG_SCALE
app.state.config.AUTOMATIC1111_SAMPLER = config.AUTOMATIC1111_SAMPLER
app.state.config.AUTOMATIC1111_SCHEDULER = config.AUTOMATIC1111_SCHEDULER
app.state.config.COMFYUI_BASE_URL = config.COMFYUI_BASE_URL
app.state.config.COMFYUI_API_KEY = config.COMFYUI_API_KEY
app.state.config.COMFYUI_WORKFLOW = config.COMFYUI_WORKFLOW
app.state.config.COMFYUI_WORKFLOW_NODES = config.COMFYUI_WORKFLOW_NODES

app.state.config.IMAGE_SIZE = config.IMAGE_SIZE
app.state.config.IMAGE_STEPS = config.IMAGE_STEPS


########################################
#
# AUDIO
#
########################################

app.state.config.STT_OPENAI_API_BASE_URL = config.STT_OPENAI_API_BASE_URL
app.state.config.STT_OPENAI_API_KEY = config.STT_OPENAI_API_KEY
app.state.config.STT_ENGINE = config.STT_ENGINE
app.state.config.STT_MODEL = config.STT_MODEL

app.state.config.WHISPER_MODEL = config.WHISPER_MODEL

app.state.config.TTS_OPENAI_API_BASE_URL = config.TTS_OPENAI_API_BASE_URL
app.state.config.TTS_OPENAI_API_KEY = config.TTS_OPENAI_API_KEY
app.state.config.TTS_ENGINE = config.TTS_ENGINE
app.state.config.TTS_MODEL = config.TTS_MODEL
app.state.config.TTS_VOICE = config.TTS_VOICE
app.state.config.TTS_API_KEY = config.TTS_API_KEY
app.state.config.TTS_SPLIT_ON = config.TTS_SPLIT_ON


app.state.config.TTS_AZURE_SPEECH_REGION = config.TTS_AZURE_SPEECH_REGION
app.state.config.TTS_AZURE_SPEECH_OUTPUT_FORMAT = config.TTS_AZURE_SPEECH_OUTPUT_FORMAT


app.state.faster_whisper_model = None
app.state.speech_synthesiser = None
app.state.speech_speaker_embeddings_dataset = None


########################################
#
# TASKS
#
########################################


app.state.config.TASK_MODEL = config.TASK_MODEL
app.state.config.TASK_MODEL_EXTERNAL = config.TASK_MODEL_EXTERNAL


app.state.config.ENABLE_SEARCH_QUERY_GENERATION = config.ENABLE_SEARCH_QUERY_GENERATION
app.state.config.ENABLE_RETRIEVAL_QUERY_GENERATION = (
    config.ENABLE_RETRIEVAL_QUERY_GENERATION
)
app.state.config.ENABLE_AUTOCOMPLETE_GENERATION = config.ENABLE_AUTOCOMPLETE_GENERATION
app.state.config.ENABLE_TAGS_GENERATION = config.ENABLE_TAGS_GENERATION


app.state.config.TITLE_GENERATION_PROMPT_TEMPLATE = (
    config.TITLE_GENERATION_PROMPT_TEMPLATE
)
app.state.config.TAGS_GENERATION_PROMPT_TEMPLATE = (
    config.TAGS_GENERATION_PROMPT_TEMPLATE
)
app.state.config.TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE = (
    config.TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE
)
app.state.config.QUERY_GENERATION_PROMPT_TEMPLATE = (
    config.QUERY_GENERATION_PROMPT_TEMPLATE
)
app.state.config.AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE = (
    config.AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE
)
app.state.config.AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH = (
    config.AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH
)

########################################
#
# WEBUI
#
########################################

app.state.MODELS = {}


class RedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if the request is a GET request
        if request.method == "GET":
            path = request.url.path
            query_params = dict(parse_qs(urlparse(str(request.url)).query))

            # Check for the specific watch path and the presence of 'v' parameter
            if path.endswith("/watch") and "v" in query_params:
                video_id = query_params["v"][0]  # Extract the first 'v' parameter
                encoded_video_id = urlencode({"youtube": video_id})
                redirect_url = f"/?{encoded_video_id}"
                return RedirectResponse(url=redirect_url)

        # Proceed with the normal flow of other requests
        response = await call_next(request)
        return response


# Add the middleware to the app
app.add_middleware(RedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructlogContextMiddleware)


@app.middleware("http")
async def commit_session_after_request(request: Request, call_next):
    response = await call_next(request)
    # log.debug("Commit session after request")
    Session.commit()
    return response


@app.middleware("http")
async def check_url(request: Request, call_next):
    start_time = int(time.time())
    request.state.enable_api_key = app.state.config.ENABLE_API_KEY
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def inspect_websocket(request: Request, call_next):
    if (
        "/ws/socket.io" in request.url.path
        and request.query_params.get("transport") == "websocket"
    ):
        upgrade = (request.headers.get("Upgrade") or "").lower()
        connection = (request.headers.get("Connection") or "").lower().split(",")
        # Check that there's the correct headers for an upgrade, else reject the connection
        # This is to work around this upstream issue: https://github.com/miguelgrinberg/python-engineio/issues/367
        if upgrade != "websocket" or "upgrade" not in connection:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid WebSocket upgrade request"},
            )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/ws", socket_app)


app.include_router(ollama.router, prefix="/ollama", tags=["ollama"])
app.include_router(openai.router, prefix="/openai", tags=["openai"])


app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["pipelines"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(images.router, prefix="/api/v1/images", tags=["images"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(retrieval.router, prefix="/api/v1/retrieval", tags=["retrieval"])

app.include_router(configs.router, prefix="/api/v1/configs", tags=["configs"])

app.include_router(auths.router, prefix="/api/v1/auths", tags=["auths"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(chats.router, prefix="/api/v1/chats", tags=["chats"])

app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])

app.include_router(memories.router, prefix="/api/v1/memories", tags=["memories"])
app.include_router(folders.router, prefix="/api/v1/folders", tags=["folders"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["groups"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(functions.router, prefix="/api/v1/functions", tags=["functions"])
app.include_router(
    evaluations.router, prefix="/api/v1/evaluations", tags=["evaluations"]
)
app.include_router(utils.router, prefix="/api/v1/utils", tags=["utils"])


##################################
#
# Chat Endpoints
#
##################################


@app.get("/api/models")
async def get_models(request: Request, user=Depends(get_verified_user)):
    def get_filtered_models(models, user):
        filtered_models = []
        for model in models:
            if model.get("arena"):
                if has_access(
                    user.id,
                    type="read",
                    access_control=model.get("info", {})
                    .get("meta", {})
                    .get("access_control", {}),
                ):
                    filtered_models.append(model)
                continue

            model_info = Models.get_model_by_id(model["id"])
            if model_info:
                if user.id == model_info.user_id or has_access(
                    user.id, type="read", access_control=model_info.access_control
                ):
                    filtered_models.append(model)

        return filtered_models

    models = await get_all_models(request)

    # Filter out filter pipelines
    models = [
        model
        for model in models
        if "pipeline" not in model or model["pipeline"].get("type", None) != "filter"
    ]

    model_order_list = request.app.state.config.MODEL_ORDER_LIST
    if model_order_list:
        model_order_dict = {model_id: i for i, model_id in enumerate(model_order_list)}
        # Sort models by order list priority, with fallback for those not in the list
        models.sort(
            key=lambda x: (model_order_dict.get(x["id"], float("inf")), x["name"])
        )

    # Filter out models that the user does not have access to
    if user.role == "user" and not BYPASS_MODEL_ACCESS_CONTROL:
        models = get_filtered_models(models, user)

    log.debug(
        f"/api/models returned filtered models accessible to the user: {json.dumps([model['id'] for model in models])}"
    )
    return {"data": models}


@app.get("/api/models/base")
async def get_base_models(request: Request, user=Depends(get_admin_user)):
    models = await get_all_base_models(request)
    return {"data": models}


@app.post("/api/chat/completions")
async def chat_completion(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
):
    if not request.app.state.MODELS:
        await get_all_models(request)

    tasks = form_data.pop("background_tasks", None)
    try:
        model_id = form_data.get("model", None)
        if model_id not in request.app.state.MODELS:
            raise Exception("Model not found")
        model = request.app.state.MODELS[model_id]

        # Check if user has access to the model
        if not BYPASS_MODEL_ACCESS_CONTROL and user.role == "user":
            try:
                check_model_access(user, model)
            except Exception as e:
                raise e

        metadata = {
            "user_id": user.id,
            "chat_id": form_data.pop("chat_id", None),
            "message_id": form_data.pop("id", None),
            "session_id": form_data.pop("session_id", None),
            "tool_ids": form_data.get("tool_ids", None),
            "files": form_data.get("files", None),
            "features": form_data.get("features", None),
        }
        form_data["metadata"] = metadata

        form_data, events = await process_chat_payload(
            request, form_data, metadata, user, model
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    try:
        response = await chat_completion_handler(request, form_data, user)
        return await process_chat_response(
            request, response, form_data, user, events, metadata, tasks
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Alias for chat_completion (Legacy)
generate_chat_completions = chat_completion
generate_chat_completion = chat_completion


@app.post("/api/chat/completed")
async def chat_completed(
    request: Request, form_data: dict, user=Depends(get_verified_user)
):
    try:
        return await chat_completed_handler(request, form_data, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post("/api/chat/actions/{action_id}")
async def chat_action(
    request: Request, action_id: str, form_data: dict, user=Depends(get_verified_user)
):
    try:
        return await chat_action_handler(request, action_id, form_data, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post("/api/tasks/stop/{task_id}")
async def stop_task_endpoint(task_id: str, user=Depends(get_verified_user)):
    try:
        result = await stop_task(task_id)  # Use the function from tasks.py
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


##################################
#
# Config Endpoints
#
##################################


@app.get("/api/config")
async def get_app_config(request: Request, response: Response):
    user = None
    data = None
    if "token" in request.cookies:
        token = request.cookies.get("token")
        try:
            data = decode_token(token)
        except jwt.ExpiredSignatureError:
            try:
                data = refresh_jwt(request, response)
            except jwt.ExpiredSignatureError:
                # if this is expired it's okay
                # The current code allows accessing config
                # for onboarding below.
                pass
        except Exception as e:
            log.debug(e)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        if data is not None and "id" in data:
            user = Users.get_user_by_id(data["id"])

    onboarding = False
    if user is None:
        user_count = Users.get_num_users()
        onboarding = user_count == 0 and config.ENABLE_ONBOARDING_PAGE

    return {
        **({"onboarding": True} if onboarding else {}),
        "status": True,
        "name": WEBUI_NAME,
        "version": VERSION,
        "default_locale": str(config.DEFAULT_LOCALE),
        "oauth": {
            "providers": {
                name: config.get("name", name)
                for name, config in config.OAUTH_PROVIDERS.items()
            }
        },
        "features": {
            "auth": WEBUI_AUTH,
            "auth_trusted_header": bool(app.state.AUTH_TRUSTED_EMAIL_HEADER),
            "enable_ldap": app.state.config.ENABLE_LDAP,
            "enable_api_key": app.state.config.ENABLE_API_KEY,
            "enable_signup": app.state.config.ENABLE_SIGNUP,
            "enable_login_form": app.state.config.ENABLE_LOGIN_FORM,
            "enable_websocket": ENABLE_WEBSOCKET_SUPPORT,
            **(
                {
                    "enable_channels": app.state.config.ENABLE_CHANNELS,
                    "enable_web_search": app.state.config.ENABLE_RAG_WEB_SEARCH,
                    "enable_google_drive_integration": app.state.config.ENABLE_GOOGLE_DRIVE_INTEGRATION,
                    "enable_image_generation": app.state.config.ENABLE_IMAGE_GENERATION,
                    "enable_community_sharing": app.state.config.ENABLE_COMMUNITY_SHARING,
                    "enable_message_rating": app.state.config.ENABLE_MESSAGE_RATING,
                    "allow_simultaneous_models": config.ALLOW_SIMULTANEOUS_MODELS,
                    "enable_chat_controls": config.ENABLE_CHAT_CONTROLS,
                    "enable_set_as_default_model": config.ENABLE_SET_AS_DEFAULT_MODEL,
                    "enable_admin_export": config.ENABLE_ADMIN_EXPORT,
                    "enable_admin_chat_access": config.ENABLE_ADMIN_CHAT_ACCESS,
                    "default_show_changelog": config.DEFAULT_SHOW_CHANGELOG,
                    "default_show_version_update": config.DEFAULT_SHOW_VERSION_UPDATE,
                    "enable_active_users_count": config.ENABLE_ACTIVE_USERS_COUNT,
                    "enable_admin_feedbacks": config.ENABLE_ADMIN_FEEDBACKS,
                    "enable_record_voice_and_call": config.ENABLE_RECORD_VOICE_AND_CALL,
                    "enable_more_inputs": config.ENABLE_MORE_INPUTS,
                    "enable_disclaimer": config.ENABLE_DISCLAIMER,
                    "enable_sidebar_search": config.ENABLE_SIDEBAR_SEARCH,
                    "enable_sidebar_create_folder": config.ENABLE_SIDEBAR_CREATE_FOLDER,
                    "enable_floating_buttons": config.ENABLE_FLOATING_BUTTONS,
                    "enable_delete_button": config.ENABLE_DELETE_BUTTON,
                    "enable_sidebar_user_profile": config.ENABLE_SIDEBAR_USER_PROFILE,
                    "enable_message_input_logo": config.ENABLE_MESSAGE_INPUT_LOGO,
                    "enable_prompt_suggestions": config.ENABLE_PROMPT_SUGGESTIONS,
                    "enable_user_settings_menu": config.ENABLE_USER_SETTINGS_MENU,
                    "enable_model_selector_search": config.ENABLE_MODEL_SELECTOR_SEARCH,
                    "enable_response_prompt_edit": config.ENABLE_RESPONSE_PROMPT_EDIT,
                    "enable_response_continue": config.ENABLE_RESPONSE_CONTINUE,
                    "enable_rag_hybrid_search": app.state.config.ENABLE_RAG_HYBRID_SEARCH,
                    "enable_screen_capture": config.ENABLE_SCREEN_CAPTURE,
                }
                if user is not None
                else {}
            ),
        },
        "google_drive": {
            "client_id": config.GOOGLE_DRIVE_CLIENT_ID,
            "api_key": config.GOOGLE_DRIVE_API_KEY,
        },
        **(
            {
                "default_models": app.state.config.DEFAULT_MODELS,
                "default_prompt_suggestions": app.state.config.DEFAULT_PROMPT_SUGGESTIONS,
                "audio": {
                    "tts": {
                        "engine": app.state.config.TTS_ENGINE,
                        "voice": app.state.config.TTS_VOICE,
                        "split_on": app.state.config.TTS_SPLIT_ON,
                    },
                    "stt": {
                        "engine": app.state.config.STT_ENGINE,
                    },
                },
                "file": {
                    "max_size": app.state.config.RAG_FILE_MAX_SIZE,
                    "max_count": app.state.config.RAG_FILE_MAX_COUNT,
                },
                "permissions": {**app.state.config.USER_PERMISSIONS},
            }
            if user is not None
            else {}
        ),
    }


class UrlForm(BaseModel):
    url: str


@app.get("/api/webhook")
async def get_webhook_url(user=Depends(get_admin_user)):
    return {
        "url": app.state.config.WEBHOOK_URL,
    }


@app.post("/api/webhook")
async def update_webhook_url(form_data: UrlForm, user=Depends(get_admin_user)):
    app.state.config.WEBHOOK_URL = form_data.url
    app.state.WEBHOOK_URL = app.state.config.WEBHOOK_URL
    return {"url": app.state.config.WEBHOOK_URL}


@app.get("/api/version")
async def get_app_version():
    return {
        "version": VERSION,
    }


@app.get("/api/version/updates")
async def get_app_latest_release_version():
    if OFFLINE_MODE:
        log.debug(
            f"Offline mode is enabled, returning current version as latest version"
        )
        return {"current": VERSION, "latest": VERSION}
    try:
        timeout = aiohttp.ClientTimeout(total=1)
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.get(
                "https://api.github.com/repos/open-webui/open-webui/releases/latest"
            ) as response:
                response.raise_for_status()
                data = await response.json()
                latest_version = data["tag_name"]

                return {"current": VERSION, "latest": latest_version[1:]}
    except Exception as e:
        log.debug(e)
        return {"current": VERSION, "latest": VERSION}


@app.get("/api/changelog")
async def get_app_changelog():
    return {key: CHANGELOG[key] for idx, key in enumerate(CHANGELOG) if idx < 5}


############################
# OAuth Login & Callback
############################

# SessionMiddleware is used by authlib for oauth
if len(config.OAUTH_PROVIDERS) > 0:
    app.add_middleware(
        SessionMiddleware,
        secret_key=WEBUI_SECRET_KEY,
        session_cookie="oui-session",
        same_site=WEBUI_SESSION_COOKIE_SAME_SITE,
        https_only=WEBUI_SESSION_COOKIE_SECURE,
    )


@app.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    return await oauth_manager.handle_login(provider, request)


# OAuth login logic is as follows:
# 1. Attempt to find a user with matching subject ID, tied to the provider
# 2. If OAUTH_MERGE_ACCOUNTS_BY_EMAIL is true, find a user with the email address provided via OAuth
#    - This is considered insecure in general, as OAuth providers do not always verify email addresses
# 3. If there is no user, and ENABLE_OAUTH_SIGNUP is true, create a user
#    - Email addresses are considered unique, so we fail registration if the email address is already taken
@app.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, response: Response):
    return await oauth_manager.handle_callback(provider, request, response)


@app.get("/manifest.json")
async def get_manifest_json():
    return {
        "name": WEBUI_NAME,
        "short_name": WEBUI_NAME,
        "description": "Open WebUI is an open, extensible, user-friendly interface for AI that adapts to your workflow.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#343541",
        "orientation": "natural",
        "icons": [
            {
                "src": "/static/logo.png",
                "type": "image/png",
                "sizes": "500x500",
                "purpose": "any",
            },
            {
                "src": "/static/logo.png",
                "type": "image/png",
                "sizes": "500x500",
                "purpose": "maskable",
            },
        ],
    }


@app.get("/opensearch.xml")
async def get_opensearch_xml():
    xml_content = rf"""
    <OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/" xmlns:moz="http://www.mozilla.org/2006/browser/search/">
    <ShortName>{WEBUI_NAME}</ShortName>
    <Description>Search {WEBUI_NAME}</Description>
    <InputEncoding>UTF-8</InputEncoding>
    <Image width="16" height="16" type="image/x-icon">{app.state.config.WEBUI_URL}/static/favicon.png</Image>
    <Url type="text/html" method="get" template="{app.state.config.WEBUI_URL}/?q={"{searchTerms}"}"/>
    <moz:SearchForm>{app.state.config.WEBUI_URL}</moz:SearchForm>
    </OpenSearchDescription>
    """
    return Response(content=xml_content, media_type="application/xml")


@app.get("/health")
async def healthcheck():
    pipeline_is_healthy = False
    cohere_is_healthy = False
    db_is_healthy = False
    redis_is_healthy = False

    # get db health
    Session.execute(text("SELECT 1;")).all()
    db_is_healthy = True

    # get pipelines health
    response = requests.get("http://localhost:9099/models")
    if response.status_code == 200:
        pipeline_is_healthy = True

    # check redis health with REDIS_URL
    redis_client = redis.StrictRedis.from_url(WEBSOCKET_REDIS_URL)
    pong = redis_client.ping()
    redis_is_healthy = pong is True

    # get cohere proxy health
    response = requests.get("http://localhost:9101/health")
    if response.status_code == 200:
        cohere_is_healthy = True

    healthy = (
        pipeline_is_healthy and cohere_is_healthy and db_is_healthy and redis_is_healthy
    )

    if not healthy:
        log.warning(
            f"Readiness check at: {int(time.time())}\n"
            + f"pipeline_is_healthy: {pipeline_is_healthy}\n"
            + f"cohere_is_healthy: {cohere_is_healthy}\n"
            + f"db_is_healthy: {db_is_healthy}\n"
            + f"redis_is_healthy: {redis_is_healthy}\n"
        )
        raise HTTPException(status_code=500, detail="Health check failed")

    return {"status": True}


@app.get("/health/db")
async def healthcheck_with_db():
    Session.execute(text("SELECT 1;")).all()
    return {"status": True}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/cache", StaticFiles(directory=CACHE_DIR), name="cache")


def swagger_ui_html(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon.png",
    )


applications.get_swagger_ui_html = swagger_ui_html

if os.path.exists(FRONTEND_BUILD_DIR):
    mimetypes.add_type("text/javascript", ".js")
    app.mount(
        "/",
        SPAStaticFiles(directory=FRONTEND_BUILD_DIR, html=True),
        name="spa-static-files",
    )
else:
    log.warning(
        f"Frontend build directory not found at '{FRONTEND_BUILD_DIR}'. Serving API only."
    )
