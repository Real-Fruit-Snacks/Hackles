"""Custom argparse formatter with ANSI color support"""
import argparse
import sys
from hackles.display.colors import Colors


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Argparse formatter that adds ANSI colors to help output"""

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = 'usage: '
        if sys.stdout.isatty():
            prefix = f"{Colors.BOLD}{prefix}{Colors.END}"
        return super()._format_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        if sys.stdout.isatty() and heading:
            heading = f"{Colors.CYAN}{heading}{Colors.END}"
        super().start_section(heading)
