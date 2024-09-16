#!/usr/bin/env bash

set -e

# Run scripts from the root directory
script_dir=$(dirname $0)
parent_dir=$(dirname $script_dir)
cd $parent_dir

# Update grapevne_helper.py script with current version
helper_scripts=$(find tests/test-repo -name grapevne_helper.py)
for helper_script in $helper_scripts; do
    cp tests/grapevne_helper.py $helper_script
done

# Run tests (outside of docker) - useful for CI matrix strategies
tests/test-repo/test_snakemake.sh
