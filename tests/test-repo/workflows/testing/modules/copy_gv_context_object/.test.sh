#!/usr/bin/env bash

rm -rf results/out logs
snakemake --cores 1 --configfile=config/.test.yaml _test
