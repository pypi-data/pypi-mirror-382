"""Controller for tournament-related operations."""

import json
import os
import logging
import random
from datetime import date
from jinja2 import Environment, PackageLoader
from chess.models.tournament import Tournament
from chess.models.round import Round
from chess.models.match import Match
from chess.views.tournament_view import TournamentView

logger = logging.getLogger(__name__)


class TournamentController:
    """Handles tournament operations such as creation, loading, and saving."""

    FILE_PATH = "data/tournaments.json"

    def __init__(self, player_controller):
        """Initialize the tournament controller and ensure JSON file exists."""
        self.player_controller = player_controller
        self.view = TournamentView()
        self.tournaments = []
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                f.write("[]")

        self.tournaments = self.load_tournaments()

    def load_tournaments(self) -> list[Tournament]:
        """Load tournaments from JSON file."""
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                data = f.read()
                if not data:
                    return []
                return [Tournament.from_dict(t) for t in json.loads(data)]
        except FileNotFoundError:
            return []

    def save_tournaments(self) -> None:
        """Save tournaments to JSON file."""
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tournaments], f, indent=4)

    def create_tournament(self, name, location, start_date, end_date, description=""):
        """Create a new tournament."""

        tournament = Tournament(
            name=name,
            location=location,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            current_round=0,
            rounds=[],
            number_of_rounds=4,
            players=[],
            description=description,
        )

        self.tournaments.append(tournament)
        self.save_tournaments()
        logger.info("Tournament '%s' created successfully.", name)
        self.view.display_message(f"Tournament '{name}' created!")

    def list_tournaments(self):
        """Show list of tournaments."""
        self.tournaments = self.load_tournaments()
        if not self.tournaments:
            self.view.display_no_tournaments()
        else:
            self.view.display_tournaments(self.tournaments)
        return self.tournaments

    def add_players(self, tournament: Tournament, player_ids: list[str]):
        """Add players to the given tournament using provided IDs."""
        existing_ids = {p.id_national for p in tournament.players}

        for player_id in player_ids:
            if player_id in existing_ids:
                self.view.display_player_already_registered()
                continue
            player = self.player_controller.find_player_by_id(player_id)
            if player:
                tournament.players.append(player)
                existing_ids.add(player.id_national)
                self.view.display_player_added(player)
            else:
                self.view.display_player_not_found()

        self.save_tournaments()
        self.view.display_total_players(tournament)

    def start_round(self, tournament=None):
        """Start the next round of the given tournament (or last one if None)."""
        if tournament is None:
            tournaments = self.load_tournaments()
            if not tournaments:
                self.view.display_message("No tournaments exist. Create one first.")
                return

            tournament = tournaments[-1]

        if tournament.rounds and not tournament.rounds[-1].is_complete():
            self.view.display_message(
                "You must enter all results before starting a new round."
            )
            return

        if tournament.current_round >= tournament.number_of_rounds:
            self.view.display_message(
                "All rounds have been played. Tournament finished."
            )
            return

        if not tournament.players:
            self.view.display_message("Cannot start a round. No players registered.")
            return

        if len(tournament.players) % 2 != 0:
            self.view.display_message("Even number of players required.")
            return

        players = tournament.players
        if tournament.current_round > 0:
            players.sort(key=lambda p: p.score, reverse=True)
        else:
            random.shuffle(players)

        matches = []
        to_pair = players[:]

        while to_pair:
            player_white = to_pair.pop(0)
            for i, player_black in enumerate(to_pair):
                already_played = any(
                    player_white.id_national
                    in {m.player_white.id_national, m.player_black.id_national}
                    and player_black.id_national
                    in {m.player_white.id_national, m.player_black.id_national}
                    for r in tournament.rounds
                    for m in r.matches
                )
                if not already_played:
                    matches.append(Match(player_white, player_black, [0, 0]))
                    to_pair.pop(i)
                    break

        new_round = Round(tournament.current_round + 1)
        new_round.matches = matches
        tournament.rounds.append(new_round)
        tournament.current_round += 1
        self.save_tournaments()
        self.view.display_rounds_and_matches(tournament)

    def enter_results(self, tournament=None, current_round=None, results=None):
        """Enter results for a specific tournament and round."""
        tournaments = self.load_tournaments()
        if not tournaments:
            self.view.display_message("No tournaments exist.")
            return

        if tournament is None:
            tournament = tournaments[-1]

        if not tournament.rounds:
            self.view.display_message("No rounds started yet.")
            return

        if current_round is None:
            current_round = tournament.rounds[-1]

        if results is None:
            results = self.view.prompt_results_for_round(current_round)

        for match, score in zip(current_round.matches, results):
            match.score = score
            if score == [1, 0]:
                match.player_white.score += 1
            elif score == [0, 1]:
                match.player_black.score += 1
            else:
                match.player_white.score += 0.5
                match.player_black.score += 0.5

        current_round.close()
        self.save_tournaments()
        self.view.display_results(tournament)

    def show_standings(self):
        """Display current standings for the last tournament."""
        tournaments = self.load_tournaments()
        if not tournaments:
            self.view.display_message("No tournaments exist.")
            return

        tournament = tournaments[-1]

        for player in tournament.players:
            player.score = 0.0
        for rnd in tournament.rounds:
            for match in rnd.matches:
                match.player_white.score += match.score[0]
                match.player_black.score += match.score[1]

        self.view.display_standings(tournament)

    def export_full_tournament_report_html(
        self, tournament, filename="tournament_report.html"
    ):
        """Export full tournament report to HTML, including rounds and standings."""
        sorted_players = sorted(
            tournament.players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower()),
        )
        sorted_standings = sorted(
            tournament.players,
            key=lambda p: (-p.score, p.last_name.lower(), p.first_name.lower()),
        )

        scores = {player.id_national: player.score for player in tournament.players}

        env = Environment(loader=PackageLoader("chess", "templates"))
        template = env.get_template("tournament_report.html.j2")

        html_content = template.render(
            tournament=tournament,
            sorted_players=sorted_players,
            sorted_standings=sorted_standings,
            scores=scores,
        )

        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.view.display_message(
            f"Full tournament HTML report exported successfully: {filepath}"
        )

    def export_report(self):
        """Export the last created tournament to HTML."""
        tournaments = self.load_tournaments()
        if not tournaments:
            self.view.display_message("No tournaments exist.")
            return
        tournament = tournaments[-1]
        filename = f"{tournament.name.replace(' ', '_')}_report.html"
        self.export_full_tournament_report_html(tournament, filename)
