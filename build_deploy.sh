#!/bin/bash
set -e

python3 -m pip install --user twine wheel
python3 setup.py bdist_wheel

# TODO: this fails if the package version alrdy exists
# We should check before uploading
python3 -m twine upload dist/* || true
