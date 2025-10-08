"""Model for representing a chess match between two players."""

import logging
from .player import Player

logger = logging.getLogger(__name__)


class Match:
    """Represents a match between two players."""

    def __init__(self, player_white: Player, player_black: Player, score: list):
        """Initialize a Match instance with two players and their scores.

        Args:
            player_white: The first player.
            player_black: The second player.
            score: A list with two elements [score1, score2].
        """
        self.player_white = player_white
        self.player_black = player_black
        self.score = score or [0.0, 0.0]
        logger.debug(
            "Creating Match: %s vs %s, score: %s", player_white, player_black, score
        )

    def __str__(self):
        return (
            f"{self.player_white.last_name} vs {self.player_black.last_name} : "
            f"{self.score[0]}-{self.score[1]}"
        )

    def to_dict(self):
        """Converts the Match object to a dictionary for serialization."""
        logger.debug("Converting Match to dict")
        return {
            "player_white_id": self.player_white.id_national,
            "player_black_id": self.player_black.id_national,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data, players_by_id):
        """Create a Match instance from a dictionary."""
        player_white = players_by_id[data["player_white_id"]]
        player_black = players_by_id[data["player_black_id"]]
        logger.debug("Creating Match from dict: %s", data)
        return cls(player_white, player_black, data.get("score", [0.0, 0.0]))
