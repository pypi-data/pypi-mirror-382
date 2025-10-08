"""View for displaying tournaments and their details."""

from chess.models.match import Match


class TournamentView:
    """View for displaying tournaments and their details."""

    def display_no_tournaments(self):
        """Display a message when no tournaments exist."""
        print("No tournaments registered.")

    def display_adding_players(self, tournament):
        """Display a message indicating players are being added to a tournament."""
        print(f"Adding players to tournament '{tournament.name}'.")

    def display_invalid_number(self):
        """Display a message indicating the entered number is invalid."""
        print("Invalid number entered.")

    def display_empty_id_error(self):
        """Display a message indicating the player ID cannot be empty."""
        print("Player ID cannot be empty.")

    def display_player_already_registered(self):
        """Display a message indicating the player is already registered."""
        print("Player is already registered in this tournament.")

    def display_player_added(self, player):
        """Display a message confirming that a player has been added."""
        print(f"Player {player.last_name} {player.first_name} added successfully.")

    def display_player_not_found(self):
        """Display a message indicating the player was not found."""
        print("Player not found in the database.")

    def display_total_players(self, tournament):
        """Display the total number of players in the tournament."""
        print(
            f"Total players in tournament '{tournament.name}': "
            f"{len(tournament.players)}"
        )

    def display_tournaments(self, tournaments):
        """Display the list of tournaments with their details."""
        if not tournaments:
            self.display_no_tournaments()
            return
        print("=== List of Tournaments ===")
        for t in tournaments:
            print(
                f"- {t.name} ({t.location}), {t.start_date} → {t.end_date}, "
                f"{t.number_of_rounds} rounds"
            )

    def display_tournament_details(self, tournament):
        """Display the details of a selected tournament."""
        print(f"\n=== Tournament Details: {tournament.name} ===")
        print(f"Location: {tournament.location}")
        print(f"Dates: {tournament.start_date} → {tournament.end_date}")
        print(f"Number of rounds: {tournament.number_of_rounds}")

        print("\nRegistered Players:")
        if tournament.players:
            for player in tournament.players:
                print(
                    f"  - {player.last_name} {player.first_name} "
                    f"({player.id_national})"
                )
        else:
            print("  No players registered.")

        print("\nRounds:")
        if tournament.rounds:
            for rnd in tournament.rounds:
                print(f"  - {rnd.name} ({rnd.start_date} → {rnd.end_date})")
        else:
            print("  No rounds recorded.")

    def display_standings(self, tournament):
        """Display the standings of players for a given tournament."""
        if not tournament.players:
            print("No players to rank.")
            return

        print(f"\n=== Tournament Standings: {tournament.name} ===")
        sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
        for idx, player in enumerate(sorted_players, 1):
            print(f"{idx}. {player.last_name} {player.first_name} - {player.score} pts")

    def display_rounds_and_matches(self, tournament):
        """Display rounds and associated matches for each round."""
        if not tournament.rounds:
            print("No rounds to display.")
            return

        print(f"\n=== Rounds and Matches: {tournament.name} ===")
        for rnd in tournament.rounds:
            print(f"\nRound: {rnd.name} ({rnd.start_date} → {rnd.end_date})")
            if rnd.matches:
                for match in rnd.matches:
                    print(
                        f"  {match.player_white.last_name} "
                        f"vs {match.player_black.last_name} : {match.score}"
                    )
            else:
                print("  No matches recorded.")

    def display_results(self, tournament):
        """Display match results and player scores."""
        if not tournament.rounds:
            print("No results to display.")
            return

        print(f"\n=== Match Results: {tournament.name} ===")
        for rnd in tournament.rounds:
            print(f"\nRound: {rnd.name}")
            if rnd.matches:
                for match in rnd.matches:
                    print(
                        f"  {match.player_white.last_name} "
                        f"vs {match.player_black.last_name} : {match.score}"
                    )
            else:
                print("  No matches recorded.")

        print("\nPlayer Scores:")
        if tournament.players:
            for player in tournament.players:
                print(f"{player.last_name} {player.first_name} : {player.score} pts")
        else:
            print("  No players registered.")

    def display_incomplete_round_error(self):
        """Display a message when a round is not complete."""
        print("Cannot start next round. Please enter results for the current round.")

    def prompt_tournament_info(self):
        """Prompt the user for tournament information and return the details."""
        name = input("Tournament name: ").strip()
        location = input("Location: ").strip()
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        description = input("Description (optional): ").strip()
        return name, location, start_date, end_date, description

    def prompt_number_of_players(self):
        """Prompt the user for the number of players to add and return the number."""
        user_input = input("How many players do you want to add? ").strip()
        if user_input.isdigit() and int(user_input) > 0:
            return int(user_input)
        else:
            self.display_invalid_number()
            return None

    def prompt_player_id(self, i):
        """Prompt the user for a player's national ID and return it."""
        return input(f"Enter player's national ID {i+1}: ").strip()

    def prompt_match_result(self, match: Match):
        """Prompt the user for a match result and return a valid score list."""
        result_map = {"1": [1, 0], "2": [0, 1], "0": [0.5, 0.5]}
        while True:
            res = input(
                f"Result for {match.player_white.last_name}"
                f"vs {match.player_black.last_name}"
                f"(1=win, 2=loss, 0=draw): "
            ).strip()
            if res in result_map:
                return result_map[res]
            print("Invalid input. Use 0, 1, or 2.")

    def display_message(self, message: str):
        """Display a generic message."""
        print(message)

    def prompt_results_for_round(self, current_round):
        """Prompt the user to enter results for each match of the current round."""
        results = []
        print(f"\n--- Enter results for Round {current_round.round_no} ---")
        for i, match in enumerate(current_round.matches, start=1):
            print(
                f"Match {i}: {match.player_white.full_name()} (White) "
                f"vs {match.player_black.full_name()} (Black)"
            )
            print("Enter result: 1 for White win, 2 for Black win, 3 for Draw")
            choice = input("Your choice: ").strip()
            if choice == "1":
                results.append([1, 0])
            elif choice == "2":
                results.append([0, 1])
            else:
                results.append([0.5, 0.5])
        return results
