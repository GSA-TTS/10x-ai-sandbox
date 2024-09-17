FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Pyenv
ENV PYENV_ROOT=/usr/local/pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
RUN git clone https://github.com/pyenv/pyenv.git ${PYENV_ROOT} \
    && ${PYENV_ROOT}/bin/pyenv install 3.11 \
    && ${PYENV_ROOT}/bin/pyenv global 3.11
