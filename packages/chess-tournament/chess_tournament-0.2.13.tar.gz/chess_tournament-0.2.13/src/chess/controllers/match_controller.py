"""Controller for creating and viewing chess matches."""

import json
import os
import logging
from chess.models.match import Match
from chess import storage

logger = logging.getLogger(__name__)


class MatchController:
    """Handles the creation and viewing of matches."""

    FILE_PATH = "data/matches.json"

    def __init__(self, player_controller):
        self.player_controller = player_controller
        self.storage = storage
        logger.debug("Initializing MatchController")
        self.matches = self.load_matches()

    def load_matches(self):
        """
        Load matches from the JSON file.
        Returns an empty list if the file does not exist or is empty.
        """
        if not os.path.exists(self.FILE_PATH):
            logger.info(
                "matches.json not found – starting with an empty list"
                "(will be created on save)"
            )
            return []
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            file_content = f.read()
            if not file_content:
                return []

            f.seek(0)

            try:
                logger.debug("Loading matches from file")
                data = json.load(f)
                players_by_id = self.player_controller.get_players_by_id()

                return [Match.from_dict(d, players_by_id) for d in data]
            except json.JSONDecodeError as e:
                # Handle the case where the JSON is invalid
                logging.error("JSON decoding error in %s: %s", self.FILE_PATH, e)
                return []

    def save_matches(self):
        """Save the current list of matches to the JSON file."""
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                [m.to_dict() for m in self.matches], f, indent=2, ensure_ascii=False
            )
        logger.info("Matches saved to %s", self.FILE_PATH)

    def interactive_create_match(self):
        """
        Interactively prompts the user to create a new match.
        """
        print("\n--- Create a Match ---")
        id1 = input("Enter first player's national ID: ").strip()
        id2 = input("Enter second player's national ID: ").strip()
        result = input("Enter result (1 for win, 2 for loss, 0 for draw): ").strip()

        self.create_match(id1, id2, result)

    def create_match(self, id1, id2, result):
        """Create a new match between two players with the given result.
        Args:
        id1 (str): National ID of the first player.
        id2 (str): National ID of the second player.
        result (str): The result as a string ("1", "2", or "0").
        """
        p_white = self.player_controller.find_player_by_id(id1)
        p_black = self.player_controller.find_player_by_id(id2)

        if not p_white or not p_black:
            logger.error("One or both player IDs not found: %s, %s", id1, id2)
            return False

        if id1 == id2:
            logger.warning("A player cannot play against themselves: idx=%s", id1)
            return False

        if result == "1":
            score = [1, 0]
        elif result == "2":
            score = [0, 1]
        elif result == "0":
            score = [0.5, 0.5]
        else:
            logger.error("Invalid result provided: %s", result)
            return False

        new_match = Match(
            player_white=p_white,
            player_black=p_black,
            score=score,
        )

        self.matches.append(new_match)
        self.save_matches()
        logger.info(
            "Match created between %s %s and %s %s with score %s",
            p_white.first_name,
            p_white.last_name,
            p_black.first_name,
            p_black.last_name,
            score,
        )
        return True

    def list_matches(self):
        """Loads all matches from file and returns them."""
        self.matches = self.load_matches()
        logger.debug("Returning match list (%d items)", len(self.matches))
        return self.matches
