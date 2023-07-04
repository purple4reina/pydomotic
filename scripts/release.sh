#!/bin/bash -e

CURRENT_VERSION=$(cat pydomotic/version.py | awk '{print $3}')
echo "current version is ${CURRENT_VERSION}"

if [[ -z $VERSION ]]; then
    echo "VERSION must be set, ex: VERSION=\"0.2.0\" ./scripts/release.sh"
    exit 1
fi

echo "updating version to \"${VERSION}\""
echo "version = \"${VERSION}\"" > pydomotic/version.py

rm -rf dist

echo "committing changes"
git add pydomotic/version.py
git cm -m "Updating version to ${VERSION}"
git push
git tag "v${VERSION}"
git push --tags

echo packaging
python3 setup.py sdist

echo "installing twine"
pip3 install twine

echo "uploading to PyPI"
twine upload dist/*

echo "Creating new release in github"
echo "Release title: v${VERSION}"
open https://github.com/purple4reina/pydomotic/releases/new
