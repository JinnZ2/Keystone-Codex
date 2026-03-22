#!/usr/bin/env python3
"""
Unified CLI for Keystone-Codex.

Usage:
    python3 -m src <command> [options]

Commands:
    validate          Validate all data entries against the schema
    score             Score entries and generate proof reports
    graph             Build dependency graph (graph.json + graph.dot)
    timeline          Render markdown timeline sorted by era
    query             Query/filter entries by domain, score, region, era
    analyze           Cross-entry analysis (coverage, gaps, shared evidence)
    new               Scaffold a new keystone entry template
    all               Run full pipeline (validate → score → graph → timeline)
"""
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def usage():
    print(__doc__.strip())
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        usage()

    cmd = sys.argv[1]

    if cmd == "validate":
        from src.validate import main as run
        run()
    elif cmd == "score":
        from src.prove import main as run
        run()
    elif cmd == "graph":
        from src.build_graph import main as run
        run()
    elif cmd == "timeline":
        from src.render_timeline import main as run
        run()
    elif cmd == "query":
        from src.query import main as run
        run()
    elif cmd == "analyze":
        from src.analyze import main as run
        run()
    elif cmd == "new":
        from src.scaffold import main as run
        run()
    elif cmd == "all":
        from src.validate import run as validate
        from src.prove import main as score
        from src.build_graph import main as graph
        from src.render_timeline import main as timeline
        if not validate():
            print("Validation failed. Aborting pipeline.")
            sys.exit(1)
        score()
        graph()
        timeline()
    else:
        print(f"Unknown command: {cmd}")
        usage()

if __name__ == "__main__":
    main()
