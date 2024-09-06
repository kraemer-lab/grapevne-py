#!/usr/bin/env bash

set -e

# Check that the script is called from the parent ('grapevne-py') folder
script_dir=$(dirname "$(realpath "$BASH_SOURCE")")
parent_dir=$(dirname "$script_dir")
current_dir=$(pwd)
if [ "$current_dir" != "$parent_dir" ]; then
    echo "This script must be run from the parent folder of the script's directory."
    echo "Please navigate to $parent_dir and run the script again."
    exit 1
fi

docker build \
    --file tests/Dockerfile_Snakemake8 \
    --no-cache \
    -t snakemake8 .
docker run \
    --rm -t snakemake8
