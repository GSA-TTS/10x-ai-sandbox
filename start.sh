#!/bin/sh

./backend/open_webui_pipelines/start.sh &
./backend/cohere_proxy/start.sh &
./backend/start.sh &

wait
