from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.resolve()

assert PACKAGE_DIR.is_dir(), "Failed to resolve package directory."
