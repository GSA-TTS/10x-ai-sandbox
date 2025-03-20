# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS builder

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
    python3.11 \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgcrypt20-dev \
    libgpg-error-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY z-root-public.crt /usr/local/share/ca-certificates/z-root-public.crt

RUN update-ca-certificates

RUN python3 --version
RUN python3.11 --version

RUN ln -sf /usr/bin/python3.11 /usr/bin/python


# ----------------------------------------------------
# 2. Install Python dependencies in builder
# ----------------------------------------------------

# EITHER: just pip install into the base environment
# OR: create a virtualenv to copy into final
#
# For better isolation, many folks do:
#     RUN python -m venv /venv
#     ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip==23.3
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir uv pip==23.3