#!/usr/bin/env bash
# Push current HEAD to GitHub (origin) and GitLab DR mirror (gitlab).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
git push origin HEAD
git push gitlab HEAD
echo "PASS: pushed to origin and gitlab"
