#!/bin/sh

set -e

echo ======================== Unit Test ==========================
python setup.py install
pip install -r test-requirements.txt
nosetests -v --with-coverage --cover-package haproxy

if [ "$(uname -s)" != "Darwin" ]; then
    echo ==================== Integration Test on Legacy links =======================
    tests/test_legacy_links.sh
fi
