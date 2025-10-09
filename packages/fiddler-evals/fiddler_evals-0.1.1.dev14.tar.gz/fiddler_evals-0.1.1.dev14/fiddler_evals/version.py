from pathlib import Path

with open(Path(__file__).resolve().parent / "VERSION", encoding="utf-8") as f:
    __version__ = f.read().strip()
