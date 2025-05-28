#!/usr/bin/env bash

./backend/open_webui_pipelines/dev.sh &
./backend/cohere_proxy/dev.sh &
./backend/dev.sh &

wait
