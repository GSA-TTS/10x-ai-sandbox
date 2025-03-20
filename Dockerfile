## syntax=docker/dockerfile:1
# ##############################################################################
# ###               1) FRONTEND BUILD (Node)                                 ###
# ##############################################################################
FROM node:22.14.0-alpine3.21 AS build-frontend

COPY z-root-public.pem /usr/local/share/ca-certificates/z-root-public.pem
# RUN apt-get update && \
#     apt-get install -y ca-certificates && \
#     update-ca-certificates

WORKDIR /app
COPY package.json package-lock.json ./
RUN NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/z-root-public.pem npm ci

COPY . .
ENV APP_BUILD_HASH=dev-build
ENV NODE_OPTIONS=--max-old-space-size=4096
ARG PUBLIC_DATADOG_APP_ID
ARG PUBLIC_DATADOG_CLIENT_TOKEN
ARG PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN
ARG PUBLIC_DATADOG_SERVICE

ENV PUBLIC_DATADOG_APP_ID=${PUBLIC_DATADOG_APP_ID}
ENV PUBLIC_DATADOG_CLIENT_TOKEN=${PUBLIC_DATADOG_CLIENT_TOKEN}
ENV PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN=${PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN}
ENV PUBLIC_DATADOG_SERVICE=${PUBLIC_DATADOG_SERVICE}

RUN echo "PUBLIC_DATADOG_APP_ID=${PUBLIC_DATADOG_APP_ID}"
RUN echo "PUBLIC_DATADOG_CLIENT_TOKEN=${PUBLIC_DATADOG_CLIENT_TOKEN}"
RUN echo "PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN=${PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN}"
RUN echo "PUBLIC_DATADOG_SERVICE=${PUBLIC_DATADOG_SERVICE}"

RUN npm run build

# ##############################################################################
# ###               2) PYTHON DEPENDENCIES BUILDER STAGE                     ###
# ##############################################################################
FROM gsai-jammy-builder AS builder

ARG USE_CUDA=false
ARG USE_OLLAMA=false
ARG USE_CUDA_VER=cu121
ARG USE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG USE_RERANKING_MODEL=""
ARG TIKTOKEN_ENCODING_NAME="cl100k_base"
ARG UID=0
ARG GID=0

ENV ENV=prod \
    PORT=8080 \
    USE_OLLAMA_DOCKER=${USE_OLLAMA} \
    USE_CUDA_DOCKER=${USE_CUDA} \
    USE_CUDA_DOCKER_VER=${USE_CUDA_VER} \
    USE_EMBEDDING_MODEL_DOCKER=${USE_EMBEDDING_MODEL} \
    USE_RERANKING_MODEL_DOCKER=${USE_RERANKING_MODEL} \
    OLLAMA_BASE_URL="/ollama" \
    OPENAI_API_BASE_URL="" \
    OPENAI_API_KEY="" \
    WEBUI_SECRET_KEY="" \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false \
    WHISPER_MODEL="base" \
    WHISPER_MODEL_DIR="/app/backend/data/cache/whisper/models" \
    RAG_EMBEDDING_MODEL="$USE_EMBEDDING_MODEL_DOCKER" \
    RAG_RERANKING_MODEL="$USE_RERANKING_MODEL_DOCKER" \
    SENTENCE_TRANSFORMERS_HOME="/app/backend/data/cache/embedding/models" \
    TIKTOKEN_ENCODING_NAME="$TIKTOKEN_ENCODING_NAME" \
    TIKTOKEN_CACHE_DIR="/app/backend/data/cache/tiktoken" \
    HF_HOME="/app/backend/data/cache/embedding/models" \
    HOME=/root

COPY ./backend/requirements.txt ./requirements.txt
RUN uv pip install --system -r requirements.txt --no-cache-dir

# We should move these python fixes to the builder *might* need pip upgrade in final
RUN uv pip install --upgrade --system pillow==10.3.0
RUN uv pip install --upgrade --system setuptools==70.0.0
RUN uv pip install --upgrade --system posthog==3.11.0
RUN uv pip install --upgrade --system starlette==0.40.0
RUN uv pip uninstall --system flask
RUN uv pip uninstall --system Jinja2
RUN uv pip uninstall --system python-jose
RUN uv pip uninstall --system ecdsa

# ----------------------------------------------------
# 3. (Optional) Pre-download / cache large models
#    so they’re already present in the builder layer.
# ----------------------------------------------------

# RUN python -c "import os; \
#     from sentence_transformers import SentenceTransformer; \
#     SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')" && \
RUN python -c "import os; \
    from faster_whisper import WhisperModel; \
    WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])" 
# python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"

# ##############################################################################
# ###               3) FINAL RUNTIME IMAGE                                   ###
# ##############################################################################
FROM gsai-jammy-final AS final

## We re-declare our ARGs/ENVs as needed
ARG USE_CUDA=false
ARG USE_OLLAMA=false
ARG USE_CUDA_VER
ARG USE_EMBEDDING_MODEL
ARG USE_RERANKING_MODEL
ARG UID=0
ARG GID=0
ARG BUILD_HASH=dev-build

# Minimal runtime environment variables
ENV ENV=prod \
    PORT=8080 \
    USE_OLLAMA_DOCKER=${USE_OLLAMA} \
    USE_CUDA_DOCKER=${USE_CUDA} \
    USE_CUDA_DOCKER_VER=${USE_CUDA_VER} \
    USE_EMBEDDING_MODEL_DOCKER=${USE_EMBEDDING_MODEL} \
    USE_RERANKING_MODEL_DOCKER=${USE_RERANKING_MODEL} \
    HOME=/root \
    RAG_EMBEDDING_ENGINE=openai \
    WEBUI_BUILD_VERSION=${BUILD_HASH} \
    DOCKER=true

WORKDIR /app

# (Optional) If you run as non-root
RUN if [ $UID -ne 0 ]; then \
    if [ $GID -ne 0 ]; then \
    addgroup --gid $GID app; \
    fi; \
    adduser --uid $UID --gid $GID --home $HOME --disabled-password --no-create-home app; \
    fi

# ----------------------------------------------------
# 1. Copy only what we need from builder
# ----------------------------------------------------

COPY --from=builder /usr/local/lib/python3.11/dist-packages \
    /usr/local/lib/python3.11/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/backend/data/cache/whisper/models /app/backend/data/cache/whisper/models
RUN ln -sf /usr/bin/python3.11 /usr/bin/python

# # Copy any caches or model downloads you want at runtime
# COPY --from=builder /root/.cache /root/.cache

# Make sure the user has ownership if you’re using non-root
RUN chown -R $UID:$GID /app /root

# ----------------------------------------------------
# 2. Copy in your built frontend
# ----------------------------------------------------
COPY --from=build-frontend /app/build /app/build
COPY --from=build-frontend /app/.svelte-kit /app/.svelte-kit
COPY --from=build-frontend /app/CHANGELOG.md /app/CHANGELOG.md
COPY --from=build-frontend /app/package.json /app/package.json

# ----------------------------------------------------
# 3. Copy in your backend source code
# ----------------------------------------------------
COPY --chown=$UID:$GID ./backend /app/backend
COPY --chown=$UID:$GID ./start.sh /app/start.sh

# Ensure the user owns the /app directory
RUN chown -R $UID:$GID /app

EXPOSE 8080

## Healthcheck
HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health \
    | jq -ne 'input.status == true' || exit 1

USER $UID:$GID

# Ensure start.sh is executable
RUN chmod +x /app/start.sh

# local
CMD ["bash", "-c", "./start.sh && tail -f /dev/null"]

# remote
# CMD ["nohup", "ddtrace-run", "./start.sh", "&", "sleep", "infinity"]
