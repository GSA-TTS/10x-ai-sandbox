import json

from sqlalchemy import Column, Integer, JSON, DateTime, func

from open_webui.internal.db import Base, get_db
from open_webui.env import log


# TODO: Remove this module after config has been moved to Redis


path_name_mapping = {
    "auth.api_key.enable": "ENABLE_API_KEY",  # pragma: allowlist secret
    "auth.api_key.endpoint_restrictions": "ENABLE_API_KEY_ENDPOINT_RESTRICTIONS",
    "auth.api_key.allowed_endpoints": "API_KEY_ALLOWED_ENDPOINTS",
    "auth.jwt_expiry": "JWT_EXPIRES_IN",
    "oauth.enable_signup": "ENABLE_OAUTH_SIGNUP",
    "oauth.merge_accounts_by_email": "OAUTH_MERGE_ACCOUNTS_BY_EMAIL",
    "oauth.google.client_id": "GOOGLE_CLIENT_ID",
    "oauth.google.client_secret": "GOOGLE_CLIENT_SECRET",  # pragma: allowlist secret
    "oauth.google.scope": "GOOGLE_OAUTH_SCOPE",
    "oauth.google.redirect_uri": "GOOGLE_REDIRECT_URI",
    "oauth.microsoft.client_id": "MICROSOFT_CLIENT_ID",
    "oauth.microsoft.client_secret": "MICROSOFT_CLIENT_SECRET",  # pragma: allowlist secret
    "oauth.microsoft.tenant_id": "MICROSOFT_CLIENT_TENANT_ID",
    "oauth.microsoft.scope": "MICROSOFT_OAUTH_SCOPE",
    "oauth.microsoft.redirect_uri": "MICROSOFT_REDIRECT_URI",
    "oauth.oidc.client_id": "OAUTH_CLIENT_ID",
    "oauth.oidc.client_secret": "OAUTH_CLIENT_SECRET",  # pragma: allowlist secret
    "oauth.oidc.provider_url": "OPENID_PROVIDER_URL",
    "oauth.oidc.redirect_uri": "OPENID_REDIRECT_URI",
    "oauth.oidc.scopes": "OAUTH_SCOPES",
    "oauth.oidc.provider_name": "OAUTH_PROVIDER_NAME",
    "oauth.oidc.username_claim": "OAUTH_USERNAME_CLAIM",
    "oauth.oidc.avatar_claim": "OAUTH_PICTURE_CLAIM",
    "oauth.oidc.email_claim": "OAUTH_EMAIL_CLAIM",
    "oauth.oidc.group_claim": "OAUTH_GROUPS_CLAIM",
    "oauth.enable_role_mapping": "ENABLE_OAUTH_ROLE_MANAGEMENT",
    "oauth.enable_group_mapping": "ENABLE_OAUTH_GROUP_MANAGEMENT",
    "oauth.roles_claim": "OAUTH_ROLES_CLAIM",
    "oauth.allowed_roles": "OAUTH_ALLOWED_ROLES",
    "oauth.admin_roles": "OAUTH_ADMIN_ROLES",
    "oauth.oidc.acr_claim": "OAUTH_ACR_CLAIM",
    "oauth.oidc.nonce_claim": "OAUTH_NONCE_CLAIM",
    "oauth.oidc.use_pkce": "OAUTH_USE_PKCE",
    "oauth.allowed_domains": "OAUTH_ALLOWED_DOMAINS",
    "ollama.enable": "ENABLE_OLLAMA_API",
    "ollama.base_urls": "OLLAMA_BASE_URLS",
    "ollama.api_configs": "OLLAMA_API_CONFIGS",
    "openai.enable": "ENABLE_OPENAI_API",
    "openai.api_keys": "OPENAI_API_KEYS",  # pragma: allowlist secret
    "openai.api_base_urls": "OPENAI_API_BASE_URLS",
    "openai.api_configs": "OPENAI_API_CONFIGS",
    "webui.url": "WEBUI_URL",
    "ui.enable_signup": "ENABLE_SIGNUP",
    "ui.ENABLE_LOGIN_FORM": "ENABLE_LOGIN_FORM",
    "ui.default_locale": "DEFAULT_LOCALE",
    "ui.default_models": "DEFAULT_MODELS",
    "ui.prompt_suggestions": "DEFAULT_PROMPT_SUGGESTIONS",
    "ui.model_order_list": "MODEL_ORDER_LIST",
    "ui.default_user_role": "DEFAULT_USER_ROLE",
    "user.permissions": "USER_PERMISSIONS",
    "channels.enable": "ENABLE_CHANNELS",
    "evaluation.arena.enable": "ENABLE_EVALUATION_ARENA_MODELS",
    "evaluation.arena.models": "EVALUATION_ARENA_MODELS",
    "webhook_url": "WEBHOOK_URL",
    "ui.enable_community_sharing": "ENABLE_COMMUNITY_SHARING",
    "ui.enable_message_rating": "ENABLE_MESSAGE_RATING",
    "ui.banners": "WEBUI_BANNERS",
    "auth.admin.show": "SHOW_ADMIN_DETAILS",
    "auth.admin.email": "ADMIN_EMAIL",
    "task.model.default": "TASK_MODEL",
    "task.model.external": "TASK_MODEL_EXTERNAL",
    "task.title.prompt_template": "TITLE_GENERATION_PROMPT_TEMPLATE",
    "task.tags.prompt_template": "TAGS_GENERATION_PROMPT_TEMPLATE",
    "task.tags.enable": "ENABLE_TAGS_GENERATION",
    "task.query.search.enable": "ENABLE_SEARCH_QUERY_GENERATION",
    "task.query.retrieval.enable": "ENABLE_RETRIEVAL_QUERY_GENERATION",
    "task.query.prompt_template": "QUERY_GENERATION_PROMPT_TEMPLATE",
    "task.autocomplete.enable": "ENABLE_AUTOCOMPLETE_GENERATION",
    "task.autocomplete.input_max_length": "AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH",
    "task.autocomplete.prompt_template": "AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE",
    "task.tools.prompt_template": "TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE",
    "google_drive.enable": "ENABLE_GOOGLE_DRIVE_INTEGRATION",
    "google_drive.client_id": "GOOGLE_DRIVE_CLIENT_ID",
    "google_drive.api_key": "GOOGLE_DRIVE_API_KEY",  # pragma: allowlist secret
    "rag.CONTENT_EXTRACTION_ENGINE": "CONTENT_EXTRACTION_ENGINE",
    "rag.tika_server_url": "TIKA_SERVER_URL",
    "rag.top_k": "RAG_TOP_K",
    "rag.relevance_threshold": "RAG_RELEVANCE_THRESHOLD",
    "rag.enable_hybrid_search": "ENABLE_RAG_HYBRID_SEARCH",
    "rag.file.max_count": "RAG_FILE_MAX_COUNT",
    "rag.file.max_size": "RAG_FILE_MAX_SIZE",
    "rag.enable_web_loader_ssl_verification": "ENABLE_RAG_WEB_LOADER_SSL_VERIFICATION",
    "rag.embedding_engine": "RAG_EMBEDDING_ENGINE",
    "rag.pdf_extract_images": "PDF_EXTRACT_IMAGES",
    "rag.embedding_model": "RAG_EMBEDDING_MODEL",
    "rag.embedding_batch_size": "RAG_EMBEDDING_BATCH_SIZE",
    "rag.reranking_model": "RAG_RERANKING_MODEL",
    "rag.text_splitter": "RAG_TEXT_SPLITTER",
    "rag.tiktoken_encoding_name": "TIKTOKEN_ENCODING_NAME",
    "rag.chunk_size": "CHUNK_SIZE",
    "rag.chunk_overlap": "CHUNK_OVERLAP",
    "rag.template": "RAG_TEMPLATE",
    "rag.openai_api_base_url": "RAG_OPENAI_API_BASE_URL",
    "rag.openai_api_key": "RAG_OPENAI_API_KEY",  # pragma: allowlist secret
    "rag.ollama.url": "RAG_OLLAMA_BASE_URL",
    "rag.ollama.key": "RAG_OLLAMA_API_KEY",  # pragma: allowlist secret
    "rag.youtube_loader_language": "YOUTUBE_LOADER_LANGUAGE",
    "rag.youtube_loader_proxy_url": "YOUTUBE_LOADER_PROXY_URL",
    "rag.web.search.enable": "ENABLE_RAG_WEB_SEARCH",
    "rag.web.search.engine": "RAG_WEB_SEARCH_ENGINE",
    "rag.web.search.searxng_query_url": "SEARXNG_QUERY_URL",
    "rag.web.search.google_pse_api_key": "GOOGLE_PSE_API_KEY",  # pragma: allowlist secret
    "rag.web.search.google_pse_engine_id": "GOOGLE_PSE_ENGINE_ID",
    "rag.web.search.brave_search_api_key": "BRAVE_SEARCH_API_KEY",  # pragma: allowlist secret
    "rag.web.search.kagi_search_api_key": "KAGI_SEARCH_API_KEY",  # pragma: allowlist secret
    "rag.web.search.mojeek_search_api_key": "MOJEEK_SEARCH_API_KEY",  # pragma: allowlist secret
    "rag.web.search.serpstack_api_key": "SERPSTACK_API_KEY",  # pragma: allowlist secret
    "rag.web.search.serpstack_https": "SERPSTACK_HTTPS",
    "rag.web.search.serper_api_key": "SERPER_API_KEY",  # pragma: allowlist secret
    "rag.web.search.serply_api_key": "SERPLY_API_KEY",  # pragma: allowlist secret
    "rag.web.search.tavily_api_key": "TAVILY_API_KEY",  # pragma: allowlist secret
    "rag.web.search.jina_api_key": "JINA_API_KEY",  # pragma: allowlist secret
    "rag.web.search.searchapi_api_key": "SEARCHAPI_API_KEY",  # pragma: allowlist secret
    "rag.web.search.searchapi_engine": "SEARCHAPI_ENGINE",
    "rag.web.search.bing_search_v7_endpoint": "BING_SEARCH_V7_ENDPOINT",
    "rag.web.search.bing_search_v7_subscription_key": "BING_SEARCH_V7_SUBSCRIPTION_KEY",  # pragma: allowlist secret
    "rag.web.search.result_count": "RAG_WEB_SEARCH_RESULT_COUNT",
    "rag.web.search.concurrent_requests": "RAG_WEB_SEARCH_CONCURRENT_REQUESTS",
    "image_generation.engine": "IMAGE_GENERATION_ENGINE",
    "image_generation.enable": "ENABLE_IMAGE_GENERATION",
    "image_generation.automatic1111.base_url": "AUTOMATIC1111_BASE_URL",
    "image_generation.automatic1111.api_auth": "AUTOMATIC1111_API_AUTH",
    "image_generation.automatic1111.cfg_scale": "AUTOMATIC1111_CFG_SCALE",
    "image_generation.automatic1111.sampler": "AUTOMATIC1111_SAMPLER",
    "image_generation.automatic1111.scheduler": "AUTOMATIC1111_SCHEDULER",
    "image_generation.comfyui.base_url": "COMFYUI_BASE_URL",
    "image_generation.comfyui.api_key": "COMFYUI_API_KEY",  # pragma: allowlist secret
    "image_generation.comfyui.workflow": "COMFYUI_WORKFLOW",
    "image_generation.comfyui.nodes": "COMFYUI_WORKFLOW_NODES",
    "image_generation.openai.api_base_url": "IMAGES_OPENAI_API_BASE_URL",
    "image_generation.openai.api_key": "IMAGES_OPENAI_API_KEY",  # pragma: allowlist secret
    "image_generation.size": "IMAGE_SIZE",
    "image_generation.steps": "IMAGE_STEPS",
    "image_generation.model": "IMAGE_GENERATION_MODEL",
    "audio.stt.whisper_model": "WHISPER_MODEL",
    "audio.stt.openai.api_base_url": "AUDIO_STT_OPENAI_API_BASE_URL",
    "audio.stt.openai.api_key": "AUDIO_STT_OPENAI_API_KEY",  # pragma: allowlist secret
    "audio.stt.engine": "AUDIO_STT_ENGINE",
    "audio.stt.model": "AUDIO_STT_MODEL",
    "audio.tts.openai.api_base_url": "AUDIO_TTS_OPENAI_API_BASE_URL",
    "audio.tts.openai.api_key": "AUDIO_TTS_OPENAI_API_KEY",  # pragma: allowlist secret
    "audio.tts.api_key": "AUDIO_TTS_API_KEY",  # pragma: allowlist secret
    "audio.tts.engine": "AUDIO_TTS_ENGINE",
    "audio.tts.model": "AUDIO_TTS_MODEL",
    "audio.tts.voice": "AUDIO_TTS_VOICE",
    "audio.tts.split_on": "AUDIO_TTS_SPLIT_ON",
    "audio.tts.azure.speech_region": "AUDIO_TTS_AZURE_SPEECH_REGION",
    "audio.tts.azure.speech_output_format": "AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT",
    "ldap.enable": "ENABLE_LDAP",
    "ldap.server.label": "LDAP_SERVER_LABEL",
    "ldap.server.host": "LDAP_SERVER_HOST",
    "ldap.server.port": "LDAP_SERVER_PORT",
    "ldap.server.attribute_for_username": "LDAP_ATTRIBUTE_FOR_USERNAME",
    "ldap.server.app_dn": "LDAP_APP_DN",
    "ldap.server.app_password": "LDAP_APP_PASSWORD",  # pragma: allowlist secret
    "ldap.server.users_dn": "LDAP_SEARCH_BASE",
    "ldap.server.search_filter": "LDAP_SEARCH_FILTERS",
    "ldap.server.use_tls": "LDAP_USE_TLS",
    "ldap.server.ca_cert_file": "LDAP_CA_CERT_FILE",
    "ldap.server.ciphers": "LDAP_CIPHERS",
}


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())


def flatten(d: dict, parent_key="", sep="."):
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def migrate_db_config(redis_client, hash_name):
    if redis_client.exists(hash_name):
        log.info("CONFIG MIGRATION: Config already exists in Redis, skipping migration")
        return

    log.info("CONFIG MIGRATION: No config found in Redis, migrating from database")
    with get_db() as db:
        db_config = db.query(Config).order_by(Config.id.desc()).first()
        if db_config:
            log.info(
                f"CONFIG MIGRATION: Migrating config from database to Redis: {db_config.data}"
            )
            flattened_config = flatten(db_config.data)
            for path, value in flattened_config.items():
                log.info(f"CONFIG MIGRATION: Config item: {path}={value}")
                if path in path_name_mapping:
                    redis_client.hset(
                        hash_name, path_name_mapping[path], json.dumps(value)
                    )
                else:
                    log.warning(f"CONFIG MIGRATION: Skipping unknown path: {path}")
        else:
            log.info("CONFIG MIGRATION: No config found in database, doing nothing")
    log.info("CONFIG MIGRATION: Config migration complete")
