#!/bin/bash
set -e
set -x
# rye self update
rye sync
rye run black loop.py
rye run mypy --strict loop.py
rye run python loop.py || true
git status
git --no-pager diff
repomix
