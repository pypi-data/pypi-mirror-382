#!/usr/bin/env python3
"""
SpeakUB CLI - Entry point for the application
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from speakub.ui.app import EPUBReaderApp


def is_running_in_terminal(debug: bool = False) -> bool:
    """
    Check if running in a real terminal environment
    - Check if stdout/stderr are tty
    - If not tty, we need to relaunch in terminal
    - If tty, check if it's a proper terminal
    """
    # Basic check: stdout and stderr must both be tty
    stdout_is_tty = sys.stdout.isatty()
    stderr_is_tty = sys.stderr.isatty()
    if debug:
        print(
            f"DEBUG: stdout.isatty()={stdout_is_tty}, stderr.isatty()={stderr_is_tty}",
            file=sys.stderr,
        )

    if not (stdout_is_tty and stderr_is_tty):
        if debug:
            print(
                "DEBUG: Not running in tty, need to relaunch in terminal",
                file=sys.stderr,
            )
        return False

    # Check TERM environment variable
    term = os.environ.get("TERM", "")
    if debug:
        print(f"DEBUG: TERM={term}", file=sys.stderr)
    if not term or term == "dumb":
        if debug:
            print("DEBUG: TERM is not set or dumb, need to relaunch", file=sys.stderr)
        return False

    # If we're in a proper terminal, we're good
    if term in ("xterm", "xterm-256color", "screen", "tmux", "linux"):
        if debug:
            print("DEBUG: In proper terminal, returning True", file=sys.stderr)
        return True

    if debug:
        print(
            "DEBUG: TERM not recognized as proper terminal, need to relaunch",
            file=sys.stderr,
        )
    return False


def find_terminal_emulator() -> Optional[tuple[str, List[str]]]:
    """
    Find an available terminal emulator and return the launch command
    Returns (terminal_name, command_args) or None
    """
    # Terminal emulator list, in order of preference
    terminals = [
        ("xterm", ["xterm", "-e"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e"]),
        ("foot", ["foot", "-e"]),
        ("alacritty", ["alacritty", "-e"]),
        ("kitty", ["kitty", "-e"]),
        ("wezterm", ["wezterm", "start", "--"]),
        ("gnome-terminal", ["gnome-terminal", "--"]),
        ("konsole", ["konsole", "-e"]),
        ("urxvt", ["urxvt", "-e"]),
        ("st", ["st", "-e"]),
    ]

    # First check the system default terminal ($TERMINAL environment variable)
    default_term = os.environ.get("TERMINAL")
    if default_term:
        for term_name, cmd_args in terminals:
            if term_name == default_term:
                try:
                    result = subprocess.run(
                        ["which", term_name], capture_output=True, timeout=1
                    )
                    if result.returncode == 0:
                        return (term_name, cmd_args)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

    # If no default terminal or not found, check in order of preference
    for term_name, cmd_args in terminals:
        # Check if the terminal can be found
        try:
            result = subprocess.run(
                ["which", term_name], capture_output=True, timeout=1
            )
            if result.returncode == 0:
                return (term_name, cmd_args)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return None


def relaunch_in_terminal(original_args: List[str], debug: bool = False) -> None:
    """
    Relaunch the application in a terminal emulator

    Args:
        original_args: Original command line arguments
        debug: Whether debug output should be shown
    """
    if debug:
        print(
            f"DEBUG: Relaunching in terminal with args: {original_args}",
            file=sys.stderr,
        )
    terminal_info = find_terminal_emulator()

    if not terminal_info:
        if debug:
            print("DEBUG: No terminal emulator found", file=sys.stderr)
        # Unable to find terminal emulator, try to notify user with desktop notification
        try:
            subprocess.run(
                [
                    "notify-send",
                    "SpeakUB Error",
                    "No terminal emulator found. Please run from a terminal.",
                ],
                timeout=2,
            )
        except Exception:
            pass

        print("Error: No terminal emulator found.", file=sys.stderr)
        print("Please run SpeakUB from a terminal.", file=sys.stderr)
        sys.exit(1)

    term_name, term_cmd = terminal_info
    if debug:
        print(
            f"DEBUG: Found terminal: {term_name}, command: {term_cmd}", file=sys.stderr
        )

    # Build the complete launch command
    # Use current Python interpreter and script path
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])

    # Check if we're running as a module (python -m speakub.cli)
    if script_path.endswith(".py") and "speakub/cli.py" in script_path:
        # Running as module, use python -m
        cmd_string = f"{python_exe} -m speakub.cli"
    else:
        # Running as installed script
        cmd_string = f"{python_exe} {script_path}"

    if original_args:
        # Use shlex.quote to properly escape arguments
        import shlex

        quoted_args = [shlex.quote(arg) for arg in original_args]
        cmd_string += " " + " ".join(quoted_args)

    # Use appropriate command format for each terminal
    # Wrap command to exit terminal after execution
    exit_cmd = f"{cmd_string}; exit"

    if term_name == "xfce4-terminal":
        # xfce4-terminal: execute without hold, terminal closes after exit
        full_cmd = ["xfce4-terminal", "-e", f"bash -c '{exit_cmd}'"]
    elif term_name == "xterm":
        # xterm: execute without -hold so terminal closes
        full_cmd = ["xterm", "-e", f"bash -c '{exit_cmd}'"]
    elif term_name in ("gnome-terminal", "konsole"):
        # These terminals work better with bash -c
        full_cmd = term_cmd + ["bash", "-c", exit_cmd]
    elif term_name == "alacritty":
        # Alacritty: use -e with shell
        full_cmd = ["alacritty", "-e", "bash", "-c", exit_cmd]
    elif term_name == "kitty":
        # Kitty: use -e with shell
        full_cmd = ["kitty", "-e", "bash", "-c", exit_cmd]
    else:
        # For other terminals, try the standard approach with exit
        full_cmd = term_cmd + ["bash", "-c", exit_cmd]
    if debug:
        print(f"DEBUG: Full command: {full_cmd}", file=sys.stderr)

    try:
        # Launch with Popen in background, don't wait for completion
        if debug:
            print("DEBUG: Launching subprocess...", file=sys.stderr)
        subprocess.Popen(
            full_cmd,
            start_new_session=True,  # Detach from current session
            # Don't redirect stdout/stderr so user can see any error messages
        )
        if debug:
            print(
                "DEBUG: Subprocess launched, exiting current process", file=sys.stderr
            )
        # Exit current process immediately
        sys.exit(0)
    except Exception as e:
        print(f"Error launching terminal ({term_name}): {e}", file=sys.stderr)
        sys.exit(1)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for SpeakUB."""

    # ===== Parse arguments first to get debug flag =====
    parser = argparse.ArgumentParser(description="SpeakUB")
    parser.add_argument("epub", help="Path to EPUB file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", help="Path to log file")
    args = parser.parse_args(argv)

    # ===== Auto-install desktop entry on first run =====
    from speakub.desktop import check_desktop_installed, install_desktop_entry

    if not check_desktop_installed():
        try:
            install_desktop_entry()
        except Exception:
            pass  # Silently fail if desktop installation fails

    # ===== Check if running in terminal =====
    if not is_running_in_terminal(args.debug):
        if args.debug:
            print("DEBUG: Not running in terminal, relaunching...", file=sys.stderr)
        relaunch_in_terminal(argv or sys.argv[1:], args.debug)
        return  # relaunch_in_terminal calls sys.exit(0)

    if args.debug and not args.log_file:
        log_dir = Path.home() / ".local/share/speakub/logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = str(log_dir / f"speakub-{ts}.log")
        print(f"Debug logging to: {args.log_file}")

    log_level = logging.DEBUG if args.debug else logging.INFO
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(
            logging.FileHandler(Path(args.log_file).expanduser(), encoding="utf-8")
        )
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    epub_path = Path(args.epub)
    if not epub_path.exists():
        print(f"Error: EPUB file not found: {epub_path}", file=sys.stderr)
        sys.exit(1)

    app = EPUBReaderApp(str(epub_path), debug=args.debug, log_file=args.log_file)
    app.run()


if __name__ == "__main__":
    main()
