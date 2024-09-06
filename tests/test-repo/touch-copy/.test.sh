#!/usr/bin/env bash

rm -rf results
snakemake --cores 1 copy_copy

test -f results/touch/touch
test -f results/copy/touch
