#!/usr/bin/env bash
# Full pipeline. Validate first — a malformed entry makes everything after it
# meaningless — then the falsification loop, then the exporters.
#
# falsify.py deliberately exits 0 when hypotheses are falsified: that is the
# loop working, not a build failure. Pass --strict if you want the opposite.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 src/validate.py
python3 src/falsify.py "$@"
python3 src/prove.py
python3 src/build_graph.py
python3 src/render_timeline.py
