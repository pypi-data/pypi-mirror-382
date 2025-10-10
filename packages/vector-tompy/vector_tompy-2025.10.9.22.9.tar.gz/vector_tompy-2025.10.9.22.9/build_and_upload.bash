#!/bin/bash

# Insert current date-time in pyproject.toml
current_datetime="$(date +"%Y.%m.%d.%H.%M")"
pyproject_version_new="version = \"${current_datetime}\""
pyproject_version_current="^version \= .*\$"
sed -i "s|${pyproject_version_current}|${pyproject_version_new}|" pyproject.toml

# Building
HATCH_BUILD_CLEAN=true python3 -m build

# Uploading
python3 -m twine upload dist/*
