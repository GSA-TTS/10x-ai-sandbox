import json
import logging
import os
import shutil
from pathlib import Path
from typing import Generic, Optional, TypeVar, List
from urllib.parse import urlparse

import chromadb
from pydantic import BaseModel
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
    OFFLINE_MODE,
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


migrate_db_config(r, hash_name)


T = TypeVar("T")


class PersistentConfig(Generic[T]):
    def __init__(self, config_name: str, value: T):
        self.name = config_name
        if not r.hexists(hash_name, config_name):
            log.info(f"'{config_name}' is not in Redis, persisting value")
            r.hset(hash_name, config_name, json.dumps(value))

    def __str__(self):
        return str(self.value)

    @property
    def __dict__(self):
        raise TypeError(
            "PersistentConfig object cannot be converted to dict, use .value instead."
        )

    def __getattribute__(self, item):
        if item == "__dict__":
            raise TypeError(
                "PersistentConfig object cannot be converted to dict, use .value instead."
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
            self._state[key].value = value

    def __getattr__(self, key):
        return self._state[key].value


####################################
# OAuth config
####################################

OAUTH_PROVIDERS = {}

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

STORAGE_PROVIDER = os.environ.get("STORAGE_PROVIDER", "")  # defaults to local, s3

S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID", None)
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", None)
S3_REGION_NAME = os.environ.get("S3_REGION_NAME", None)
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", None)
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", None)

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

ENABLE_OLLAMA_API = PersistentConfig(
    "ENABLE_OLLAMA_API",
    os.environ.get("ENABLE_OLLAMA_API", "True").lower() == "true",
)

OLLAMA_API_BASE_URL = os.environ.get(
    "OLLAMA_API_BASE_URL", "http://localhost:11434/api"
)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "")
if OLLAMA_BASE_URL:
    # Remove trailing slash
    OLLAMA_BASE_URL = (
        OLLAMA_BASE_URL[:-1] if OLLAMA_BASE_URL.endswith("/") else OLLAMA_BASE_URL
    )


K8S_FLAG = os.environ.get("K8S_FLAG", "")
USE_OLLAMA_DOCKER = os.environ.get("USE_OLLAMA_DOCKER", "false")

if OLLAMA_BASE_URL == "" and OLLAMA_API_BASE_URL != "":
    OLLAMA_BASE_URL = (
        OLLAMA_API_BASE_URL[:-4]
        if OLLAMA_API_BASE_URL.endswith("/api")
        else OLLAMA_API_BASE_URL
    )

if ENV == "prod":
    if OLLAMA_BASE_URL == "/ollama" and not K8S_FLAG:
        if USE_OLLAMA_DOCKER.lower() == "true":
            # if you use all-in-one docker container (Open WebUI + Ollama)
            # with the docker build arg USE_OLLAMA=true (--build-arg="USE_OLLAMA=true") this only works with http://localhost:11434
            OLLAMA_BASE_URL = "http://localhost:11434"
        else:
            OLLAMA_BASE_URL = "http://host.docker.internal:11434"
    elif K8S_FLAG:
        OLLAMA_BASE_URL = "http://ollama-service.open-webui.svc.cluster.local:11434"


OLLAMA_BASE_URLS = os.environ.get("OLLAMA_BASE_URLS", "")
OLLAMA_BASE_URLS = OLLAMA_BASE_URLS if OLLAMA_BASE_URLS != "" else OLLAMA_BASE_URL

OLLAMA_BASE_URLS = [url.strip() for url in OLLAMA_BASE_URLS.split(";")]
OLLAMA_BASE_URLS = PersistentConfig("OLLAMA_BASE_URLS", OLLAMA_BASE_URLS)

OLLAMA_API_CONFIGS = PersistentConfig(
    "OLLAMA_API_CONFIGS",
    {},
)

####################################
# OPENAI_API
####################################


ENABLE_OPENAI_API = PersistentConfig(
    "ENABLE_OPENAI_API",
    os.environ.get("ENABLE_OPENAI_API", "True").lower() == "true",
)


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE_URL = os.environ.get("OPENAI_API_BASE_URL", "")


if OPENAI_API_BASE_URL == "":
    OPENAI_API_BASE_URL = "https://api.openai.com/v1"

OPENAI_API_KEYS = os.environ.get("OPENAI_API_KEYS", "")
OPENAI_API_KEYS = OPENAI_API_KEYS if OPENAI_API_KEYS != "" else OPENAI_API_KEY

OPENAI_API_KEYS = [url.strip() for url in OPENAI_API_KEYS.split(";")]
OPENAI_API_KEYS = PersistentConfig("OPENAI_API_KEYS", OPENAI_API_KEYS)

OPENAI_API_BASE_URLS = os.environ.get("OPENAI_API_BASE_URLS", "")
OPENAI_API_BASE_URLS = (
    OPENAI_API_BASE_URLS if OPENAI_API_BASE_URLS != "" else OPENAI_API_BASE_URL
)

OPENAI_API_BASE_URLS = [
    url.strip() if url != "" else "https://api.openai.com/v1"
    for url in OPENAI_API_BASE_URLS.split(";")
]
OPENAI_API_BASE_URLS = PersistentConfig("OPENAI_API_BASE_URLS", OPENAI_API_BASE_URLS)

OPENAI_API_CONFIGS = PersistentConfig(
    "OPENAI_API_CONFIGS",
    {},
)

# Get the actual OpenAI API key based on the base URL
OPENAI_API_KEY = ""
try:
    OPENAI_API_KEY = OPENAI_API_KEYS.value[
        OPENAI_API_BASE_URLS.value.index("https://api.openai.com/v1")
    ]
except Exception:
    pass
OPENAI_API_BASE_URL = "https://api.openai.com/v1"

####################################
# WEBUI
####################################

ENABLE_SIGNUP = PersistentConfig(
    "ENABLE_SIGNUP",
    (
        False
        if not WEBUI_AUTH
        else os.environ.get("ENABLE_SIGNUP", "True").lower() == "true"
    ),
)

DEFAULT_PROMPT_SUGGESTIONS = PersistentConfig(
    "DEFAULT_PROMPT_SUGGESTIONS",
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
    ],
)

USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS = (
    os.environ.get("USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS", "False").lower()
    == "true"
)

USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS = (
    os.environ.get("USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS", "False").lower()
    == "true"
)

USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS = (
    os.environ.get("USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS", "False").lower()
    == "true"
)

USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS = (
    os.environ.get("USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS", "False").lower() == "true"
)

USER_PERMISSIONS_CHAT_FILE_UPLOAD = (
    os.environ.get("USER_PERMISSIONS_CHAT_FILE_UPLOAD", "True").lower() == "true"
)

USER_PERMISSIONS_CHAT_DELETE = (
    os.environ.get("USER_PERMISSIONS_CHAT_DELETE", "True").lower() == "true"
)

USER_PERMISSIONS_CHAT_EDIT = (
    os.environ.get("USER_PERMISSIONS_CHAT_EDIT", "True").lower() == "true"
)

USER_PERMISSIONS_CHAT_TEMPORARY = (
    os.environ.get("USER_PERMISSIONS_CHAT_TEMPORARY", "True").lower() == "true"
)

USER_PERMISSIONS = PersistentConfig(
    "USER_PERMISSIONS",
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
    },
)

DEFAULT_ARENA_MODEL = {
    "id": "arena-model",
    "name": "Arena Model",
    "meta": {
        "profile_image_url": "/favicon.png",
        "description": "Submit your questions to anonymous AI chatbots and vote on the best response.",
        "model_ids": None,
    },
}

ENABLE_ADMIN_EXPORT = os.environ.get("ENABLE_ADMIN_EXPORT", "True").lower() == "true"

ENABLE_ADMIN_CHAT_ACCESS = (
    os.environ.get("ENABLE_ADMIN_CHAT_ACCESS", "True").lower() == "true"
)

ALLOW_SIMULTANEOUS_MODELS = (
    os.environ.get("ALLOW_SIMULTANEOUS_MODELS", "True").lower() == "true"
)

DEFAULT_SHOW_VERSION_UPDATE = (
    os.environ.get("DEFAULT_SHOW_VERSION_UPDATE", "False").lower() == "true"
)

DEFAULT_SHOW_CHANGELOG = (
    os.environ.get("DEFAULT_SHOW_CHANGELOG", "False").lower() == "true"
)

ENABLE_MORE_INPUTS = os.environ.get("ENABLE_MORE_INPUTS", "False").lower() == "true"

ENABLE_CHAT_CONTROLS = os.environ.get("ENABLE_CHAT_CONTROLS", "True").lower() == "true"

ENABLE_SET_AS_DEFAULT_MODEL = (
    os.environ.get("ENABLE_SET_AS_DEFAULT_MODEL", "True").lower() == "true"
)

ENABLE_ACTIVE_USERS_COUNT = (
    os.environ.get("ENABLE_ACTIVE_USERS_COUNT", "False").lower() == "true"
)

ENABLE_ADMIN_FEEDBACKS = (
    os.environ.get("ENABLE_ADMIN_FEEDBACKS", "True").lower() == "true"
)

ENABLE_RECORD_VOICE_AND_CALL = (
    os.environ.get("ENABLE_RECORD_VOICE_AND_CALL", "False").lower() == "true"
)

ENABLE_DISCLAIMER = os.environ.get("ENABLE_DISCLAIMER", "True").lower() == "true"


ENABLE_SIDEBAR_SEARCH = (
    os.environ.get("ENABLE_SIDEBAR_SEARCH", "False").lower() == "true"
)

ENABLE_SIDEBAR_CREATE_FOLDER = (
    os.environ.get("ENABLE_SIDEBAR_CREATE_FOLDER", "False").lower() == "true"
)

ENABLE_FLOATING_BUTTONS = (
    os.environ.get("ENABLE_FLOATING_BUTTONS", "False").lower() == "true"
)

ENABLE_DELETE_BUTTON = os.environ.get("ENABLE_DELETE_BUTTON", "False").lower() == "true"

ENABLE_SIDEBAR_USER_PROFILE = (
    os.environ.get("ENABLE_SIDEBAR_USER_PROFILE", "False").lower() == "true"
)

ENABLE_MESSAGE_INPUT_LOGO = (
    os.environ.get("ENABLE_MESSAGE_INPUT_LOGO", "False").lower() == "true"
)

ENABLE_PROMPT_SUGGESTIONS = (
    os.environ.get("ENABLE_PROMPT_SUGGESTIONS", "True").lower() == "true"
)

ENABLE_USER_SETTINGS_MENU = (
    os.environ.get("ENABLE_USER_SETTINGS_MENU", "True").lower() == "true"
)

ENABLE_MODEL_SELECTOR_SEARCH = (
    os.environ.get("ENABLE_MODEL_SELECTOR_SEARCH", "False").lower() == "true"
)

ENABLE_RESPONSE_PROMPT_EDIT = (
    os.environ.get("ENABLE_RESPONSE_PROMPT_EDIT", "True").lower() == "true"
)

ENABLE_RESPONSE_CONTINUE = (
    os.environ.get("ENABLE_RESPONSE_CONTINUE", "True").lower() == "true"
)


def validate_cors_origins(origins):
    for origin in origins:
        if origin != "*":
            validate_cors_origin(origin)


def validate_cors_origin(origin):
    parsed_url = urlparse(origin)

    # Check if the scheme is either http or https
    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError(
            f"Invalid scheme in CORS_ALLOW_ORIGIN: '{origin}'. Only 'http' and 'https' are allowed."
        )

    # Ensure that the netloc (domain + port) is present, indicating it's a valid URL
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL structure in CORS_ALLOW_ORIGIN: '{origin}'.")


# For production, you should only need one host as
# fastapi serves the svelte-kit built frontend and backend from the same host and port.
# To test CORS_ALLOW_ORIGIN locally, you can set something like
# CORS_ALLOW_ORIGIN=http://localhost:5173;http://localhost:8080
# in your .env file depending on your frontend port, 5173 in this case.
CORS_ALLOW_ORIGIN = os.environ.get("CORS_ALLOW_ORIGIN", "*").split(";")

if "*" in CORS_ALLOW_ORIGIN:
    log.warning(
        "\n\nWARNING: CORS_ALLOW_ORIGIN IS SET TO '*' - NOT RECOMMENDED FOR PRODUCTION DEPLOYMENTS.\n"
    )

validate_cors_origins(CORS_ALLOW_ORIGIN)


class BannerModel(BaseModel):
    id: str
    type: str
    title: Optional[str] = None
    content: str
    dismissible: bool
    timestamp: int


try:
    banners = json.loads(os.environ.get("WEBUI_BANNERS", "[]"))
    banners = [BannerModel(**banner) for banner in banners]
except Exception as e:
    print(f"Error loading WEBUI_BANNERS: {e}")
    banners = []

WEBUI_BANNERS = PersistentConfig("WEBUI_BANNERS", banners)

####################################
# TASKS
####################################

DEFAULT_TITLE_GENERATION_PROMPT_TEMPLATE = """Create a concise, 3-5 word title with an emoji as a title for the chat history, in the given language. Suitable Emojis for the summary can be used to enhance understanding but avoid quotation marks or special formatting. RESPOND ONLY WITH THE TITLE TEXT.

Examples of titles:
📉 Stock Market Trends
🍪 Perfect Chocolate Chip Recipe
Evolution of Music Streaming
Remote Work Productivity Tips
Artificial Intelligence in Healthcare
🎮 Video Game Development Insights

<chat_history>
{{MESSAGES:END:2}}
</chat_history>"""

DEFAULT_TAGS_GENERATION_PROMPT_TEMPLATE = """### Task:
Generate 1-3 broad tags categorizing the main themes of the chat history, along with 1-3 more specific subtopic tags.

### Guidelines:
- Start with high-level domains (e.g. Science, Technology, Philosophy, Arts, Politics, Business, Health, Sports, Entertainment, Education)
- Consider including relevant subfields/subdomains if they are strongly represented throughout the conversation
- If content is too short (less than 3 messages) or too diverse, use only ["General"]
- Use the chat's primary language; default to English if multilingual
- Prioritize accuracy over specificity

### Output:
JSON format: { "tags": ["tag1", "tag2", "tag3"] }

### Chat History:
<chat_history>
{{MESSAGES:END:6}}
</chat_history>"""

DEFAULT_QUERY_GENERATION_PROMPT_TEMPLATE = """### Task:
Analyze the chat history to determine the necessity of generating search queries, in the given language. By default, **prioritize generating 1-3 broad and relevant search queries** unless it is absolutely certain that no additional information is required. The aim is to retrieve comprehensive, updated, and valuable information even with minimal uncertainty. If no search is unequivocally needed, return an empty list.

### Guidelines:
- Respond **EXCLUSIVELY** with a JSON object. Any form of extra commentary, explanation, or additional text is strictly prohibited.
- When generating search queries, respond in the format: { "queries": ["query1", "query2"] }, ensuring each query is distinct, concise, and relevant to the topic.
- If and only if it is entirely certain that no useful results can be retrieved by a search, return: { "queries": [] }.
- Err on the side of suggesting search queries if there is **any chance** they might provide useful or updated information.
- Be concise and focused on composing high-quality search queries, avoiding unnecessary elaboration, commentary, or assumptions.
- Today's date is: {{CURRENT_DATE}}.
- Always prioritize providing actionable and broad queries that maximize informational coverage.

### Output:
Strictly return in JSON format:
{
  "queries": ["query1", "query2"]
}

### Chat History:
<chat_history>
{{MESSAGES:END:6}}
</chat_history>
"""

DEFAULT_AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE = """### Task:
You are an autocompletion system. Continue the text in `<text>` based on the **completion type** in `<type>` and the given language.

### **Instructions**:
1. Analyze `<text>` for context and meaning.
2. Use `<type>` to guide your output:
   - **General**: Provide a natural, concise continuation.
   - **Search Query**: Complete as if generating a realistic search query.
3. Start as if you are directly continuing `<text>`. Do **not** repeat, paraphrase, or respond as a model. Simply complete the text.
4. Ensure the continuation:
   - Flows naturally from `<text>`.
   - Avoids repetition, overexplaining, or unrelated ideas.
5. If unsure, return: `{ "text": "" }`.

### **Output Rules**:
- Respond only in JSON format: `{ "text": "<your_completion>" }`.

### **Examples**:
#### Example 1:
Input:
<type>General</type>
<text>The sun was setting over the horizon, painting the sky</text>
Output:
{ "text": "with vibrant shades of orange and pink." }

#### Example 2:
Input:
<type>Search Query</type>
<text>Top-rated restaurants in</text>
Output:
{ "text": "New York City for Italian cuisine." }

---
### Context:
<chat_history>
{{MESSAGES:END:6}}
</chat_history>
<type>{{TYPE}}</type>
<text>{{PROMPT}}</text>
#### Output:
"""

DEFAULT_TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE = """Available Tools: {{TOOLS}}\nReturn an empty string if no tools match the query. If a function tool matches, construct and return a JSON object in the format {\"name\": \"functionName\", \"parameters\": {\"requiredFunctionParamKey\": \"requiredFunctionParamValue\"}} using the appropriate tool and its parameters. Only return the object and limit the response to the JSON object without additional text."""

DEFAULT_EMOJI_GENERATION_PROMPT_TEMPLATE = """Your task is to reflect the speaker's likely facial expression through a fitting emoji. Interpret emotions from the message and reflect their facial expression using fitting, diverse emojis (e.g., 😊, 😢, 😡, 😱).

Message: ```{{prompt}}```"""

DEFAULT_MOA_GENERATION_PROMPT_TEMPLATE = """You have been provided with a set of responses from various models to the latest user query: "{{prompt}}"

Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability.

Responses from models: {{responses}}"""

####################################
# Vector Database
####################################

VECTOR_DB = os.environ.get("VECTOR_DB", "pgvector")

# Chroma
CHROMA_DATA_PATH = f"{DATA_DIR}/vector_db"
CHROMA_TENANT = os.environ.get("CHROMA_TENANT", chromadb.DEFAULT_TENANT)
CHROMA_DATABASE = os.environ.get("CHROMA_DATABASE", chromadb.DEFAULT_DATABASE)
CHROMA_HTTP_HOST = os.environ.get("CHROMA_HTTP_HOST", "")
CHROMA_HTTP_PORT = int(os.environ.get("CHROMA_HTTP_PORT", "8000"))
CHROMA_CLIENT_AUTH_PROVIDER = os.environ.get("CHROMA_CLIENT_AUTH_PROVIDER", "")
CHROMA_CLIENT_AUTH_CREDENTIALS = os.environ.get("CHROMA_CLIENT_AUTH_CREDENTIALS", "")
# Comma-separated list of header=value pairs
CHROMA_HTTP_HEADERS = os.environ.get("CHROMA_HTTP_HEADERS", "")
if CHROMA_HTTP_HEADERS:
    CHROMA_HTTP_HEADERS = dict(
        [pair.split("=") for pair in CHROMA_HTTP_HEADERS.split(",")]
    )
else:
    CHROMA_HTTP_HEADERS = None
CHROMA_HTTP_SSL = os.environ.get("CHROMA_HTTP_SSL", "false").lower() == "true"
# this uses the model defined in the Dockerfile ENV variable. If you dont use docker or docker based deployments such as k8s, the default embedding model will be used (sentence-transformers/all-MiniLM-L6-v2)

# Milvus

MILVUS_URI = os.environ.get("MILVUS_URI", f"{DATA_DIR}/vector_db/milvus.db")

# Qdrant
QDRANT_URI = os.environ.get("QDRANT_URI", None)
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)

# OpenSearch
OPENSEARCH_URI = os.environ.get("OPENSEARCH_URI", "https://localhost:9200")
OPENSEARCH_SSL = os.environ.get("OPENSEARCH_SSL", True)
OPENSEARCH_CERT_VERIFY = os.environ.get("OPENSEARCH_CERT_VERIFY", False)
OPENSEARCH_USERNAME = os.environ.get("OPENSEARCH_USERNAME", None)
OPENSEARCH_PASSWORD = os.environ.get("OPENSEARCH_PASSWORD", None)

# Pgvector
PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL", DATABASE_URL)
if VECTOR_DB == "pgvector" and not PGVECTOR_DB_URL.startswith("postgres"):
    raise ValueError(
        "Pgvector requires setting PGVECTOR_DB_URL or using Postgres with vector extension as the primary database."
    )

####################################
# Information Retrieval (RAG)
####################################

RAG_EMBEDDING_MODEL_AUTO_UPDATE = (
    not OFFLINE_MODE
    and os.environ.get("RAG_EMBEDDING_MODEL_AUTO_UPDATE", "True").lower() == "true"
)

RAG_RERANKING_MODEL_AUTO_UPDATE = (
    not OFFLINE_MODE
    and os.environ.get("RAG_RERANKING_MODEL_AUTO_UPDATE", "True").lower() == "true"
)

TIKTOKEN_CACHE_DIR = os.environ.get("TIKTOKEN_CACHE_DIR", f"{CACHE_DIR}/tiktoken")

DEFAULT_RAG_TEMPLATE = """### Task:
Respond to the user query using the provided context, incorporating inline citations in the format [source_id] **only when the <source_id> tag is explicitly provided** in the context.

### Guidelines:
- If you don't know the answer, clearly state that.
- If uncertain, ask the user for clarification.
- Respond in the same language as the user's query.
- If the context is unreadable or of poor quality, inform the user and provide the best possible answer.
- If the answer isn't present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.
- **Only include inline citations using [source_id] when a <source_id> tag is explicitly provided in the context.**
- Do not cite if the <source_id> tag is not provided in the context.
- Do not use XML tags in your response.
- Ensure citations are concise and directly related to the information provided.

### Example of Citation:
If the user asks about a specific topic and the information is found in "whitepaper.pdf" with a provided <source_id>, the response should include the citation like so:
* "According to the study, the proposed method increases efficiency by 20% [whitepaper.pdf]."
If no <source_id> is present, the response should omit the citation.

### Output:
Provide a clear and direct response to the user's query, including inline citations in the format [source_id] only when the <source_id> tag is present in the context.

<context>
{{CONTEXT}}
</context>

<user_query>
{{QUERY}}
</user_query>
"""

####################################
# Images
####################################

COMFYUI_DEFAULT_WORKFLOW = """
{
  "3": {
    "inputs": {
      "seed": 0,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "model.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "text": "Prompt",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""

####################################
# Audio
####################################

WHISPER_MODEL_DIR = os.getenv("WHISPER_MODEL_DIR", f"{CACHE_DIR}/whisper/models")
WHISPER_MODEL_AUTO_UPDATE = (
    not OFFLINE_MODE
    and os.environ.get("WHISPER_MODEL_AUTO_UPDATE", "").lower() == "true"
)


class PersistentConfigSettings(BaseSettings):
    """
    Track persistent configuration settings to provide validation and type checking.
    Individual PersistentConfig instances should be generated from these settings.
    """

    # API Key Settings
    ENABLE_API_KEY: bool = True
    ENABLE_API_KEY_ENDPOINT_RESTRICTIONS: bool = False
    API_KEY_ALLOWED_ENDPOINTS: str = ""
    JWT_EXPIRES_IN: str = "-1"

    # OAuth Settings
    ENABLE_OAUTH_SIGNUP: bool = False
    OAUTH_MERGE_ACCOUNTS_BY_EMAIL: bool = False
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_SCOPE: str = "openid email profile"
    GOOGLE_REDIRECT_URI: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_TENANT_ID: str = ""
    MICROSOFT_OAUTH_SCOPE: str = "openid email profile"
    MICROSOFT_REDIRECT_URI: str = ""
    OAUTH_CLIENT_ID: str = ""
    OAUTH_CLIENT_SECRET: str = ""
    OPENID_PROVIDER_URL: str = ""
    OPENID_REDIRECT_URI: str = ""
    OAUTH_SCOPES: str = "openid email profile"
    OAUTH_PROVIDER_NAME: str = "SSO"
    OAUTH_USERNAME_CLAIM: str = "name"
    OAUTH_PICTURE_CLAIM: str = "picture"
    OAUTH_EMAIL_CLAIM: str = "email"
    OAUTH_GROUPS_CLAIM: str = "groups"
    ENABLE_OAUTH_ROLE_MANAGEMENT: bool = False
    ENABLE_OAUTH_GROUP_MANAGEMENT: bool = False
    OAUTH_ROLES_CLAIM: str = "roles"
    OAUTH_ALLOWED_ROLES: List[str] = ["user", "admin"]
    OAUTH_ADMIN_ROLES: List[str] = ["admin"]
    OAUTH_ACR_CLAIM: str = ""
    OAUTH_NONCE_CLAIM: str = ""
    OAUTH_USE_PKCE: str = ""
    OAUTH_ALLOWED_DOMAINS: List[str] = ["*"]

    # WebUI Settings
    WEBUI_URL: str = "http://localhost:3000"
    ENABLE_ONBOARDING_PAGE: bool = False
    ENABLE_LOGIN_FORM: bool = True
    DEFAULT_LOCALE: str = ""
    DEFAULT_MODELS: Optional[str] = None
    MODEL_ORDER_LIST: List[str] = []
    DEFAULT_USER_ROLE: str = "pending"
    ENABLE_CHANNELS: bool = False
    ENABLE_EVALUATION_ARENA_MODELS: bool = True
    EVALUATION_ARENA_MODELS: List[str] = []
    WEBHOOK_URL: str = ""
    ENABLE_COMMUNITY_SHARING: bool = True
    ENABLE_MESSAGE_RATING: bool = True
    SHOW_ADMIN_DETAILS: bool = True
    ADMIN_EMAIL: Optional[str] = None

    # Task Settings
    TASK_MODEL: str = ""
    TASK_MODEL_EXTERNAL: str = ""
    TITLE_GENERATION_PROMPT_TEMPLATE: str = ""
    TAGS_GENERATION_PROMPT_TEMPLATE: str = ""
    ENABLE_TAGS_GENERATION: bool = True
    ENABLE_SEARCH_QUERY_GENERATION: bool = True
    ENABLE_RETRIEVAL_QUERY_GENERATION: bool = True
    QUERY_GENERATION_PROMPT_TEMPLATE: str = ""
    ENABLE_AUTOCOMPLETE_GENERATION: bool = True
    AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH: int = -1
    AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE: str = ""
    TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE: str = ""

    # RAG Settings
    ENABLE_GOOGLE_DRIVE_INTEGRATION: bool = False
    GOOGLE_DRIVE_CLIENT_ID: str = ""
    GOOGLE_DRIVE_API_KEY: str = ""
    CONTENT_EXTRACTION_ENGINE: str = ""  # RAG Content Extraction
    TIKA_SERVER_URL: str = "http://tika:9998"  # Default for sidecar deployment
    RAG_TOP_K: int = 3
    RAG_RELEVANCE_THRESHOLD: float = 0.0
    ENABLE_RAG_HYBRID_SEARCH: bool = False
    RAG_FILE_MAX_COUNT: Optional[int] = None
    RAG_FILE_MAX_SIZE: Optional[int] = None
    ENABLE_RAG_WEB_LOADER_SSL_VERIFICATION: bool = True
    RAG_EMBEDDING_ENGINE: str = ""
    PDF_EXTRACT_IMAGES: bool = False
    RAG_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE: bool = True
    RAG_EMBEDDING_BATCH_SIZE: int = 1
    RAG_RERANKING_MODEL: str = ""
    RAG_RERANKING_MODEL_TRUST_REMOTE_CODE: bool = True
    RAG_TEXT_SPLITTER: str = ""
    TIKTOKEN_ENCODING_NAME: str = "cl100k_base"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    RAG_TEMPLATE: str = DEFAULT_RAG_TEMPLATE
    RAG_OPENAI_API_BASE_URL: str = OPENAI_API_BASE_URL
    RAG_OPENAI_API_KEY: str = OPENAI_API_KEY
    RAG_OLLAMA_BASE_URL: str = OLLAMA_BASE_URL
    RAG_OLLAMA_API_KEY: str = ""
    ENABLE_RAG_LOCAL_WEB_FETCH: bool = False
    YOUTUBE_LOADER_LANGUAGE: List[str] = ["en"]
    YOUTUBE_LOADER_PROXY_URL: str = ""
    ENABLE_RAG_WEB_SEARCH: bool = False
    RAG_WEB_SEARCH_ENGINE: str = ""
    # You can provide a list of your own websites to filter after performing a web search.
    # This ensures the highest level of safety and reliability of the information sources.
    # Example: ["wikipedia.com", "wikimedia.org", "wikidata.org"]
    RAG_WEB_SEARCH_DOMAIN_FILTER_LIST: List[str] = []
    RAG_WEB_SEARCH_RESULT_COUNT: int = 3
    RAG_WEB_SEARCH_CONCURRENT_REQUESTS: int = 10
    SEARXNG_QUERY_URL: str = ""
    GOOGLE_PSE_API_KEY: str = ""
    GOOGLE_PSE_ENGINE_ID: str = ""
    BRAVE_SEARCH_API_KEY: str = ""
    KAGI_SEARCH_API_KEY: str = ""
    MOJEEK_SEARCH_API_KEY: str = ""
    SERPSTACK_API_KEY: str = ""
    SERPSTACK_HTTPS: bool = True
    SERPER_API_KEY: str = ""
    SERPLY_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    JINA_API_KEY: str = ""
    SEARCHAPI_API_KEY: str = ""
    SEARCHAPI_ENGINE: str = ""
    BING_SEARCH_V7_ENDPOINT: str = "https://api.bing.microsoft.com/v7.0/search"
    BING_SEARCH_V7_SUBSCRIPTION_KEY: str = ""

    # Image Settings
    IMAGE_GENERATION_ENGINE: str = "openai"
    ENABLE_IMAGE_GENERATION: bool = False
    AUTOMATIC1111_BASE_URL: str = ""
    AUTOMATIC1111_API_AUTH: str = ""
    AUTOMATIC1111_CFG_SCALE: Optional[float] = None
    AUTOMATIC1111_SAMPLER: Optional[str] = None
    AUTOMATIC1111_SCHEDULER: Optional[str] = None
    COMFYUI_BASE_URL: str = ""
    COMFYUI_API_KEY: str = ""
    COMFYUI_WORKFLOW: str = COMFYUI_DEFAULT_WORKFLOW
    COMFYUI_WORKFLOW_NODES: List[str] = []
    IMAGES_OPENAI_API_BASE_URL: str = OPENAI_API_BASE_URL
    IMAGES_OPENAI_API_KEY: str = OPENAI_API_KEY
    IMAGE_SIZE: str = "512x512"
    IMAGE_STEPS: int = 50
    IMAGE_GENERATION_MODEL: str = ""

    # Audio Settings
    WHISPER_MODEL: str = "base"
    AUDIO_STT_OPENAI_API_BASE_URL: str = OPENAI_API_BASE_URL
    AUDIO_STT_OPENAI_API_KEY: str = OPENAI_API_KEY
    AUDIO_STT_ENGINE: str = ""
    AUDIO_STT_MODEL: str = ""
    AUDIO_TTS_OPENAI_API_BASE_URL: str = OPENAI_API_BASE_URL
    AUDIO_TTS_OPENAI_API_KEY: str = OPENAI_API_KEY
    AUDIO_TTS_API_KEY: str = ""
    AUDIO_TTS_ENGINE: str = ""
    AUDIO_TTS_MODEL: str = "tts-1"
    AUDIO_TTS_VOICE: str = "alloy"
    AUDIO_TTS_SPLIT_ON: str = "punctuation"
    AUDIO_TTS_AZURE_SPEECH_REGION: str = "eastus"
    AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT: str = "audio-24khz-160kbitrate-mono-mp3"

    # LDAP Settings
    ENABLE_LDAP: bool = False
    LDAP_SERVER_LABEL: str = "LDAP Server"
    LDAP_SERVER_HOST: str = "localhost"
    LDAP_SERVER_PORT: int = 389
    LDAP_ATTRIBUTE_FOR_USERNAME: str = "uid"
    LDAP_APP_DN: str = ""
    LDAP_APP_PASSWORD: str = ""
    LDAP_SEARCH_BASE: str = ""
    LDAP_SEARCH_FILTERS: str = ""
    LDAP_USE_TLS: bool = True
    LDAP_CA_CERT_FILE: str = ""
    LDAP_CIPHERS: str = "ALL"


# Initialize PersistentConfig settings
settings = PersistentConfigSettings()

# Create PersistentConfig instances from settings
for field_name, field_value in settings.model_dump().items():
    # TODO: add these PersistentConfigs to an AppConfig instance?
    if field_name not in globals():
        globals()[field_name] = PersistentConfig(field_name, field_value)


def load_oauth_providers():
    OAUTH_PROVIDERS.clear()
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        OAUTH_PROVIDERS["google"] = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "scope": settings.GOOGLE_OAUTH_SCOPE,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }

    if (
        settings.MICROSOFT_CLIENT_ID
        and settings.MICROSOFT_CLIENT_SECRET
        and settings.MICROSOFT_CLIENT_TENANT_ID
    ):
        OAUTH_PROVIDERS["microsoft"] = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "server_metadata_url": f"https://login.microsoftonline.com/{settings.MICROSOFT_CLIENT_TENANT_ID}/v2.0/.well-known/openid-configuration",
            "scope": settings.MICROSOFT_OAUTH_SCOPE,
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        }

    if (
        settings.OAUTH_CLIENT_ID
        and settings.OAUTH_CLIENT_SECRET
        and settings.OPENID_PROVIDER_URL
    ):
        OAUTH_PROVIDERS["oidc"] = {
            "client_id": settings.OAUTH_CLIENT_ID,
            "client_secret": settings.OAUTH_CLIENT_SECRET,
            "server_metadata_url": settings.OPENID_PROVIDER_URL,
            "scope": settings.OAUTH_SCOPES,
            "name": settings.OAUTH_PROVIDER_NAME,
            "redirect_uri": settings.OPENID_REDIRECT_URI,
        }

        # TODO: does this work out of the box for google and microsoft, too?
        if settings.OAUTH_USE_PKCE:
            OAUTH_PROVIDERS["oidc"]["pkce"] = settings.OAUTH_USE_PKCE


load_oauth_providers()
