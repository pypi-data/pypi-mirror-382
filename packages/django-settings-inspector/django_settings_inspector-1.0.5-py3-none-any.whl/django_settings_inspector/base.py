import json
from pprint import pformat
from django.core.management.base import BaseCommand
from django.conf import settings

# Try rich
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    HAS_RICH = True
except Exception:
    HAS_RICH = False

# Try make_colors
try:
    from make_colors import make_colors
    HAS_MAKE_COLORS = True
except Exception:
    HAS_MAKE_COLORS = False


SENSITIVE_KEYS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "AWS_SECRET", "AWS_ACCESS")


class BaseInspectorCommand(BaseCommand):
    """
    Base class for inspector commands.
    Provides:
    - add_arguments (filter, json, export)
    - render_data(data, options) -> prints filtered/masked output
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--filter",
            "-f",
            dest="filter",
            type=str,
            default=None,
            help="Filter output by keyword (case-insensitive)",
        )
        parser.add_argument(
            "--json",
            dest="json",
            action="store_true",
            default=False,
            help="Output JSON",
        )
        parser.add_argument(
            "--export",
            dest="export",
            type=str,
            default=None,
            help="Export output to file (path). If --json is set, exports JSON; otherwise pretty-printed text.",
        )

    def render_data(self, data, options):
        """
        data: dict or other python object
        options: dict-like from argparse (passed from handle(**options))
        """
        keyword = options.get("filter")
        as_json = options.get("json")
        export_path = options.get("export")

        # Mask sensitive keys before output
        safe_data = self._mask_sensitive(data)

        # Filter
        if keyword:
            safe_data = self._filter_recursive(safe_data, keyword)

        # Prepare output string
        if as_json:
            try:
                out = json.dumps(self._prepare_serializable(safe_data), indent=2, default=repr)
            except Exception:
                out = json.dumps(self._prepare_serializable(pformat(safe_data)), indent=2)
        else:
            out = pformat(safe_data, width=120, sort_dicts=True)

        # Export if requested
        if export_path:
            mode = "w"
            with open(export_path, mode, encoding="utf-8") as fh:
                fh.write(out)
            self.stdout.write(f"Exported to {export_path}")
            return

        # Print
        if HAS_RICH:
            console = Console()
            panel = Panel(Syntax(out, "python", theme="fruity", line_numbers=False, word_wrap=True), title=self.help or "Settings")
            console.print(panel)
        elif HAS_MAKE_COLORS:
            for line in out.splitlines():
                self.stdout.write(make_colors(line, "lightyellow"))
        else:
            self.stdout.write(out)

    def _prepare_serializable(self, obj):
        # Make objects serializable by converting non-serializable items to repr
        if isinstance(obj, dict):
            return {str(k): self._prepare_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [self._prepare_serializable(v) for v in obj]
        try:
            json.dumps(obj)
            return obj
        except Exception:
            return repr(obj)

    def _mask_sensitive(self, obj):
        # Mask values for keys that look sensitive
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if any(sk.lower() in str(k).lower() for sk in SENSITIVE_KEYS):
                    out[k] = self._mask_value(v)
                else:
                    out[k] = self._mask_sensitive(v)
            return out
        elif isinstance(obj, (list, tuple)):
            return [self._mask_sensitive(v) for v in obj]
        else:
            return obj

    def _mask_value(self, value):
        if value is None:
            return None
        s = str(value)
        if len(s) <= 8:
            return "*****"
        return s[:6] + "..." + s[-4:]

    def _filter_recursive(self, obj, keyword):
        keyword = keyword.lower()
        if isinstance(obj, dict):
            filtered = {}
            for k, v in obj.items():
                k_lower = str(k).lower()
                if keyword in k_lower:
                    filtered[k] = v
                    continue
                # check nested
                nested = self._filter_recursive(v, keyword)
                if nested:
                    filtered[k] = nested
            return filtered
        elif isinstance(obj, (list, tuple, set)):
            out = []
            for item in obj:
                if keyword in str(item).lower():
                    out.append(item)
                else:
                    nested = self._filter_recursive(item, keyword)
                    if nested:
                        out.append(nested)
            return out
        else:
            return obj if keyword in str(obj).lower() else None
