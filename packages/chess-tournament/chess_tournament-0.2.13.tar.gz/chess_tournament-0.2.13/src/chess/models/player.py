"""This module defines the Player class for a chess tournament."""

import logging

logger = logging.getLogger(__name__)


class Player:
    """Represents a chess player."""

    def __init__(self, last_name, first_name, birth_date, id_national, score=0.0):
        """Initialize a Player instance."""
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.id_national = id_national
        self.score = score
        logger.debug(
            "Creating Player: %s %s, Birth Date: %s, ID: %s, Score: %s",
            self.last_name,
            self.first_name,
            self.birth_date,
            self.id_national,
            self.score,
        )

    def full_name(self):
        """display full name of the player."""
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        """Convert the Player object to a dictionary."""
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birth_date": self.birth_date,
            "id_national": self.id_national,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Player instance from a dictionary."""
        logger.debug("Reconstructing Player from dict: %s", data)
        return cls(
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            birth_date=data.get("birth_date"),
            id_national=data.get("id_national"),
            score=data.get("score", 0.0),
        )
