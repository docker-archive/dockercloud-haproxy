#!/bin/sh

set -e

echo ======================== Unit Test ==========================
pip install -r requirements.txt
pip install -r test-requirements.txt
python setup.py install
nosetests -v --with-coverage --cover-package haproxy

if [ "$(uname -s)" != "Darwin" ]; then
    echo ==================== Integration Test on Legacy links =======================
    tests/test_legacy_links.sh
fi
