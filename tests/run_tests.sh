#!/usr/bin/env bash

set -e

# Run scripts from the root directory
script_dir=$(dirname $0)
parent_dir=$(dirname $script_dir)
cd $parent_dir

# Run tests (outside of docker) - useful for CI matrix strategies
tests/test-repo/test_snakemake.sh
