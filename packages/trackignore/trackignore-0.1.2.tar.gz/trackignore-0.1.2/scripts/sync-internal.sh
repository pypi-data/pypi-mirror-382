#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper that delegates to the Python CLI.
# Environment variables map to CLI flags; explicit CLI arguments take precedence.

PRIVATE_REMOTE="${PRIVATE_REMOTE:-origin-private}"
PRIVATE_BRANCH="${PRIVATE_BRANCH:-main}"
PRIVATE_DIR="${PRIVATE_DIR:-__PRIVATE__}"

cmd=(trackignore sync --remote "${PRIVATE_REMOTE}" --branch "${PRIVATE_BRANCH}" --path "${PRIVATE_DIR}")
cmd+=("$@")

exec "${cmd[@]}"
