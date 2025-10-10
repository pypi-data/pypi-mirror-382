#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import sys
from hwscan.scanner import run_all_detectors
from hwscan.__about__ import __version__

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="hwscan",
        description="Hardware detector for common USB serial/debug devices."
    )
    parser.add_argument("-j", "--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--errors", action="store_true", help="Print detector errors to stderr.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    results, errors = run_all_detectors()
    if args.pretty:
        print(json.dumps(results, indent=2, sort_keys=False))
    else:
        print(json.dumps(results, separators=(",", ":"), sort_keys=False))

    if args.errors and errors:
        print("\n# Detector errors:", file=sys.stderr)
        for mod, msg in errors.items():
            print(f"- {mod}: {msg}", file=sys.stderr)

if __name__ == "__main__":
    main()
