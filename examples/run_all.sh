#!/usr/bin/env bash
python3 src/validate.py && python3 src/prove.py && python3 src/build_graph.py && python3 src/render_timeline.py
