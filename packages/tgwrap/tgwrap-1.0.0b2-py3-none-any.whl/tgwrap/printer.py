"""Simple class for printing console messages
"""
import shutil
import sys

import click


class Printer:
    """Render formatted CLI messages with consistent styling."""

    def __init__(self, verbose: bool = False):
        self._print_verbose = verbose

    @property
    def print_verbose(self) -> bool:
        """Return whether verbose output is enabled."""
        return self._print_verbose

    def line(self, char: str = "-", length: int | None = None) -> None:
        """Draw a horizontal line using the provided character."""
        width = length or 80
        try:
            width, _ = shutil.get_terminal_size()
        except OSError:
            # Fall back to default width when the terminal size cannot be detected.
            pass
        if length is not None:
            width = length
        click.secho(char * width, file=sys.stderr)

    def header(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a highlighted header with optional separator lines."""
        msg = msg.strip() if isinstance(msg, str) else msg
        if print_line_before:
            self.line()
        self.line()
        click.secho(msg, bold=True, file=sys.stderr)
        self.line()
        if print_line_after:
            self.line()

    def verbose(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a verbose-only message when verbosity is enabled."""
        if not self._print_verbose:
            return
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            print(msg, flush=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            # Ignore broken pipe style errors during verbose logging.
            pass

    def normal(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a regular message to stderr."""
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            print(msg, flush=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            pass

    def bold(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a bold highlighted message."""
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            click.secho(msg, bold=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            pass

    def warning(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a warning message in yellow."""
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            click.secho(msg, fg="yellow", bold=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            pass

    def error(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print an error message in red."""
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            click.secho(msg, fg="red", bold=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            pass

    def success(
        self, msg, print_line_before: bool = False, print_line_after: bool = False
    ) -> None:
        """Print a success message in green."""
        msg = msg.strip() if isinstance(msg, str) else msg
        try:
            if print_line_before:
                self.line()
            click.secho(msg, fg="green", bold=True, file=sys.stderr)
            if print_line_after:
                self.line()
        except OSError:
            pass

    def progress_indicator(self) -> None:
        """Emit a progress dot without breaking the terminal."""
        try:
            print(".", flush=True, file=sys.stderr, end="")
        except OSError:
            pass
