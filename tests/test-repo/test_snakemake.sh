#!/usr/bin/env bash

set -eoux pipefail

# Run tests from the script folder
cd "$(dirname "$0")"

# ########################################################
# Test individual workflows
# ########################################################

# Minimalist init(), input(), output() and params() testing
echo "Test: sources/touch"
pushd workflows/testing/sources/touch
./.test.sh
popd

# Test script(), resource(), log()
echo "Test: modules/copy"
pushd workflows/testing/modules/copy
./.test.sh
popd

# Indexing multiple input ports
echo "Test: modules/concat"
pushd workflows/testing/modules/concat
./.test.sh
popd

# Test Helper as object instance
echo "Test: modules/copy_gv_object"
pushd workflows/testing/modules/copy_gv_object
./.test.sh
popd

# Test Helper as namespace import
echo "Test: modules/copy_gv_namespace"
pushd workflows/testing/modules/copy_gv_namespace
./.test.sh
popd

# Test Helper as context manager
echo "Test: modules/copy_gv_context"
pushd workflows/testing/modules/copy_gv_context
./.test.sh
popd

# ########################################################
# Test composite workflows
# ########################################################

# Test combined workflows to ensure returned paths are module-specific
echo "Test: touch-copy"
pushd touch-copy
./.test.sh
popd
