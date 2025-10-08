"""
Custom Django management command untuk diffsettings dengan output berwarna.
Menggunakan Rich dengan fallback ke make_colors.

Cara Install:
1. Letakkan file ini di: yourapp/management/commands/diffsettings.py
2. Pastikan struktur folder:
   yourapp/
   ├── management/
   │   ├── __init__.py
   │   └── commands/
   │       ├── __init__.py
   │       └── diffsettings.py
"""

from django.core.management.commands.diffsettings import Command as BaseCommand
from django.conf import settings as django_settings

# Try import Rich, fallback to make_colors
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


class Command(BaseCommand):
    """
    Override Django's diffsettings command dengan colored output
    """
    
    def handle(self, **options):
        from django.conf import settings, Settings
        
        # Ambil default settings
        default_settings = options['default']
        if default_settings:
            settings_mod = __import__(default_settings, fromlist=[''])
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
        
        # Build output
        output_lines = []
        
        # Tampilkan yang berbeda atau tidak ada di default
        if options['all']:
            # Tampilkan semua settings
            for key in sorted(user_settings):
                output_lines.append(f"{key} = {user_settings[key]!r}")
        else:
            # Tampilkan hanya yang berbeda
            for key in sorted(user_settings):
                if key not in default:
                    output_lines.append(f"{key} = {user_settings[key]!r}  ###")
                elif user_settings[key] != default[key]:
                    output_lines.append(f"{key} = {user_settings[key]!r}")
        
        # Join output
        output = '\n'.join(output_lines)
        
        # Cek apakah user minta no-color
        if options.get('no_color'):
            self.stdout.write(output)
            return
        
        # Format dengan warna
        if HAS_RICH:
            self._output_with_rich(output)
        elif HAS_MAKE_COLORS:
            self._output_with_make_colors(output)
        else:
            # Fallback tanpa warna
            self.stdout.write(output)
    
    def _output_with_rich(self, output):
        """Format output menggunakan Rich dengan syntax highlighting"""
        console = Console()
        
        # Gunakan Syntax dengan theme fruity dan lexer Python
        syntax = Syntax(
            output,
            "python",
            theme="fruity",
            line_numbers=False,
            word_wrap=True,
        )
        
        console.print(syntax)
    
    def _output_with_make_colors(self, output):
        """Format output menggunakan make_colors sebagai fallback"""
        lines = output.split('\n')
        
        for line in lines:
            if not line.strip():
                self.stdout.write(line)
                continue
            
            # Deteksi tipe baris dan beri warna
            if '###' in line:
                # Setting yang tidak ada di default (ditandai ###)
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
            elif '=' in line:
                # Setting line dengan assignment
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = make_colors(parts[0].strip(), 'cyan', 'bold')
                    value = make_colors('= ' + parts[1].strip(), 'lightyellow')
                    colored_line = key + ' ' + value
                else:
                    colored_line = make_colors(line, 'white')
            else:
                # Default
                colored_line = make_colors(line, 'white')
            
            self.stdout.write(colored_line)