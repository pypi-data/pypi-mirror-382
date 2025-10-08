#!/usr/bin/env python3
"""
djinspect CLI entrypoint.
Usage:
  djinspect <command> [--filter kw] [--json] [--export path]
"""

import argparse
import importlib
import sys

def main(argv=None):
    parser = argparse.ArgumentParser(prog="djinspect", description="Inspect Django settings (standalone).")
    parser.add_argument("command", help="Command name (all, db, core, etc.)")
    parser.add_argument("--filter", "-f", help="Filter keyword", default=None)
    parser.add_argument("--json", help="Output JSON", action="store_true")
    parser.add_argument("--export", help="Export to file", default=None)
    args = parser.parse_args(argv)

    cmd_name = args.command
    try:
        mod = importlib.import_module(f"django_settings_inspector.management.commands.{cmd_name}")
    except ModuleNotFoundError:
        print(f"Unknown command: {cmd_name}")
        sys.exit(2)

    if not hasattr(mod, "Command"):
        print(f"Command module {cmd_name} has no Command class.")
        sys.exit(2)

    Command = getattr(mod, "Command")
    cmd = Command()
    # call handle with options dictionary
    options = {"filter": args.filter, "json": args.json, "export": args.export}
    try:
        cmd.handle(**options)
    except TypeError:
        # Some handles may expect (*args, **options) signature
        cmd.handle(*(), **options)

if __name__ == "__main__":
    main()
