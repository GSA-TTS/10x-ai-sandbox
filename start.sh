#!/bin/sh

# Start the ollama server
ollama serve &

# Start the application
./backend/start.sh &

# Wait for all background processes to exit
wait