#!/usr/bin/env python3
"""
search_settings.py
------------------
Search for Django settings.py (recursively) and extract ROOT_URLCONF.

Usage:
  python search_settings.py all
  python search_settings.py -f path/to/manage.py
  python search_settings.py -f path/to/settings.py
"""

import argparse
import importlib
import sys
import os
import re
from typing import ClassVar
from pathlib import Path

try:
    from rich_argparse import RichHelpFormatter, RawDescriptionRichHelpFormatter, _lazy_rich as rr
    from rich.syntax import Syntax
    class CustomRichHelpFormatter(RawDescriptionRichHelpFormatter):
        """A custom RichHelpFormatter with modified styles."""

        def __init__(self, prog, epilog=None, width=None, max_help_position=24, indent_increment=2):
            super().__init__(prog)
            if epilog is not None:
                self.epilog = epilog
            if width is not None:
                self.width = width
            self._max_help_position = max_help_position
            self._indent_increment = indent_increment
            
        styles: ClassVar[dict[str, rr.StyleType]] = {
            "argparse.args":  "bold #FFFF00",  # Changed from cyan
            "argparse.groups":  "#AA55FF",   # Changed from dark_orange
            "argparse.help":  "bold #00FFFF",    # Changed from default
            "argparse.metavar":  "bold #FF55FF", # Changed from dark_cyan
            "argparse.syntax":  "underline", # Changed from bold
            "argparse.text":  "white",   # Changed from default
            "argparse.prog":  "bold #00AAFF italic",     # Changed from grey50
            "argparse.default":  "bold", # Changed from italic
        }
        
        def format_help(self):
            help_text = super().format_help()
            # Add a newline in front of the usage if not there
            if not help_text.lstrip().startswith("Usage:"):
                # Cari posisi Usage
                idx = help_text.find("Usage:")
                if idx > 0:
                    help_text = help_text[:idx] + "\n" + help_text[idx:]
                elif idx == 0:
                    help_text = "\n" + help_text
            elif not help_text.startswith("\n"):
                help_text = "\n" + help_text
            return help_text
        
        def _rich_fill_text(self, text: rr.Text, width: int, indent: rr.Text) -> rr.Text:
            # Split per baris, pertahankan baris kosong
            lines = text.plain.splitlines()
            return rr.Text("\n").join(
                indent + rr.Text(line, style=text.style) for line in lines
            ) + "\n\n"
            
        def add_text(self, text):
            if text is argparse.SUPPRESS or text is None:
                return
            if isinstance(text, str):
                lines = text.strip().splitlines()
                indent = " " * getattr(self, "_current_indent", 2)
                if len(indent) < 2:
                    indent = " " * 2
                # Detection: If all rows are commands (python, $, or spaces), display all as syntax
                is_all_code = all(
                    l.strip().startswith(("python", "$")) or l.startswith("  ") for l in lines if l.strip()
                )
                # print(f"Detected all code: {is_all_code}, lines: {lines}")
                if len(lines) > 0 and (is_all_code or len(lines) > 1):
                    # If there is a title (the first line is not an order), display the title
                    if len(lines) > 1 and not (lines[0].strip().startswith(("python", "$")) or lines[0].startswith("  ")):
                        # print(f"Adding title: {lines[0]}")
                        self.add_renderable(rr.Text(lines[0], style="#007F74 bold"))
                        code_lines = lines[1:]
                    else:
                        # print("No title detected, using all lines as code.")
                        code_lines = lines
                    # Add indentation to all line code
                    code = "\n".join(f"{indent}{l.strip()}" for l in code_lines)
                    if code.strip():
                        self.add_renderable(
                            Syntax(code, "bash", theme="fruity", line_numbers=False)
                        )
                    return
                else:
                    text = rr.Text(text, style=self.styles["argparse.text"])
            super().add_text(text)

except:
    CustomRichHelpFormatter = argparse.RawTextHelpFormatter


try:
    from rich import print
    from rich.prompt import Prompt
except ImportError:
    print = print
    class Prompt:
        @staticmethod
        def ask(question, choices=None, default=None):
            print(question)
            if choices:
                for i, c in enumerate(choices, 1):
                    print(f"{i}. {c}")
                sel = input(f"Select (1-{len(choices)}): ").strip()
                try:
                    return choices[int(sel) - 1]
                except Exception:
                    return default or choices[0]
            return input("> ") or default

# ----------------------------------------------------------------------
# AUTO-DETECT SETTINGS
# ----------------------------------------------------------------------

def auto_detect_settings(file_path=None):
    """
    Automatically detect DJANGO_SETTINGS_MODULE by scanning settings.py or manage.py
    using regex, not import. (Preserves original logic.)
    """

    def search_recursive(root, filename="settings.py"):
        found = []
        for dirpath, _, files in os.walk(root):
            if filename in files:
                found.append(os.path.join(dirpath, filename))
        return found

    # Step 1: If user provides file (-f), use it
    target_file = file_path

    # Step 2: Otherwise, auto-search recursively
    if not target_file:
        found_files = search_recursive(os.getcwd())
        if not found_files:
            print("❌ settings.py not found recursively in current directory.", file=sys.stderr)
            sys.exit(1)

        # If multiple found → ask user which one to use
        if len(found_files) > 1:
            selected = Prompt.ask(
                "[yellow]Multiple settings.py found. Choose one:[/yellow]",
                choices=found_files,
                default=found_files[0]
            )
            target_file = selected
        else:
            target_file = found_files[0]

    # Step 3: Read file and extract ROOT_URLCONF or DJANGO_SETTINGS_MODULE
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read {target_file}: {e}", file=sys.stderr)
        sys.exit(1)

    module_name = None

    # From settings.py → find ROOT_URLCONF = "xxx.urls"
    match = re.search(r'ROOT_URLCONF\s*=\s*[\'"]([\w\.]+)\.urls[\'"]', content)
    if match:
        module_name = f"{match.group(1)}.settings"

    # From manage.py → find DJANGO_SETTINGS_MODULE='xxx.settings'
    if not module_name:
        match2 = re.search(r'DJANGO_SETTINGS_MODULE\s*=\s*[\'"]([\w\.]+)[\'"]', content)
        if match2:
            module_name = match2.group(1)

    if not module_name:
        print(f"❌ Could not detect DJANGO_SETTINGS_MODULE from {target_file}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Set environment
    os.environ["DJANGO_SETTINGS_MODULE"] = module_name

    # Step 5: Determine proper project root (ensure importable)
    target_dir = os.path.dirname(os.path.abspath(target_file))
    parent_dir = os.path.dirname(target_dir)

    # Add both to sys.path (project and parent)
    for path in [target_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)

    print(f"✅ Using settings module: {module_name}")
    return module_name

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(prog="djinspect", description="Inspect Django settings (standalone).", formatter_class=CustomRichHelpFormatter)
    parser.add_argument("command", help="Command name (all, auth, cache, core, db, diffsettings, email, installed, locale, logging, media, middleware, security, session, site, static, storage, template, validator)")
    parser.add_argument("--filter", "-F", help="Filter keyword", default=None)
    parser.add_argument("--json", help="Output JSON", action="store_true")
    parser.add_argument("--export", help="Export to file", default=None)
    parser.add_argument("-f", "--file", help="Path to settings.py or manage.py for auto detection (optional)")

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
        if not os.getenv("DJANGO_SETTINGS_MODULE"):
            auto_detect_settings(file_path=args.file)

        cmd.handle(**options)
    except TypeError:
        # Some handles may expect (*args, **options) signature
        cmd.handle(*(), **options)

if __name__ == "__main__":
    main()
