"""Tournament model."""

from datetime import date
from chess.models.round import Round
from .player import Player
from .match import Match


class Tournament:
    """Represents a chess tournament."""

    def __init__(
        self,
        name: str,
        location: str,
        start_date: date,
        end_date: date,
        number_of_rounds=4,
        rounds=None,
        players=None,
        description="",
        current_round=0,
    ):
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.number_of_rounds = number_of_rounds
        self.current_round = current_round
        self.players = players if players is not None else []
        self.rounds = rounds if rounds is not None else []
        self.description = description

    def add_player(self, player):
        """Add a player to the tournament."""
        self.players.append(player)

    def add_round(self, round_):
        """Add a round to the tournament."""
        self.rounds.append(round_)

    def next_round_number(self):
        """Return the next round number."""
        return self.current_round + 1

    def increment_round(self):
        """Move to the next round."""
        self.current_round += 1

    def to_dict(self) -> dict:
        """Converts the Tournament object to a dictionary for serialization."""
        return {
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "number_of_rounds": self.number_of_rounds,
            "current_round": self.current_round,
            "players": [p.to_dict() for p in self.players],
            "rounds": [r.to_dict() for r in self.rounds],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Tournament from a dictionary
        without duplicating Player instances."""
        players = [Player.from_dict(pdata) for pdata in data.get("players", [])]
        players_by_id = {p.id_national: p for p in players}

        rounds = []
        for rdata in data.get("rounds", []):
            matches = [
                Match.from_dict(mdata, players_by_id)
                for mdata in rdata.get("matches", [])
            ]

            round_obj = Round(
                round_no=rdata.get("round_no", 0),
                matches=matches,
                start_time=rdata.get("start_time"),
                end_time=rdata.get("end_time"),
            )
            rounds.append(round_obj)

        tournament = cls(
            name=data.get("name", ""),
            location=data.get("location", ""),
            start_date=(
                date.fromisoformat(data.get("start_date"))
                if data.get("start_date")
                else None
            ),
            end_date=(
                date.fromisoformat(data.get("end_date"))
                if data.get("end_date")
                else None
            ),
            description=data.get("description", ""),
            current_round=data.get("current_round", 0),
            players=players,
            rounds=rounds,
            number_of_rounds=data.get("number_of_rounds", 4),
        )

        return tournament
