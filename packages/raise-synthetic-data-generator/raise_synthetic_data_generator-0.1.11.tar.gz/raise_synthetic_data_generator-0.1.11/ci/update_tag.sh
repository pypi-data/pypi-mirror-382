#!/bin/sh

set -e

# Install git if neccesary
if ! command -v git >/dev/null 2>&1; then
  apk add --no-cache git >/dev/null
fi

apk add --no-cache git
git fetch --prune --tags --force

# Obtain last tag
LATEST_TAG="$(git tag -l | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n1)"

if [ -z "$LATEST_TAG" ]; then
  MAJOR=0; MINOR=0; PATCH=0
  echo "No version tags found. Starting from 0.0.0"
else
  MAJOR="$(echo "$LATEST_TAG" | cut -d. -f1)"
  MINOR="$(echo "$LATEST_TAG" | cut -d. -f2)"
  PATCH="$(echo "$LATEST_TAG" | cut -d. -f3)"
  echo "Latest tag: $LATEST_TAG  ->  $MAJOR.$MINOR.$PATCH"
fi

# Decide bump based on commit message
COMMIT_MSG="${CI_COMMIT_MESSAGE:-}"
if echo "$COMMIT_MSG" | grep -q '\[MAJOR\]'; then
  MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0
  BUMP="major"
elif echo "$COMMIT_MSG" | grep -q '\[MINOR\]'; then
  MINOR=$((MINOR + 1)); PATCH=0
  BUMP="minor"
else
  PATCH=$((PATCH + 1))
  BUMP="patch"
fi

NEW_TAG="${MAJOR}.${MINOR}.${PATCH}"
echo "Bump: $BUMP  ->  New tag: $NEW_TAG"

git tag -d "$NEW_TAG" 2>/dev/null || true

echo "New version: $NEW_TAG"
echo "$NEW_TAG" > version.txt

git config user.name "$CI_USER"
git config user.email "$CI_EMAIL"

git tag -a "$NEW_TAG" -m "Release $NEW_TAG"
git remote set-url origin https://oauth2:$CI_REPOSITORY_TOKEN@$CI_REPOSITORY_PATH
git remote -v

echo "CI_PUSH_USER: $CI_USER"
echo "CI_PUSH_TOKEN (First 5 chars): ${CI_REPOSITORY_TOKEN:0:5}"

git push origin "$NEW_TAG"

echo "Tag pushed: $NEW_TAG"
