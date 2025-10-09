"""
Defines the sidebar and its child components for the Wordle Solver UI.

- ResultsTable: A DataTable widget to display word suggestions and scores.
- StatsTable: A DataTable to display miscellaneous game statistics.
- Sidebar: a container for the ResultsTable and StatsTable.
"""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static

from ...backend.core import WordleGame
from ...config import EVENTS

class ResultsTable(Static):
    """A DataTable widget to display word suggestions."""
    
    BORDER_TITLE = "Top Computer Answers"

    def compose(self) -> ComposeResult:
        """Creates the table and its columns."""
        yield DataTable(zebra_stripes = True, cursor_type = 'row')

    def on_mount(self) -> None:
        """Adds columns to the table."""
        table = self.query_one(DataTable)
        table.add_columns("Rank", "Word", "Avrg.", "Total", "Notes")

    def update_data(self, game_obj: WordleGame, sorted_results: list[tuple[str, float]], recommendation: str) -> None:
        """Clears and repopulates the table with new results."""
        table = self.query_one(DataTable)
        table.clear()
        
        answers_remaining = len(game_obj.ans_idxs[-1])
        if answers_remaining == 0:
            return

        max_len = len(str(int(max(score for _, score in sorted_results)))) if sorted_results else 1

        for i, (word, score) in enumerate(sorted_results):
            annotation = ""
            if word in set(game_obj.current_answer_set):
                annotation = "\u2731"
            
            # Use score/answers_remaining for the score column, and the raw score in notes
            average_guesses = f"{score/answers_remaining:.4f}"
            total_guesses = f"{score:<{max_len}}"

            table.add_row(str(i + 1), word.upper(), average_guesses, total_guesses, annotation)
        
        if sorted_results:
            try:
                # Find the index of the recommended word in the list
                word_list = [word for word, _ in sorted_results]
                target_row = word_list.index(recommendation)
            except ValueError:
                # Fallback to the first row if the recommendation isn't found
                target_row = 0
            table.move_cursor(row=target_row)


class StatsTable(Static):
    """A widget to display miscellaneous game statistics."""

    BORDER_TITLE = "Stats"

    def compose(self) -> ComposeResult:
        """Creates the stats table."""
        yield DataTable(cursor_type = 'none', zebra_stripes = True)

    def on_mount(self) -> None:
        """Populates the stats table."""
        table = self.query_one(DataTable)
        # table.cursor_type = 'none'
        table.add_columns("Statistic", "Value")
        table.can_focus = False
        # table.zebra_stripes = True

    def update_data(self, event_counts, game_obj: WordleGame) -> None:
        """Clears and repopulates the table with new stats."""
        table = self.query_one(DataTable)
        table.clear()

        table.add_row("Possible answers", f"{len(game_obj.current_answer_set):,}")

        for name, description in EVENTS:
            value = getattr(event_counts, name)
            table.add_row(description, f"{value:,}")

        if game_obj.cache:
            table.add_row("Cache entries", f"{game_obj.cache.nentries():,}")
            table.add_row("Cache segments", f"{game_obj.cache.nsegments():,}")


class Sidebar(Vertical):
    """The sidebar container widget."""

    def compose(self) -> ComposeResult:
        """Renders the sidebar's tables."""
        yield ResultsTable()
        yield StatsTable()
