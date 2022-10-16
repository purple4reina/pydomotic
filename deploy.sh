#!/bin/bash -e

rm -rf vendor

pip3 install -r requirements.txt -t vendor

# pycryptodome requires cross compilation of c-extensions
pip3 install \
    --platform manylinux2014_x86_64 \
    --target=vendor \
    --implementation cp \
    --python 3.9 \
    --only-binary=:all: \
    --no-cache-dir \
    --upgrade \
    pycryptodome==3.15.0

sls deploy
