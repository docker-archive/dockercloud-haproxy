#!/bin/sh

set -e

echo ======================== Unit Test ==========================
python setup.py install
python setup.py test


if [ "$(uname -s)" != "Darwin" ]; then
    echo ==================== Integration Test =======================
    tests/integration_test.sh
fi