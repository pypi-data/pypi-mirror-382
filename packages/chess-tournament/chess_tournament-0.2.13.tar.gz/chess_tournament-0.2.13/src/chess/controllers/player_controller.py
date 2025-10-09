"""Controller for player-related operations in the Chess Tournament Software."""

import json
import os
import logging
import re
import unicodedata
from datetime import datetime, date
from chess.models.player import Player

logger = logging.getLogger(__name__)


class PlayerController:
    """Handles player-related operations."""

    FILE_PATH = "data/players.json"

    def __init__(self):
        logger.info("PlayerController initialized")
        logger.debug("Loading players from JSON file")
        self.players = self.load_players()

    def is_valid_id(self, id_national):
        """Validate national ID format: two letters + five digits."""
        return bool(re.fullmatch(r"[A-Z]{2}\d{5}", id_national))

    def player_exists(self, id_national: str) -> bool:
        """Check if a player with this ID already exists."""
        return any(p.id_national == id_national for p in self.players)

    def is_valid_name(self, name: str) -> bool:
        """Validate name contains letters, spaces, or hyphens, and is non-empty."""
        return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\- ]+", name.strip()))

    def is_valid_birthdate(self, birthdate):
        """Validate birthdate format: YYYY-MM-DD."""
        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def load_players(self):
        """
        Load players from the JSON file.
        Return an empty list if the file does not exist.
        """
        if not os.path.exists(self.FILE_PATH):
            logger.info(
                "players.json not found – starting with an empty list"
                "(will be created on save)"
            )
            return []
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            try:
                players_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error("JSON decoding error in %s: %s", self.FILE_PATH, e)
                return []

        # Check if the loaded data is a list before proceeding
        if not isinstance(players_data, list):
            logger.error("File content is not a JSON list. Returning an empty list.")
            return []

        return [Player.from_dict(p) for p in players_data]

    def save_players(self):
        """Save the current list of players to the JSON file."""
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            players_data = [p.to_dict() for p in self.players]
            json.dump(players_data, f, indent=2, ensure_ascii=False)
        logger.info("Players saved to %s", self.FILE_PATH)

    def add_player(self, id_national, last_name, first_name, birthdate):
        """Add a new player with full details."""
        logger.debug(
            "Trying to add player: %s %s (%s)", first_name, last_name, id_national
        )

        if not self.is_valid_id(id_national):
            logger.warning("Invalid player ID format: %s", id_national)
            return False

        if self.player_exists(id_national):
            logger.warning("Duplicate player ID: %s", id_national)
            return False

        if isinstance(birthdate, str):
            if not self.is_valid_birthdate(birthdate):
                logger.warning("Invalid birthdate format: %s", birthdate)
                return False
            birthdate_iso = birthdate
        elif isinstance(birthdate, date):
            birthdate_iso = birthdate.isoformat()
        else:
            logger.warning("Birthdate type not recognized: %s", type(birthdate))
            return False

        new_player = Player(
            last_name=last_name.strip(),
            first_name=first_name.strip(),
            birth_date=birthdate_iso,
            id_national=id_national,
        )

        self.players.append(new_player)
        self.save_players()
        logger.info(
            "Player added successfully: %s %s (%s)", first_name, last_name, id_national
        )
        return True

    def list_players(self):
        """
        Return the list of all players sorted alphabetically:
        - Primary: last_name (case/accent insensitive)
        - Secondary: first_name (case/accent insensitive)
        - Tertiary: id_national (stable tie-breaker)
        """
        logger.debug("Listing %d players (sorted)", len(self.players))
        return sorted(
            self.players,
            key=lambda p: (
                self._normalize_for_sort(p.last_name),
                self._normalize_for_sort(p.first_name),
                p.id_national,
            ),
        )

    def _normalize_for_sort(self, s: str) -> str:
        """
        Normalize a string for sorting:
        - Removes accents (é → e, ç → c, etc.)
        - Converts to lowercase
        """
        normalized = unicodedata.normalize("NFKD", s)
        return normalized.encode("ASCII", "ignore").decode("utf-8").casefold()

    def find_player_by_id(self, player_id):
        """
        Finds and returns a player object by their national ID.

        Returns None if no player is found.
        """
        for player_obj in self.players:
            if player_obj.id_national == player_id:
                return player_obj
        return None

    def get_players_by_id(self):
        """Returns a dictionary mapping player IDs to Player objects."""
        return {p.id_national: p for p in self.players}
