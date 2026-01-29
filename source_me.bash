#!/usr/bin/env bash
# Source this file to add the repo root to PYTHONPATH for local tools.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${PYTHONPATH:-}" ]; then
	export PYTHONPATH="${SCRIPT_DIR}"
else
	export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
fi
