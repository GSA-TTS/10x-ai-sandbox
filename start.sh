#!/bin/sh

# Start the ollama server
# ollama serve &

# Start the application
printenv
./backend/open-webui-pipelines/start.sh &
./backend/start.sh &

# Wait for all background processes to exit
wait
