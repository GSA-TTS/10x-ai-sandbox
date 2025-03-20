# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS final

COPY z-root-public.crt /usr/local/share/ca-certificates/z-root-public.crt
RUN apt-get update && \
    apt-get install -y ca-certificates \
    curl \
    dnsutils \
    htop \
    less \
    net-tools \
    procps \
    vim \
    python3.11 \
    python3-pip \
    ffmpeg && \
    update-ca-certificates


