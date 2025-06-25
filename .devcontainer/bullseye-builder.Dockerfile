# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye AS builder

# ---------------------- Build Args ----------------------
ARG USE_CUDA=false
ARG USE_OLLAMA=false
ARG USE_CUDA_VER=cu121
ARG USE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG USE_RERANKING_MODEL=""
ARG TIKTOKEN_ENCODING_NAME="cl100k_base"
ARG UID=0
ARG GID=0

# ---------------------- Environment Variables ----------------------
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

WORKDIR /app/backend

# (Optional) If you want to create a non-root user
RUN if [ $UID -ne 0 ]; then \
    if [ $GID -ne 0 ]; then \
    addgroup --gid $GID app; \
    fi; \
    adduser --uid $UID --gid $GID --home $HOME --disabled-password --no-create-home app; \
    fi

# ----------------------------------------------------
# 1. Install all OS-level build tools (in builder only)
#    If you truly do NOT need them at runtime, they won’t
#    be carried into the final image.
# ----------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    pandoc \
    gcc \
    netcat-openbsd \
    curl \
    jq \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgcrypt20-dev \
    libgpg-error-dev && \
    # If you only need ollama or CUDA in the builder, do it here
    # (Left commented for illustration)
    # if [ "$USE_OLLAMA" = "true" ]; then \
    #     curl -fsSL https://ollama.com/install.sh | sh; \
    # fi; \
    # Clean up apt caches
    rm -rf /var/lib/apt/lists/*

# Create any extra dirs, for example for .cache
# RUN mkdir -p $HOME/.cache/chroma && \
#     echo -n 00000000-0000-0000-0000-000000000000 > $HOME/.cache/chroma/telemetry_user_id

# ----------------------------------------------------
# 2. Install Python dependencies in builder
# ----------------------------------------------------
COPY ./pyproject.toml ./uv.lock ./

# EITHER: just pip install into the base environment
# OR: create a virtualenv to copy into final
#
# For better isolation, many folks do:
#     RUN python -m venv /venv
#     ENV PATH="/venv/bin:$PATH"
#

RUN pip install --upgrade pip==23.3

# We'll keep it simple here.
RUN if [ "$USE_CUDA" = "true" ]; then \
    pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/${USE_CUDA_VER}; \
    else \
    pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu; \
    fi
RUN pip install --no-cache-dir uv pip==23.3
RUN uv sync --system --no-cache

# ----------------------------------------------------
# 3. (Optional) Pre-download / cache large models
#    so they’re already present in the builder layer.
# ----------------------------------------------------
RUN python -c "import os; \
    from sentence_transformers import SentenceTransformer; \
    SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')" && \
    python -c "import os; \
    from faster_whisper import WhisperModel; \
    WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])" && \
    python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"

# If you have any local code that also gets compiled or processed, copy it here:
# COPY --chown=$UID:$GID ./backend /app/backend
# But we can wait until final stage to copy the code if you want to keep builder clean.

# We should move these python fixes to the builder *might* need pip upgrade in final
RUN uv pip install --upgrade --system pillow==10.3.0
RUN uv pip install --upgrade --system setuptools==70.0.0

RUN uv pip install --upgrade --system starlette==0.40.0
RUN uv pip uninstall --system flask
RUN uv pip uninstall --system Jinja2
RUN uv pip uninstall --system python-jose

# FROM jimmoffetgsa/gsai-bookworm-builder:latest AS builder

##############################################################################
###               3) FINAL RUNTIME IMAGE                                   ###
##############################################################################
FROM python:3.11-slim-bullseye AS final

# ARG DEBIAN_FRONTEND=noninteractive
# ENV TZ=America/New_York

# (Optional) Install pip for Python 3.11:
# RUN python3.11 -m ensurepip --upgrade

# We re-declare our ARGs/ENVs as needed
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
# Copy site-packages (Python libs) from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages \
    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# # Copy any caches or model downloads you want at runtime
# COPY --from=builder /root/.cache /root/.cache

# Make sure the user has ownership if you’re using non-root
RUN chown -R $UID:$GID /app /root

# # ----------------------------------------------------
# # 2. Copy in your built frontend
# # ----------------------------------------------------
# COPY --from=build-frontend /app/build /app/build
# COPY --from=build-frontend /app/.svelte-kit /app/.svelte-kit
# COPY --from=build-frontend /app/CHANGELOG.md /app/CHANGELOG.md
# COPY --from=build-frontend /app/package.json /app/package.json

# # ----------------------------------------------------
# # 3. Copy in your backend source code
# # ----------------------------------------------------
# COPY --chown=$UID:$GID ./backend /app/backend
# COPY --chown=$UID:$GID ./start.sh /app/start.sh

# # Ensure the user owns the /app directory
# RUN chown -R $UID:$GID /app

# EXPOSE 8080

# # Healthcheck
# HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health \
#     | jq -ne 'input.status == true' || exit 1


# USER $UID:$GID

# # Ensure start.sh is executable
# RUN chmod +x /app/start.sh

# # local
# # CMD ["bash", "-c", "./start.sh && tail -f /dev/null"]

# # remote
# CMD ["nohup", "ddtrace-run", "./start.sh", "&", "sleep", "infinity"]
