FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu

# Install pyenv dependencies
RUN apt-get update && apt-get install -y \
    make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# Install pyenv
RUN curl https://pyenv.run | bash

# Add pyenv to bashrc
RUN echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /root/.bashrc
RUN echo 'eval "$(pyenv init --path)"' >> /root/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> /root/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc