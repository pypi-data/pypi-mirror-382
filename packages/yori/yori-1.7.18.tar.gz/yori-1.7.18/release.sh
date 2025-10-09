#!/bin/bash

# Create a release by creating a commit, tagging it, and pushing
set -e

if [[ -z $1 ]]; then
    echo "USAGE: $0 <major|minor|patch>"
    exit 1
fi

hatch version $1

readonly ver=$(hatch version)
if git tag -l | grep -E "^${ver}$" &> /dev/null; then
    echo "Whoops!! Tag for version ${ver} already exists"
    exit 1
fi

git add yori/__init__.py
git commit -am "bump version"
git tag -am "bump to ${ver}" ${ver}
git push --follow-tags
