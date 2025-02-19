#!/bin/bash
set -e
set -x
# rye self update
rye sync
rye run isort loop.py
rye run black loop.py
rye run mypy --strict loop.py
git status
git --no-pager diff
git --no-pager diff --cached
git --no-pager whatchanged
repomix
rye run python loop.py
