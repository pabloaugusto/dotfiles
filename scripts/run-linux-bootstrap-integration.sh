#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
IMAGE_TAG="${IMAGE_TAG:-dotfiles-bootstrap-linux-harness:local}"

docker build \
  --file "$REPO_ROOT/docker/bootstrap-linux-harness.Dockerfile" \
  --tag "$IMAGE_TAG" \
  "$REPO_ROOT"

docker run --rm "$IMAGE_TAG"
