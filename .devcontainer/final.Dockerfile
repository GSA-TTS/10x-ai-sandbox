# syntax=docker/dockerfile:1
# ##############################################################################
# ###               1) FRONTEND BUILD (Node)                                 ###
# ##############################################################################
FROM node:22-bookworm-slim AS build-frontend

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ENV APP_BUILD_HASH=dev-build
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN npm run build

# ##############################################################################
# ###               2) PYTHON DEPENDENCIES BUILDER STAGE                     ###
# ##############################################################################
FROM jimmoffetgsa/gsai:bookworm-builder-011525 AS builder

# ##############################################################################
# ###               3) FINAL RUNTIME IMAGE                                   ###
# ##############################################################################
FROM python:3.11-slim-bookworm AS final

# 2) Add the Debian testing (or unstable) repo to sources.list
RUN echo "deb http://deb.debian.org/debian testing main" >> /etc/apt/sources.list

# 3) Pin the zlib1g package so that only it (and its dependencies) can come from testing
RUN echo "Package: zlib1g\nPin: release a=testing\nPin-Priority: 900\n\nPackage: *\nPin: release a=testing\nPin-Priority: 100" \
    > /etc/apt/preferences.d/zlib1g

# 4) Now install zlib1g from testing
RUN apt-get update \
    && apt-get install -y --no-install-recommends zlib1g \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Remove the testing source line if you don't want to keep it
RUN sed -i '/testing main/d' /etc/apt/sources.list \
    && rm -f /etc/apt/preferences.d/zlib1g

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
COPY --from=builder /usr/local/lib/python3.11/site-packages \
    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

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

# Healthcheck
HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health \
    | jq -ne 'input.status == true' || exit 1


USER $UID:$GID

# Ensure start.sh is executable
RUN chmod +x /app/start.sh

# local
CMD ["bash", "-c", "./start.sh && tail -f /dev/null"]

# remote
# CMD ["nohup", "ddtrace-run", "./start.sh", "&", "sleep", "infinity"]
