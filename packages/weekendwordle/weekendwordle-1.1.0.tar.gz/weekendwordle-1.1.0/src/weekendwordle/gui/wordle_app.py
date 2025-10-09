"""
Main application file for the Wordle Solver GUI.

This script sets up the Textual application and manages the different screens.
"""

from textual.app import App
# import argparse
from .startup.startup_screen import StartupScreen
from ..config import APP_COLORS
from ..config_loader import load_config, translate_for_gui

class WordleApp(App):
    """The main application class for the Wordle Solver."""

    # CSS_PATH = "wordle_app.tcss"
    
    # Define keybindings that work across all screens
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, config_data = {}, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config_data = config_data

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return APP_COLORS

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        # Start with the startup screen
        self.push_screen(StartupScreen())

def run_gui():
    app = WordleApp(config_data=translate_for_gui(load_config(no_gui=False)))
    app.run()

if __name__ == "__main__":
    run_gui()
