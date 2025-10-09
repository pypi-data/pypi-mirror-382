"""View for displaying the main menu and handling user interactions."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MenuView:
    """Handles the main menu and interactive submenus for the Chess Tournament."""

    def __init__(
        self,
        player_controller,
        match_controller,
        tournament_controller,
        tournament_view,
    ):
        """Initialize MenuView with controllers."""
        self.player_controller = player_controller
        self.match_controller = match_controller
        self.tournament_controller = tournament_controller
        self.tournament_view = tournament_view
        self.running = True

        self.menu_options = [
            ("1", "Manage players", self.manage_players),
            ("2", "Manage matches", self.manage_matches),
            ("3", "Manage tournaments", self.manage_tournaments),
            ("0", "Exit", self.exit_app),
        ]

    def display_menu(self):
        """Display main menu and handle choices until exit."""
        while self.running:
            print("\n=== Chess Tournament Menu ===")
            for key, desc, _ in self.menu_options:
                print(f"{key}. {desc}")
            choice = input("Enter your choice: ").strip()
            self.handle_choice(choice)

    def handle_choice(self, choice):
        """Execute the selected action from the main menu."""
        for key, _, action in self.menu_options:
            if choice == key:
                action()
                return
        print(" Invalid choice, try again.")

    def add_player(self):
        """Interactively add a player."""
        player_id = input("National ID (2 capital letters and 5 digits): ").strip()
        if not player_id or not player_id.isalnum() or len(player_id) != 7:
            print(" Invalid ID format (ex: AB12345).")
            return
        if self.player_controller.player_exists(player_id):
            print(" Player with this ID already exists.")
            return

        last_name = input("Enter last name: ").strip()
        first_name = input("Enter first name: ").strip()
        birth_date_str = input("Enter birth date (YYYY-MM-DD): ").strip()

        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                print(" Invalid date format.")
                return

        self.player_controller.add_player(
            id_national=player_id,
            last_name=last_name,
            first_name=first_name,
            birthdate=birth_date,
        )
        print(f" Player {first_name} {last_name} added.")

    def list_players(self):
        """Display all registered players."""
        players = self.player_controller.list_players()
        if not players:
            print("No players.")
            return
        print("=== Registered Players ===")
        for p in players:
            print(
                f"- {p.last_name} {p.first_name} | ID: {p.id_national} | "
                f"Birthdate: {p.birth_date}"
            )

    def list_matches(self):
        """Display all matches."""
        matches = self.match_controller.list_matches()

        if not matches:
            print("No matches recorded.")
            return

        print("=== Recorded Matches ===")
        for i, match in enumerate(matches, start=1):
            player_white = match.player_white
            player_black = match.player_black
            score = match.score

            if score == [1, 0]:
                score_str = "1-0"
            elif score == [0, 1]:
                score_str = "0-1"
            else:
                score_str = "0.5-0.5"

            print(
                f"Match {i}: {player_white.first_name} {player_white.last_name} "
                f"vs {player_black.first_name} {player_black.last_name} | "
                f"Result: {score_str}"
            )

    def list_tournaments(self):
        """Display all tournaments."""
        self.tournament_controller.list_tournaments()

    def show_standings(self):
        """Show tournament standings."""
        self.tournament_controller.show_standings()

    def manage_players(self):
        """Player submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Add a player", self.add_player),
            "2": ("List players", self.list_players),
            "0": ("Back", None),
        }
        self._interactive_submenu("Player Menu", submenu)

    def manage_matches(self):
        """Match submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Create a match", self.match_controller.interactive_create_match),
            "2": ("List matches", self.list_matches),
            "0": ("Back", None),
        }
        self._interactive_submenu("Match Menu", submenu)

    def manage_tournaments(self):
        """Tournament submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Create a tournament", self.interactive_create_tournament),
            "2": ("List tournaments", self.list_tournaments),
            "3": ("Add players", self.interactive_add_players_to_tournament),
            "4": ("Start round", self.interactive_start_round),
            "5": ("Enter results", self.interactive_enter_results),
            "6": ("Show standings", self.show_standings),
            "7": ("Export tournament report", self.tournament_controller.export_report),
            "0": ("Back", None),
        }
        self._interactive_submenu("Tournament Menu", submenu)

    # --- Wrappers qui collectent les inputs avant d’appeler le controller ---

    def interactive_create_tournament(self):
        """Collect input from the user and create a tournament."""
        name, location, start_date, end_date, description = (
            self.tournament_view.prompt_tournament_info()
        )
        self.tournament_controller.create_tournament(
            name=name,
            location=location,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

    def interactive_add_players_to_tournament(self):
        """Prompt for number of players and their IDs, then call controller."""
        tournaments = self.tournament_controller.list_tournaments()
        if not tournaments:
            self.tournament_view.display_no_tournaments()
            return

        # Choix du tournoi
        for i, t in enumerate(tournaments, start=1):
            print(f"{i}. {t.name}")
        idx_str = input("Select a tournament by number: ").strip()

        if not idx_str.isdigit() or int(idx_str) < 1 or int(idx_str) > len(tournaments):
            self.tournament_view.display_invalid_number()
            return
        tournament = tournaments[int(idx_str) - 1]

        # Nombre de joueurs
        num_players = self.tournament_view.prompt_number_of_players()
        if not num_players:
            return

        # Collecte des IDs
        player_ids = []
        for i in range(num_players):
            pid = self.tournament_view.prompt_player_id(i)
            player_ids.append(pid)

        # Appel du controller
        self.tournament_controller.add_players(tournament, player_ids)

    def interactive_start_round(self):
        """Start next round after checking conditions."""
        tournaments = self.tournament_controller.list_tournaments()
        if not tournaments:
            self.tournament_view.display_no_tournaments()
            return

        # Choix du tournoi
        for i, t in enumerate(tournaments, start=1):
            print(f"{i}. {t.name}")
        idx_str = input("Select a tournament by number: ").strip()
        if not idx_str.isdigit() or int(idx_str) < 1 or int(idx_str) > len(tournaments):
            self.tournament_view.display_invalid_number()
            return
        tournament = tournaments[int(idx_str) - 1]

        self.tournament_controller.start_round(tournament)

    def interactive_enter_results(self):
        """Prompt results for current round and pass them to controller."""
        tournaments = self.tournament_controller.list_tournaments()
        if not tournaments:
            self.tournament_view.display_no_tournaments()
            return

        # Choix du tournoi
        for i, t in enumerate(tournaments, start=1):
            print(f"{i}. {t.name}")
        idx_str = input("Select a tournament by number: ").strip()
        if not idx_str.isdigit() or int(idx_str) < 1 or int(idx_str) > len(tournaments):
            self.tournament_view.display_invalid_number()
            return
        tournament = tournaments[int(idx_str) - 1]

        # Vérification qu’il y a une ronde en cours
        if not tournament.rounds or not tournament.rounds[-1].is_complete():
            current_round = tournament.rounds[-1] if tournament.rounds else None
            if current_round is None or current_round.is_complete():
                self.tournament_view.display_incomplete_round_error()
                return

            # Collecte des résultats
            results = self.tournament_view.prompt_results_for_round(current_round)

            # Appel du controller
            self.tournament_controller.enter_results(tournament, current_round, results)

    def _interactive_submenu(self, title: str, submenu: dict):
        """
        Display a submenu once and execute the selected action.
        """
        print(f"\n=== {title} ===")
        for key, (desc, _) in submenu.items():
            print(f"{key}. {desc}")

        choice = input("Enter your choice: ").strip()
        if choice == "0":
            return

        if choice in submenu:
            _, action = submenu[choice]

            if action:
                action()
            self._interactive_submenu(title, submenu)
        else:
            print("Invalid choice.")
            self._interactive_submenu(title, submenu)

    def exit_app(self):
        """Exit the program."""
        print(" Goodbye!")
        self.running = False
