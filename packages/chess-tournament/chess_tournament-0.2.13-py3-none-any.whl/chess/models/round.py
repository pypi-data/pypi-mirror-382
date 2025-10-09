"""This module defines the Round class for managing chess tournament rounds."""

from datetime import datetime
from .match import Match


class Round:
    """Represents a single round in a chess tournament."""

    def __init__(
        self,
        round_no: int,
        matches: list = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ):
        self.round_no = round_no
        self.name = f"Round {round_no}"
        self.matches = matches if matches is not None else []
        self.start_time = (
            start_time if start_time is not None else datetime.now().isoformat()
        )
        self.end_time = end_time
        self.start_date = self.start_time
        self.end_date = self.end_time

    def __str__(self):
        start_str = self.start_time
        end_str = self.end_time if self.end_time is not None else "In progress"
        return f"{self.name} ({start_str} → {end_str})"

    def to_dict(self):
        """Converts the Round object to a dictionary for serialization."""
        return {
            "round_no": self.round_no,
            "matches": [m.to_dict() for m in self.matches],
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data, players_by_id):
        """Creates a Round instance from a dictionary."""
        matches = [Match.from_dict(m, players_by_id) for m in data.get("matches", [])]
        return cls(
            round_no=data["round_no"],
            matches=matches,
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

    def close(self):
        """Sets the end time of the round to the current time."""
        self.end_time = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Checks if all matches in the round have been completed."""
        return all(m.score != [0, 0] for m in self.matches)
