"""Module for handling persistent storage of players,
tournaments, and matches using JSON files."""

import json
from pathlib import Path
from platformdirs import user_data_dir

APP_NAME = "chess-tournament"
APP_AUTHOR = "thi26"

data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
data_dir.mkdir(parents=True, exist_ok=True)

# Dictionnaire des fichiers JSON
FILES = {
    "players": data_dir / "players.json",
    "tournaments": data_dir / "tournaments.json",
    "matches": data_dir / "matches.json",
}


def init_files():
    """Creates empty JSON files if they don't exist yet."""
    for path in FILES.values():
        if not path.exists():
            path.write_text("[]", encoding="utf-8")


def load(name):
    """Loads a JSON file (players, tournaments, matches)."""
    if name not in FILES:
        raise KeyError(f"Clé '{name}' non définie dans FILES")
    init_files()
    path = FILES[name]
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    """Saves data to the corresponding JSON file."""
    if name not in FILES:
        raise KeyError(f"Clé '{name}' non définie dans FILES")
    path = FILES[name]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
