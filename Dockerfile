## syntax=docker/dockerfile:1
# ##############################################################################
# ###               1) FRONTEND BUILD (Node)                                 ###
# ##############################################################################
FROM node:22.14.0-alpine3.21 AS build-frontend

# COPY z-root-public.crt /usr/local/share/ca-certificates/z-root-public.crt
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

ARG PUBLIC_DATADOG_APP_ID=1570fdb1-4af6-40bd-8afc-33962f7e4f75
ARG PUBLIC_DATADOG_CLIENT_TOKEN=pub4943adb8fbab823c0b0d2c75a8100771
ARG PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN=pub010cb3969c15a90f52d688046cb62a8e
ARG PUBLIC_DATADOG_SERVICE=gsai_rum

ENV PUBLIC_DATADOG_APP_ID=$PUBLIC_DATADOG_APP_ID
ENV PUBLIC_DATADOG_CLIENT_TOKEN=$PUBLIC_DATADOG_CLIENT_TOKEN
ENV PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN=$PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN
ENV PUBLIC_DATADOG_SERVICE=$PUBLIC_DATADOG_SERVICE

RUN echo "PUBLIC_DATADOG_APP_ID=${PUBLIC_DATADOG_APP_ID}"
RUN echo "PUBLIC_DATADOG_CLIENT_TOKEN=${PUBLIC_DATADOG_CLIENT_TOKEN}"
RUN echo "PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN=${PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN}"
RUN echo "PUBLIC_DATADOG_SERVICE=${PUBLIC_DATADOG_SERVICE}"

RUN npm run build

# ##############################################################################
# ###               2) PYTHON DEPENDENCIES BUILDER STAGE                     ###
# ##############################################################################
FROM jimmoffetgsa/gsai:jammy-builder-32325 AS builder

ENV ENV=prod \
    HOME=/root

COPY ./pyproject.toml ./uv.lock ./
RUN uv pip uninstall --system setuptools && \
    uv pip install --upgrade --system setuptools==70.0.0
RUN uv sync --system --no-cache

RUN uv pip install --upgrade --system pillow==10.3.0
RUN uv pip install --upgrade --system posthog==3.11.0
RUN uv pip install --upgrade --system starlette==0.40.0
RUN uv pip uninstall --system flask
RUN uv pip uninstall --system Jinja2
RUN uv pip uninstall --system python-jose
RUN uv pip uninstall --system ecdsa

# ----------------------------------------------------
# (Optional) Pre-download / cache large models
#    so they’re already present in the builder layer.
# ----------------------------------------------------

# RUN python -c "import os; \
#     from sentence_transformers import SentenceTransformer; \
#     SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')" && \
# RUN python -c "import os; \
#     from faster_whisper import WhisperModel; \
#     WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])"
# python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"

# ##############################################################################
# ###               3) FINAL RUNTIME IMAGE                                   ###
# ##############################################################################
FROM jimmoffetgsa/gsai:jammy-final-32325 AS final

# ----------------------------------------------------
# 1. Copy only what we need from builder
# ----------------------------------------------------

ARG UID=0
ARG GID=0

COPY --from=builder /usr/local/lib/python3.11/dist-packages \
    /usr/local/lib/python3.11/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# COPY --from=builder /app/backend/data/cache/whisper/models /app/backend/data/cache/whisper/models
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

# EXPOSE 8081

# Healthcheck
HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health \
    | jq -ne 'input.status == true' || exit 1

USER $UID:$GID

# Ensure start.sh is executable
RUN chmod +x /app/start.sh

# local
CMD ["bash", "-c", "./start.sh && tail -f /dev/null"]
