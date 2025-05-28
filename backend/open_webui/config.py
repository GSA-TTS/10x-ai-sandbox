import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Generic, Optional, Self, TypeVar, List
from urllib.parse import urlparse

import chromadb
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings
import redis
import requests

from open_webui.env import (
    OPEN_WEBUI_DIR,
    DATA_DIR,
    ENV,
    FRONTEND_BUILD_DIR,
    WEBUI_AUTH,
    WEBUI_FAVICON_URL,
    WEBUI_NAME,
    log,
    DATABASE_URL,
    CONFIGURATION_REDIS_URL,
)
from .config_migration import migrate_db_config


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

####################################
# Config helpers
####################################


# Function to run the alembic migrations
def run_migrations():
    print("Running migrations")
    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config(OPEN_WEBUI_DIR / "alembic.ini")

        # Set the script location dynamically
        migrations_path = OPEN_WEBUI_DIR / "migrations"
        alembic_cfg.set_main_option("script_location", str(migrations_path))

        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Error: {e}")


run_migrations()


r = redis.from_url(CONFIGURATION_REDIS_URL)
hash_name = "config"


# TODO: Remove config migration once the config refactor is fully deployed
migrate_db_config(r, hash_name)


def load_json_config():
    with open(f"{DATA_DIR}/config.json", "r") as file:
        return json.load(file)


def reset_config():
    r.delete(hash_name)


# When initializing, check if config.json exists and migrate it to the database
if os.path.exists(f"{DATA_DIR}/config.json"):
    data = load_json_config()
    for key, value in data.items():
        r.hset(hash_name, key, json.dumps(value))
    os.rename(f"{DATA_DIR}/config.json", f"{DATA_DIR}/old_config.json")


def get_config():
    config = r.hgetall(hash_name)
    return {k.decode(): json.loads(v.decode()) for k, v in config.items()}


def save_config(config):
    for key, value in config.items():
        r.hset(hash_name, key, json.dumps(value))


T = TypeVar("T")


class PersistentConfig(Generic[T]):
    def __init__(self, config_name: str, value: T):
        self.name = config_name
        result = r.hsetnx(hash_name, config_name, json.dumps(value))
        if result == 1:
            log.info(f"'{config_name}' was not in Redis, persisted it")

    def __str__(self):
        return str(self.value)

    @property
    def __dict__(self):
        raise TypeError(
            "PersistentConfig object cannot be converted to dict, use .value instead:",
            self.name,
        )

    def __getattribute__(self, item):
        if item == "__dict__":
            raise TypeError(
                "PersistentConfig object cannot be converted to dict, use .value instead:",
                self.name,
            )
        return super().__getattribute__(item)

    @property
    def value(self) -> T:
        return json.loads(r.hget(hash_name, self.name))

    @value.setter
    def value(self, value: T):
        r.hset(hash_name, self.name, json.dumps(value))


class AppConfig:
    _state: dict[str, PersistentConfig]

    def __init__(self):
        super().__setattr__("_state", {})

    def __setattr__(self, key, value):
        if isinstance(value, PersistentConfig):
            self._state[key] = value
        else:
            if key in self._state:
                self._state[key].value = value
            else:
                self._state[key] = PersistentConfig(key, value)

    def __getattr__(self, key):
        return self._state[key].value


class Config(BaseSettings):
    """
    Base class for all configuration items. This extends Pydantic's
    BaseSettings to hook in some persistence features. When creating a
    configuration class derived from this one, you can use the `persistent()`
    static method to mark a field as persistent. This is the equivalent of
    Field(default=..., persistent=True) in Pydantic, but it also ensures that
    the correct extra attribute named "persistent" is used.
    """

    @staticmethod
    def persistent(default: Any = None, **kwargs):
        """Convenience method that wraps Pydantic's Field to add a persistent attribute"""
        kwargs["persistent"] = True
        return Field(default=default, **kwargs)

    def model_post_init(self, __context: Any) -> None:
        persistent_fields = [
            key
            for key, field_info in self.model_fields.items()
            if field_info.json_schema_extra
            and field_info.json_schema_extra.get("persistent")
        ]
        for key, value in self.model_dump().items():
            if key in persistent_fields:
                PersistentConfig(key, value)


####################################
# WEBUI_AUTH (Required for security)
####################################


class WebUIAuthConfig(Config):
    ENABLE_API_KEY: bool = Config.persistent(True)
    ENABLE_API_KEY_ENDPOINT_RESTRICTIONS: bool = Config.persistent(False)
    API_KEY_ALLOWED_ENDPOINTS: str = Config.persistent("")
    JWT_EXPIRES_IN: str = Config.persistent("-1")
    JWT_REFRESH_EXPIRES_IN: str = Config.persistent("-1")


####################################
# OAuth config
####################################


class OAuthConfig(Config):
    ENABLE_OAUTH_SIGNUP: bool = Config.persistent(False)
    OAUTH_MERGE_ACCOUNTS_BY_EMAIL: bool = Config.persistent(False)
    GOOGLE_CLIENT_ID: str = Config.persistent("")
    GOOGLE_CLIENT_SECRET: str = Config.persistent("")
    GOOGLE_OAUTH_SCOPE: str = Config.persistent("openid email profile")
    GOOGLE_REDIRECT_URI: str = Config.persistent("")
    MICROSOFT_CLIENT_ID: str = Config.persistent("")
    MICROSOFT_CLIENT_SECRET: str = Config.persistent("")
    MICROSOFT_CLIENT_TENANT_ID: str = Config.persistent("")
    MICROSOFT_OAUTH_SCOPE: str = Config.persistent("openid email profile")
    MICROSOFT_REDIRECT_URI: str = Config.persistent("")
    OAUTH_CLIENT_ID: str = Config.persistent("")
    OAUTH_CLIENT_SECRET: str = Config.persistent("")
    OPENID_PROVIDER_URL: str = Config.persistent("")
    OPENID_REDIRECT_URI: str = Config.persistent("")
    OAUTH_SCOPES: str = Config.persistent("openid email profile")
    OAUTH_PROVIDER_NAME: str = Config.persistent("SSO")
    OAUTH_USERNAME_CLAIM: str = Config.persistent("name")
    OAUTH_PICTURE_CLAIM: str = Config.persistent("picture")
    OAUTH_EMAIL_CLAIM: str = Config.persistent("email")
    OAUTH_GROUPS_CLAIM: str = Config.persistent("groups")
    ENABLE_OAUTH_ROLE_MANAGEMENT: bool = Config.persistent(False)
    ENABLE_OAUTH_GROUP_MANAGEMENT: bool = Config.persistent(False)
    OAUTH_ROLES_CLAIM: str = Config.persistent("roles")
    OAUTH_ALLOWED_ROLES: List[str] = Config.persistent(["user", "admin"])
    OAUTH_ADMIN_ROLES: List[str] = Config.persistent(["admin"])
    OAUTH_ACR_CLAIM: str = Config.persistent("")
    OAUTH_NONCE_CLAIM: str = Config.persistent("")
    OAUTH_USE_PKCE: str = Config.persistent("")
    OAUTH_ALLOWED_DOMAINS: List[str] = Config.persistent(["*"])
    OAUTH_PROVIDERS: dict[str, dict[str, Any]] = {}

    def model_post_init(self, __context: Any) -> None:
        self.OAUTH_PROVIDERS.clear()
        if self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET:
            self.OAUTH_PROVIDERS["google"] = {
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
                "scope": self.GOOGLE_OAUTH_SCOPE,
                "redirect_uri": self.GOOGLE_REDIRECT_URI,
            }

        if (
            self.MICROSOFT_CLIENT_ID
            and self.MICROSOFT_CLIENT_SECRET
            and self.MICROSOFT_CLIENT_TENANT_ID
        ):
            self.OAUTH_PROVIDERS["microsoft"] = {
                "client_id": self.MICROSOFT_CLIENT_ID,
                "client_secret": self.MICROSOFT_CLIENT_SECRET,
                "server_metadata_url": f"https://login.microsoftonline.com/{self.MICROSOFT_CLIENT_TENANT_ID}/v2.0/.well-known/openid-configuration",
                "scope": self.MICROSOFT_OAUTH_SCOPE,
                "redirect_uri": self.MICROSOFT_REDIRECT_URI,
            }

        if (
            self.OAUTH_CLIENT_ID
            and self.OAUTH_CLIENT_SECRET
            and self.OPENID_PROVIDER_URL
        ):
            self.OAUTH_PROVIDERS["oidc"] = {
                "client_id": self.OAUTH_CLIENT_ID,
                "client_secret": self.OAUTH_CLIENT_SECRET,
                "server_metadata_url": self.OPENID_PROVIDER_URL,
                "scope": self.OAUTH_SCOPES,
                "name": self.OAUTH_PROVIDER_NAME,
                "redirect_uri": self.OPENID_REDIRECT_URI,
            }

            # TODO: does this work out of the box for google and microsoft, too?
            if self.OAUTH_USE_PKCE:
                self.OAUTH_PROVIDERS["oidc"]["pkce"] = self.OAUTH_USE_PKCE
        super().model_post_init(__context)


####################################
# Static DIR
####################################

STATIC_DIR = Path(os.getenv("STATIC_DIR", OPEN_WEBUI_DIR / "static")).resolve()

frontend_favicon = FRONTEND_BUILD_DIR / "static" / "favicon.png"

if frontend_favicon.exists():
    try:
        shutil.copyfile(frontend_favicon, STATIC_DIR / "favicon.png")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
else:
    logging.warning(f"Frontend favicon not found at {frontend_favicon}")

frontend_splash = FRONTEND_BUILD_DIR / "static" / "gsa-logo.svg"

if frontend_splash.exists():
    try:
        shutil.copyfile(frontend_splash, STATIC_DIR / "gsa-logo.svg")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
else:
    logging.warning(f"Frontend splash not found at {frontend_splash}")

gsai_logo = FRONTEND_BUILD_DIR / "static" / "gsai.png"

if gsai_logo.exists():
    try:
        shutil.copyfile(gsai_logo, STATIC_DIR / "gsai.png")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
else:
    logging.warning(f"Built by logo not found at {gsai_logo}")


####################################
# CUSTOM_NAME
####################################

CUSTOM_NAME = os.environ.get("CUSTOM_NAME", "")

if CUSTOM_NAME:
    try:
        r = requests.get(f"https://api.openwebui.com/api/v1/custom/{CUSTOM_NAME}")
        data = r.json()
        if r.ok:
            if "logo" in data:
                WEBUI_FAVICON_URL = url = (
                    f"https://api.openwebui.com{data['logo']}"
                    if data["logo"][0] == "/"
                    else data["logo"]
                )

                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(f"{STATIC_DIR}/favicon.png", "wb") as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)

            if "splash" in data:
                url = (
                    f"https://api.openwebui.com{data['splash']}"
                    if data["splash"][0] == "/"
                    else data["splash"]
                )

                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(f"{STATIC_DIR}/gsa-logo.svg", "wb") as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)

            WEBUI_NAME = data["name"]
    except Exception as e:
        log.exception(e)
        pass


####################################
# STORAGE PROVIDER
####################################


class StorageProviderConfig(Config):
    STORAGE_PROVIDER: str = Config.persistent("")  # local (default), s3
    S3_REGION_NAME: Optional[str] = Config.persistent(None)
    S3_BUCKET_NAME: Optional[str] = Config.persistent(None)
    S3_ENDPOINT_URL: Optional[str] = Config.persistent(None)


####################################
# File Upload DIR
####################################

UPLOAD_DIR = f"{DATA_DIR}/uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


####################################
# Cache DIR
####################################

CACHE_DIR = f"{DATA_DIR}/cache"
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)


####################################
# OLLAMA_BASE_URL
####################################


class OllamaConfig(Config):
    ENABLE_OLLAMA_API: bool = Config.persistent(True)
    OLLAMA_API_BASE_URL: str = "http://localhost:11434/api"
    OLLAMA_BASE_URL: str = ""
    K8S_FLAG: bool = False
    USE_OLLAMA_DOCKER: bool = False
    OLLAMA_BASE_URLS: List[str] = Config.persistent([])
    OLLAMA_API_CONFIGS: dict = Config.persistent({})
    RAG_OLLAMA_BASE_URL: str = Config.persistent(OLLAMA_BASE_URL)
    RAG_OLLAMA_API_KEY: str = Config.persistent("")

    def model_post_init(self, __context: Any) -> None:
        if self.OLLAMA_BASE_URL:
            self.OLLAMA_BASE_URL = (
                self.OLLAMA_BASE_URL[:-1]
                if self.OLLAMA_BASE_URL.endswith("/")
                else self.OLLAMA_BASE_URL
            )
        if self.OLLAMA_BASE_URL == "" and self.OLLAMA_API_BASE_URL != "":
            self.OLLAMA_BASE_URL = (
                self.OLLAMA_API_BASE_URL[:-4]
                if self.OLLAMA_API_BASE_URL.endswith("/api")
                else self.OLLAMA_API_BASE_URL
            )
        if ENV == "prod":
            if self.OLLAMA_BASE_URL == "/ollama" and not self.K8S_FLAG:
                if self.USE_OLLAMA_DOCKER:
                    self.OLLAMA_BASE_URL = "http://localhost:11434"
                else:
                    self.OLLAMA_BASE_URL = "http://host.docker.internal:11434"
            elif self.K8S_FLAG:
                self.OLLAMA_BASE_URL = (
                    "http://ollama-service.open-webui.svc.cluster.local:11434"
                )
        self.OLLAMA_BASE_URLS = self.OLLAMA_BASE_URLS or [self.OLLAMA_BASE_URL]
        super().model_post_init(__context)


####################################
# OPENAI_API
####################################


class OpenAIConfig(Config):
    ENABLE_OPENAI_API: bool = Config.persistent(True)
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEYS: List[str] = Config.persistent([])
    OPENAI_API_BASE_URLS: List[str] = Config.persistent([])
    OPENAI_API_CONFIGS: dict = Config.persistent({})
    RAG_OPENAI_API_BASE_URL: str = Config.persistent(OPENAI_API_BASE_URL)
    RAG_OPENAI_API_KEY: str = Config.persistent(OPENAI_API_KEY)
    IMAGES_OPENAI_API_BASE_URL: str = Config.persistent(OPENAI_API_BASE_URL)
    IMAGES_OPENAI_API_KEY: str = Config.persistent(OPENAI_API_KEY)
    STT_OPENAI_API_BASE_URL: str = Config.persistent(OPENAI_API_BASE_URL)
    STT_OPENAI_API_KEY: str = Config.persistent(OPENAI_API_KEY)
    TTS_OPENAI_API_BASE_URL: str = Config.persistent(OPENAI_API_BASE_URL)
    TTS_OPENAI_API_KEY: str = Config.persistent(OPENAI_API_KEY)

    def model_post_init(self, __context: Any) -> None:
        if self.OPENAI_API_KEY:
            self.OPENAI_API_KEYS = [self.OPENAI_API_KEY]
        if self.OPENAI_API_BASE_URL:
            self.OPENAI_API_BASE_URLS = [self.OPENAI_API_BASE_URL]
        # Get the actual OpenAI API key based on the base URL
        try:
            self.OPENAI_API_KEY = self.OPENAI_API_KEYS[
                self.OPENAI_API_BASE_URLS.index("https://api.openai.com/v1")
            ]
        except Exception:
            pass
        super().model_post_init(__context)


####################################
# WEBUI
####################################


class BannerModel(BaseModel):
    id: str
    type: str
    title: Optional[str] = None
    content: str
    dismissible: bool
    timestamp: int


class WebUIConfig(Config):
    WEBUI_URL: str = Config.persistent("http://localhost:3000")
    ENABLE_ONBOARDING_PAGE: bool = False
    ENABLE_SIGNUP: bool = Config.persistent(False if not WEBUI_AUTH else True)
    ENABLE_LOGIN_FORM: bool = True
    DEFAULT_LOCALE: str = Config.persistent("")
    DEFAULT_MODELS: Optional[str] = Config.persistent(None)
    DEFAULT_PROMPT_SUGGESTIONS: List[dict] = Config.persistent(
        [
            {
                "title": [
                    "Help me with the FAR",
                ],
                "content": "Help me understand the Federal Acquisition Regulations; give me an overview of the FAR Parts and how they're used",
            },
            {
                "title": [
                    "Generate ideas for a report",
                ],
                "content": "Generate ideas for a report about historical preservation, specifically focused on federal buildings",
            },
            {
                "title": [
                    "Summarize meeting notes",
                ],
                "content": "Summarize meeting notes and pull out key points and next steps. Remember to avoid putting personally identifiable information into the chat.",
            },
        ]
    )
    MODEL_ORDER_LIST: List[str] = Config.persistent([])
    DEFAULT_USER_ROLE: str = Config.persistent("pending")
    USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS: bool = False
    USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS: bool = False
    USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS: bool = False
    USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS: bool = False
    USER_PERMISSIONS_CHAT_FILE_UPLOAD: bool = True
    USER_PERMISSIONS_CHAT_DELETE: bool = True
    USER_PERMISSIONS_CHAT_EDIT: bool = True
    USER_PERMISSIONS_CHAT_TEMPORARY: bool = True
    USER_PERMISSIONS: dict[str, dict[str, bool]] = Config.persistent(
        {
            "workspace": {
                "models": USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS,
                "knowledge": USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS,
                "prompts": USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS,
                "tools": USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS,
            },
            "chat": {
                "file_upload": USER_PERMISSIONS_CHAT_FILE_UPLOAD,
                "delete": USER_PERMISSIONS_CHAT_DELETE,
                "edit": USER_PERMISSIONS_CHAT_EDIT,
                "temporary": USER_PERMISSIONS_CHAT_TEMPORARY,
            },
        }
    )
    ENABLE_CHANNELS: bool = Config.persistent(False)
    ENABLE_EVALUATION_ARENA_MODELS: bool = Config.persistent(True)
    EVALUATION_ARENA_MODELS: List[str] = Config.persistent([])
    DEFAULT_ARENA_MODEL: dict[str, Any] = {
        "id": "arena-model",
        "name": "Arena Model",
        "meta": {
            "profile_image_url": "/favicon.png",
            "description": "Submit your questions to anonymous AI chatbots and vote on the best response.",
            "model_ids": None,
        },
    }
    WEBHOOK_URL: str = Config.persistent("")
    ENABLE_ADMIN_EXPORT: bool = True
    ENABLE_ADMIN_CHAT_ACCESS: bool = True
    ENABLE_COMMUNITY_SHARING: bool = Config.persistent(True)
    ENABLE_MESSAGE_RATING: bool = Config.persistent(True)
    ALLOW_SIMULTANEOUS_MODELS: bool = True
    DEFAULT_SHOW_VERSION_UPDATE: bool = False
    DEFAULT_SHOW_CHANGELOG: bool = False
    ENABLE_MORE_INPUTS: bool = False
    ENABLE_CHAT_CONTROLS: bool = True
    ENABLE_SET_AS_DEFAULT_MODEL: bool = True
    ENABLE_ACTIVE_USERS_COUNT: bool = False
    ENABLE_ADMIN_FEEDBACKS: bool = True
    ENABLE_RECORD_VOICE_AND_CALL: bool = False
    ENABLE_DISCLAIMER: bool = True
    ENABLE_SIDEBAR_SEARCH: bool = False
    ENABLE_SIDEBAR_CREATE_FOLDER: bool = False
    ENABLE_FLOATING_BUTTONS: bool = False
    ENABLE_DELETE_BUTTON: bool = False
    ENABLE_SIDEBAR_USER_PROFILE: bool = False
    ENABLE_MESSAGE_INPUT_LOGO: bool = False
    ENABLE_PROMPT_SUGGESTIONS: bool = True
    ENABLE_USER_SETTINGS_MENU: bool = True
    ENABLE_MODEL_SELECTOR_SEARCH: bool = False
    ENABLE_RESPONSE_PROMPT_EDIT: bool = True
    ENABLE_RESPONSE_CONTINUE: bool = True
    ENABLE_SCREEN_CAPTURE: bool = False
    # For production, you should only need one host as
    # fastapi serves the svelte-kit built frontend and backend from the same host and port.
    # To test CORS_ALLOW_ORIGIN locally, you can set something like
    # CORS_ALLOW_ORIGIN=http://localhost:5173;http://localhost:8080
    # in your .env file depending on your frontend port, 5173 in this case.
    CORS_ALLOW_ORIGIN: List[str] = ["*"]
    WEBUI_BANNERS: List[BannerModel] = Config.persistent([])
    SHOW_ADMIN_DETAILS: bool = Config.persistent(True)
    ADMIN_EMAIL: Optional[str] = Config.persistent(None)

    # validate CORS_ALLOW_ORIGIN
    @field_validator("CORS_ALLOW_ORIGIN")
    def is_cors_valid(cls, origins: List[str]) -> List[str]:
        for origin in origins:
            if origin != "*":
                parsed_url = urlparse(origin)
                # Check if the scheme is either http or https
                if parsed_url.scheme not in ["http", "https"]:
                    raise ValueError(
                        f"Invalid scheme in CORS_ALLOW_ORIGIN: '{origin}'. Only 'http' and 'https' are allowed."
                    )
                # Ensure that the netloc (domain + port) is present, indicating it's a valid URL
                if not parsed_url.netloc:
                    raise ValueError(
                        f"Invalid URL structure in CORS_ALLOW_ORIGIN: '{origin}'."
                    )
            else:
                log.warning(
                    "\n\nWARNING: CORS_ALLOW_ORIGIN IS SET TO '*' - NOT RECOMMENDED FOR PRODUCTION DEPLOYMENTS.\n"
                )
        return origins


####################################
# TASKS
####################################


class TasksConfig(Config):
    TASK_MODEL: str = Config.persistent("")
    TASK_MODEL_EXTERNAL: str = Config.persistent("")
    TITLE_GENERATION_PROMPT_TEMPLATE: str = Config.persistent("")
    DEFAULT_TITLE_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "title_generation_prompt_template.txt"
    ).read_text()
    TAGS_GENERATION_PROMPT_TEMPLATE: str = Config.persistent("")
    DEFAULT_TAGS_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "tags_generation_prompt_template.txt"
    ).read_text()
    ENABLE_TAGS_GENERATION: bool = Config.persistent(True)
    ENABLE_SEARCH_QUERY_GENERATION: bool = Config.persistent(True)
    ENABLE_RETRIEVAL_QUERY_GENERATION: bool = Config.persistent(True)
    QUERY_GENERATION_PROMPT_TEMPLATE: str = Config.persistent("")
    DEFAULT_QUERY_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "query_generation_prompt_template.txt"
    ).read_text()
    ENABLE_AUTOCOMPLETE_GENERATION: bool = Config.persistent(True)
    AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH: int = Config.persistent(-1)
    AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE: str = Config.persistent("")
    DEFAULT_AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "autocomplete_generation_prompt_template.txt"
    ).read_text()
    TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE: str = Config.persistent("")
    DEFAULT_TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "tools_function_calling_prompt_template.txt"
    ).read_text()
    DEFAULT_EMOJI_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent
        / "config_defaults"
        / "emoji_generation_prompt_template.txt"
    ).read_text()
    DEFAULT_MOA_GENERATION_PROMPT_TEMPLATE: str = Path(
        Path(__file__).parent / "config_defaults" / "moa_generation_prompt_template.txt"
    ).read_text()


####################################
# Vector Database
####################################


class VectorDatabaseConfig(Config):
    VECTOR_DB: str = "pgvector"
    # Chroma
    CHROMA_DATA_PATH: str = f"{DATA_DIR}/vector_db"
    CHROMA_TENANT: str = chromadb.DEFAULT_TENANT
    CHROMA_DATABASE: str = chromadb.DEFAULT_DATABASE
    CHROMA_HTTP_HOST: str = ""
    CHROMA_HTTP_PORT: int = 8000
    CHROMA_CLIENT_AUTH_PROVIDER: str = ""
    CHROMA_CLIENT_AUTH_CREDENTIALS: str = ""
    CHROMA_HTTP_HEADERS: Optional[dict[str, str]] = None
    CHROMA_HTTP_SSL: bool = False
    # Milvus
    MILVUS_URI: str = f"{DATA_DIR}/vector_db/milvus.db"
    # Qdrant
    QDRANT_URI: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    # OpenSearch
    OPENSEARCH_URI: str = "https://localhost:9200"
    OPENSEARCH_SSL: bool = True
    OPENSEARCH_CERT_VERIFY: bool = False
    OPENSEARCH_USERNAME: Optional[str] = None
    OPENSEARCH_PASSWORD: Optional[str] = None
    # Pgvector
    PGVECTOR_DB_URL: str = DATABASE_URL

    @field_validator("CHROMA_HTTP_HEADERS", mode="before")
    def parse_chroma_http_headers(cls, v: str | dict) -> dict[str, str]:
        if isinstance(v, dict):
            return v
        if not v:
            return None
        return dict(pair.split("=") for pair in v.split(","))

    @model_validator(mode="after")
    def validate_pgvector_db_url(self) -> Self:
        if (
            self.VECTOR_DB == "pgvector"
            and self.PGVECTOR_DB_URL
            and not self.PGVECTOR_DB_URL.startswith("postgres")
        ):
            raise ValueError(
                "Pgvector requires setting PGVECTOR_DB_URL or using Postgres with vector extension as the primary database."
            )
        return self


####################################
# Information Retrieval (RAG)
####################################


class RAGConfig(Config):
    # If configured, Google Drive will be available as an upload option.
    ENABLE_GOOGLE_DRIVE_INTEGRATION: bool = Config.persistent(False)
    GOOGLE_DRIVE_CLIENT_ID: str = Config.persistent("")
    GOOGLE_DRIVE_API_KEY: str = Config.persistent("")
    # RAG Content Extraction
    # See OpenAI and Ollama configs for RAG base URLs and API keys
    CONTENT_EXTRACTION_ENGINE: str = Config.persistent("")
    TIKA_SERVER_URL: str = Config.persistent(
        "http://tika:9998"
    )  # Default for sidecar deployment
    RAG_TOP_K: int = Config.persistent(3)
    RAG_RELEVANCE_THRESHOLD: float = Config.persistent(0.0)
    ENABLE_RAG_HYBRID_SEARCH: bool = Config.persistent(False)
    RAG_FILE_MAX_COUNT: Optional[int] = Config.persistent(None)
    RAG_FILE_MAX_SIZE: Optional[int] = Config.persistent(None)
    ENABLE_RAG_WEB_LOADER_SSL_VERIFICATION: bool = Config.persistent(True)
    RAG_EMBEDDING_ENGINE: str = Config.persistent("")
    PDF_EXTRACT_IMAGES: bool = Config.persistent(False)
    RAG_EMBEDDING_MODEL: str = Config.persistent(
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    RAG_EMBEDDING_MODEL_AUTO_UPDATE: bool = True
    RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE: bool = True
    RAG_EMBEDDING_BATCH_SIZE: int = Config.persistent(1)
    RAG_RERANKING_MODEL: str = Config.persistent("")
    RAG_RERANKING_MODEL_AUTO_UPDATE: bool = True
    RAG_RERANKING_MODEL_TRUST_REMOTE_CODE: bool = True
    RAG_TEXT_SPLITTER: str = Config.persistent("")
    TIKTOKEN_CACHE_DIR: str = f"{CACHE_DIR}/tiktoken"
    TIKTOKEN_ENCODING_NAME: str = Config.persistent("cl100k_base")
    CHUNK_SIZE: int = Config.persistent(1000)
    CHUNK_OVERLAP: int = Config.persistent(100)
    DEFAULT_RAG_TEMPLATE: str = Path(
        Path(__file__).parent / "config_defaults" / "rag_template.txt"
    ).read_text()
    RAG_TEMPLATE: str = Config.persistent(DEFAULT_RAG_TEMPLATE)
    ENABLE_RAG_LOCAL_WEB_FETCH: bool = False
    YOUTUBE_LOADER_LANGUAGE: List[str] = Config.persistent(["en"])
    YOUTUBE_LOADER_PROXY_URL: str = Config.persistent("")
    ENABLE_RAG_WEB_SEARCH: bool = Config.persistent(False)
    RAG_WEB_SEARCH_ENGINE: str = Config.persistent("")
    # You can provide a list of your own websites to filter after performing a web search.
    # This ensures the highest level of safety and reliability of the information sources.
    # Example: ["wikipedia.com", "wikimedia.org", "wikidata.org"]
    RAG_WEB_SEARCH_DOMAIN_FILTER_LIST: List[str] = Config.persistent([])
    SEARXNG_QUERY_URL: str = Config.persistent("")
    GOOGLE_PSE_API_KEY: str = Config.persistent("")
    GOOGLE_PSE_ENGINE_ID: str = Config.persistent("")
    BRAVE_SEARCH_API_KEY: str = Config.persistent("")
    KAGI_SEARCH_API_KEY: str = Config.persistent("")
    MOJEEK_SEARCH_API_KEY: str = Config.persistent("")
    SERPSTACK_API_KEY: str = Config.persistent("")
    SERPSTACK_HTTPS: bool = Config.persistent(True)
    SERPER_API_KEY: str = Config.persistent("")
    SERPLY_API_KEY: str = Config.persistent("")
    TAVILY_API_KEY: str = Config.persistent("")
    JINA_API_KEY: str = Config.persistent("")
    SEARCHAPI_API_KEY: str = Config.persistent("")
    SEARCHAPI_ENGINE: str = Config.persistent("")
    BING_SEARCH_V7_ENDPOINT: str = Config.persistent(
        "https://api.bing.microsoft.com/v7.0/search"
    )
    BING_SEARCH_V7_SUBSCRIPTION_KEY: str = Config.persistent("")
    RAG_WEB_SEARCH_RESULT_COUNT: int = Config.persistent(3)
    RAG_WEB_SEARCH_CONCURRENT_REQUESTS: int = Config.persistent(10)


####################################
# Images
####################################


class ImagesConfig(Config):
    # See OpenAI config for OpenAI image processing base URL and API key
    IMAGE_GENERATION_ENGINE: str = Config.persistent("openai")
    ENABLE_IMAGE_GENERATION: bool = Config.persistent(False)
    AUTOMATIC1111_BASE_URL: str = Config.persistent("")
    AUTOMATIC1111_API_AUTH: str = Config.persistent("")
    AUTOMATIC1111_CFG_SCALE: Optional[float] = Config.persistent(None)
    AUTOMATIC1111_SAMPLER: Optional[str] = Config.persistent(None)
    AUTOMATIC1111_SCHEDULER: Optional[str] = Config.persistent(None)
    COMFYUI_BASE_URL: str = Config.persistent("")
    COMFYUI_API_KEY: str = Config.persistent("")
    COMFYUI_DEFAULT_WORKFLOW: str = Path(
        Path(__file__).parent / "config_defaults" / "comfyui_default_workflow.json"
    ).read_text()
    COMFYUI_WORKFLOW: str = Config.persistent(COMFYUI_DEFAULT_WORKFLOW)
    COMFYUI_WORKFLOW_NODES: List[str] = Config.persistent([])
    IMAGE_SIZE: str = Config.persistent("512x512")
    IMAGE_STEPS: int = Config.persistent(50)
    IMAGE_GENERATION_MODEL: str = Config.persistent("")


####################################
# Audio
####################################


class AudioConfig(Config):
    # See OpenAI config for OpenAI STT and TTS base URLs and API keys
    WHISPER_MODEL: str = Config.persistent("base")
    WHISPER_MODEL_DIR: str = f"{CACHE_DIR}/whisper/models"
    WHISPER_MODEL_AUTO_UPDATE: bool = False
    STT_ENGINE: str = Config.persistent("")
    STT_MODEL: str = Config.persistent("")
    TTS_API_KEY: str = Config.persistent("")
    TTS_ENGINE: str = Config.persistent("")
    TTS_MODEL: str = Config.persistent("tts-1")  # OpenAI default model
    TTS_VOICE: str = Config.persistent("alloy")  # OpenAI default voice
    TTS_SPLIT_ON: str = Config.persistent("punctuation")
    TTS_AZURE_SPEECH_REGION: str = Config.persistent("eastus")
    TTS_AZURE_SPEECH_OUTPUT_FORMAT: str = Config.persistent(
        "audio-24khz-160kbitrate-mono-mp3"
    )


####################################
# LDAP
####################################


class LDAPConfig(Config):
    ENABLE_LDAP: bool = Config.persistent(False)
    LDAP_SERVER_LABEL: str = Config.persistent("LDAP Server")
    LDAP_SERVER_HOST: str = Config.persistent("localhost")
    LDAP_SERVER_PORT: int = Config.persistent(389)
    LDAP_ATTRIBUTE_FOR_USERNAME: str = Config.persistent("uid")
    LDAP_APP_DN: str = Config.persistent("")
    LDAP_APP_PASSWORD: str = Config.persistent("")
    LDAP_SEARCH_BASE: str = Config.persistent("")
    LDAP_SEARCH_FILTERS: str = Config.persistent("")
    LDAP_USE_TLS: bool = Config.persistent(True)
    LDAP_CA_CERT_FILE: str = Config.persistent("")
    LDAP_CIPHERS: str = Config.persistent("ALL")


####################################
# Aggregated config
####################################


class FullConfig(
    WebUIAuthConfig,
    OAuthConfig,
    StorageProviderConfig,
    OllamaConfig,
    OpenAIConfig,
    WebUIConfig,
    TasksConfig,
    VectorDatabaseConfig,
    RAGConfig,
    ImagesConfig,
    AudioConfig,
    LDAPConfig,
):
    pass


# This `config` object should be imported by other modules in order to gain access to all configuration values.
config = FullConfig()
