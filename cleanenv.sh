#!/bin/bash

# Fully clean deps and rebuild to avoid conflicts with other branches

# clean node deps
nvm use 20.18.1
rm -rf node_modules
npm install --verbose

# clean python deps
rm -rf .venv
uv venv --seed
uv sync

npm run build
