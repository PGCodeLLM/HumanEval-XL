#!/bin/bash

echo "Building HumanEval-XL Docker image..."

# Build the Docker image
docker build -t humaneval-xl:latest .

if [ $? -eq 0 ]; then
    echo "Docker image built successfully: humaneval-xl:latest"
else
    echo "Docker build failed!"
    exit 1
fi

echo "Docker image ready for use."