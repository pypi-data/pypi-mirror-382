import os
import sys
import warnings

from .config_parser import Config
from .config_writer import write_config
from types import SimpleNamespace
from typing import Optional, List
from pathlib import Path

__all__ = ["parse_config", "write_config"]

# Original execution path
_original_cwd = None


def _orange_warning(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning formatter — no source line, orange text.
    """
    _ORANGE = "\033[33m"
    _RESET = "\033[0m"

    stream = file if file is not None else sys.stderr
    text = f"{_ORANGE}{category.__name__}: {message}{_RESET}\n"
    stream.write(text)


def parse_config(
    config_paths: Optional[List[str]] = None,
    switch_cwd: bool = False,
    restore_cwd: bool = False,
) -> SimpleNamespace:
    """Retrieve the application configuration, including YAML, JSON, TOML, and .env content.

    - Optionally switches CWD to the main entry directory.
    - Optionally restores the CWD to its original value after reading config.
    - Saves the original working directory (only once).
    - Warns if the CWD changed.
    - Stores the original CWD at config.original_cwd (only if not already set).

    Args:
        config_paths: Optional list of paths to project-specific config files.
        switch_cwd: Whether to change the working directory to the main entry directory. Defaults to False.
        restore_cwd: Whether to restore the working directory to its original path after loading config. Defaults to False.

    Returns:
        SimpleNamespace: A namespace object with config and env values accessible via dot notation.
    """
    def main_dir() -> Path:
        # Frozen (Nuitka, PyInstaller, cx_Freeze)
        if getattr(sys, "frozen", False):
            # Prefer argv[0] so Nuitka onefile resolves to the real exe location
            return Path(sys.argv[0]).resolve().parent

        # Source run (script or `python -m pkg`)
        main_mod = sys.modules.get("__main__")
        if main_mod and getattr(main_mod, "__file__", None):
            return Path(main_mod.__file__).resolve().parent

        # Fallback (REPL, unusual launchers)
        return Path.cwd()
    
    global _original_cwd
    
    warnings.showwarning = _orange_warning

    # Remember original cwd
    if _original_cwd is None:
        _original_cwd = Path.cwd().resolve()

    # Switch cwd if requested
    if switch_cwd:
        target_dir = main_dir()
        if target_dir != _original_cwd:
            os.chdir(target_dir)
            new_cwd = Path.cwd().resolve()
            if new_cwd != _original_cwd:
                warnings.warn(
                    f"Working directory changed: '{_original_cwd}' -> '{new_cwd}'.",
                    RuntimeWarning,
                    stacklevel=2,
                )

    # Load config
    if config_paths:
        Config().reload(config_paths)
    else:
        Config().reload()

    cfg = Config().get()

    # Set original_cwd
    setattr(cfg, "original_cwd", str(_original_cwd))

    # Restore cwd if requested and it actually changed
    current_cwd = Path.cwd().resolve()
    if restore_cwd and current_cwd != _original_cwd:
        os.chdir(_original_cwd)
        warnings.warn(
            f"Working directory restored: '{current_cwd}' -> '{_original_cwd}'.",
            RuntimeWarning,
            stacklevel=2,
        )

    return cfg
