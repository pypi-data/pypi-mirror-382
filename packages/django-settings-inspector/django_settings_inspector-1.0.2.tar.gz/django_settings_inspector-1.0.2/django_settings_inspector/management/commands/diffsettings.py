#!/usr/bin/env python3
# file: management/commands/diffsettings.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07 20:53:40.870299
# Description: Custom colored diffsettings command
# License: MIT

import sys
from django.core.management.commands.diffsettings import Command as BaseCommand
from django.conf import settings as django_settings

# ----------------------------------------------------------------------
# Try import Rich, fallback to make_colors
# ----------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.syntax import Syntax
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    try:
        from make_colors import make_colors
        HAS_MAKE_COLORS = True
    except ImportError:
        HAS_MAKE_COLORS = False


# ----------------------------------------------------------------------
# Command class override
# ----------------------------------------------------------------------
class Command(BaseCommand):
    """
    Override Django's diffsettings command dengan colored output.
    Dapat berjalan tanpa Rich (fallback ke make_colors atau plain).
    """

    def handle(self, **options):
        from django.conf import settings, Settings

        # Ambil default settings
        default_settings = options.get('default')
        if default_settings:
            try:
                settings_mod = __import__(default_settings, fromlist=[''])
            except Exception as e:
                self.stderr.write(f"❌ Failed to import default settings: {e}")
                return
        else:
            settings_mod = Settings('django.conf.global_settings')

        # Ambil user settings
        user_settings = {
            key: getattr(django_settings, key)
            for key in dir(django_settings)
            if key.isupper()
        }

        # Ambil default settings values
        default = {
            key: getattr(settings_mod, key)
            for key in dir(settings_mod)
            if key.isupper()
        }

        # Build output lines
        output_lines = []

        # Tampilkan semua atau hanya berbeda
        if options.get('all'):
            for key in sorted(user_settings):
                output_lines.append(f"{key} = {user_settings[key]!r}")
        else:
            for key in sorted(user_settings):
                if key not in default:
                    output_lines.append(f"{key} = {user_settings[key]!r}  ###")
                elif user_settings[key] != default[key]:
                    output_lines.append(f"{key} = {user_settings[key]!r}")

        output = '\n'.join(output_lines)

        # Handle --no-color
        if options.get('no_color'):
            self.stdout.write(output)
            return

        # Warna: Prioritas → Rich → make_colors → plain
        if HAS_RICH:
            self._output_with_rich(output)
        elif HAS_MAKE_COLORS:
            self._output_with_make_colors(output)
        else:
            self.stdout.write(output)

    # ------------------------------------------------------------------
    # Rich Output
    # ------------------------------------------------------------------
    def _output_with_rich(self, output):
        """Format output menggunakan Rich dengan syntax highlighting"""
        console = Console()

        syntax = Syntax(
            output,
            "python",
            theme="fruity",
            line_numbers=False,
            word_wrap=True,
        )
        console.print(syntax)

    # ------------------------------------------------------------------
    # make_colors Output
    # ------------------------------------------------------------------
    def _output_with_make_colors(self, output):
        """Format output menggunakan make_colors sebagai fallback"""
        lines = output.split('\n')

        for line in lines:
            if not line.strip():
                self.stdout.write(line)
                continue

            # Line that is not in the default (###)
            if '###' in line:
                parts = line.split('###')
                main_part = parts[0].strip()
                if '=' in main_part:
                    key_val = main_part.split('=', 1)
                    key = make_colors(key_val[0].strip(), 'lightgreen', 'bold')
                    value = make_colors('= ' + key_val[1].strip(), 'yellow')
                    marker = make_colors('  ###', 'lightblue')
                    colored_line = key + ' ' + value + marker
                else:
                    colored_line = make_colors(line, 'white')

            # Baris setting biasa
            elif '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = make_colors(parts[0].strip(), 'cyan', 'bold')
                    value = make_colors('= ' + parts[1].strip(), 'lightyellow')
                    colored_line = key + ' ' + value
                else:
                    colored_line = make_colors(line, 'white')

            # Default
            else:
                colored_line = make_colors(line, 'white')

            self.stdout.write(colored_line)
