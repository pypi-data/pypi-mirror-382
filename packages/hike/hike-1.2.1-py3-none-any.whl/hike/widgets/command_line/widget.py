"""Provides a widget for getting input from the user."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from itertools import chain
from typing import Final

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import var
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, Rule
from textual.widgets.input import Selection

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding
from textual_enhanced.commands import Quit

##############################################################################
# Local imports.
from ...types import CommandHistory
from .base_command import InputCommand
from .change_directory import ChangeDirectoryCommand
from .general import (
    BookmarksCommand,
    ChangeLogCommand,
    ContentsCommand,
    DocumentCommand,
    HelpCommand,
    HistoryCommand,
    LocalCommand,
    QuitCommand,
    ReadMeCommand,
)
from .obsidian import ObsidianCommand
from .open_directory import OpenDirectoryCommand
from .open_file import OpenFileCommand
from .open_from_forge import (
    OpenFromBitbucket,
    OpenFromCodeberg,
    OpenFromForgeCommand,
    OpenFromGitHub,
    OpenFromGitLab,
)
from .open_url import OpenURLCommand

##############################################################################
COMMANDS: Final[tuple[type[InputCommand], ...]] = (
    # Keep the first three in order. A file match should win over a
    # directory should win over a URL.
    OpenFileCommand,
    OpenDirectoryCommand,
    OpenURLCommand,
    # Once the above are out of the way the order doesn't matter so much.
    BookmarksCommand,
    ChangeDirectoryCommand,
    DocumentCommand,
    HelpCommand,
    HistoryCommand,
    LocalCommand,
    ChangeLogCommand,
    OpenFromBitbucket,
    OpenFromCodeberg,
    OpenFromGitHub,
    OpenFromGitLab,
    ContentsCommand,
    ReadMeCommand,
    QuitCommand,
    ObsidianCommand,
)
"""The commands used for the input."""


##############################################################################
class CommandLine(Vertical):
    """A command line for getting input from the user."""

    DEFAULT_CSS = """
    CommandLine {
        height: 1;

        Label, Input {
            color: $text-muted;
        }

        &:focus-within {
            Label, Input {
                color: $text;
            }
            Label {
                text-style: bold;
            }
        }

        Rule {
            height: 1;
            margin: 0 !important;
            color: $foreground 10%;
            display: none;
        }

        Input, Input:focus {
            border: none;
            padding: 0;
            height: 1fr;
            background: transparent;
        }

        &.--top {
            dock: top;
            height: 2;
            Rule {
                display: block;
            }
        }
    }
    """

    HELP = """
    ## Command Line

    Use this command line to enter filenames, directories, URLs or commands. Entering
    a filename or a URL will open that file for viewing; entering a
    directory will open a file opening dialog starting at that location.

    | Command | Aliases | Arguments | Description |
    | --      | --      | --        | --          |
    {cli_commands}

    ### ¹Forge support

    The forge-oriented commands listed above accept a number of different
    ways of quickly specifying which file you want to view. Examples include:

    {commands}

    ### Special keys

    Special keys while in the command line:
    """.format(
        cli_commands="\n    ".join(sorted(command.help_text() for command in COMMANDS)),
        commands=OpenFromForgeCommand.HELP,
    )

    BINDINGS = [
        ("escape", "request_exit"),
        HelpfulBinding(
            "up",
            "history_previous",
            tooltip="Navigate backwards through the command history",
        ),
        HelpfulBinding(
            "down",
            "history_next",
            tooltip="Navigate forward through the command history",
        ),
    ]

    history: var[CommandHistory] = var(CommandHistory)
    """The command line history."""

    dock_top: var[bool] = var(False)
    """Should the input dock to the top of the screen?"""

    @property
    def _history_suggester(self) -> SuggestFromList:
        """A suggester for the history of input.

        If there us no history yet then a list of commands and aliases will
        be used.
        """
        return SuggestFromList(
            [
                # Start off with the history, with the most recently-used
                # commands first so suggestions come from the thing
                # most-recently done.
                *reversed(list(self.history)),
                # Tack known commands on the end; this means that the user
                # will get prompted for commands they've not used yet.
                *chain(*(command.suggestions() for command in COMMANDS)),
            ]
        )

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        with Horizontal():
            yield Label("> ")
            yield Input(
                placeholder="Enter a directory, file, path or command",
                suggester=self._history_suggester,
            )
        yield Rule(line_style="heavy")

    def _watch_history(self) -> None:
        """React to history being updated."""
        if self.is_mounted:
            self.query_one(Input).suggester = self._history_suggester

    def _watch_dock_top(self) -> None:
        """React to being asked to dock input to the top."""
        self.set_class(self.dock_top, "--top")

    @dataclass
    class HistoryUpdated(Message):
        """Message posted when the command history is updated."""

        command_line: CommandLine
        """The command line whose history was updated."""

    def handle_input(self, command: str) -> None:
        """Handle input from the user.

        Args:
            command: The command the user entered.
        """
        if not (command := command.strip()):
            return
        for candidate in COMMANDS:
            if candidate.handle(command, self):
                self.history.add(command)
                self.post_message(self.HistoryUpdated(self))
                self.query_one(Input).value = ""
                self.query_one(Input).suggester = self._history_suggester
                return
        self.notify("Unable to handle that input", title="Error", severity="error")

    @on(Input.Submitted)
    def _handle_input(self, message: Input.Submitted) -> None:
        """Handle input from the user.

        Args:
            message: The message requesting input is handled.
        """
        message.stop()
        self.handle_input(message.value)

    def action_request_exit(self) -> None:
        """Request that the application quits."""
        if self.query_one(Input).value:
            self.query_one(Input).value = ""
            self.history.goto_end()
        else:
            self.post_message(Quit())

    def action_history_previous(self) -> None:
        """Move backwards through the command line history."""
        if value := self.history.current_item:
            self.query_one(Input).value = value
            self.query_one(Input).selection = Selection(0, len(value))
            self.history.backward()

    def action_history_next(self) -> None:
        """Move forwards through the command line history."""
        if self.history.forward() and (value := self.history.current_item) is not None:
            self.query_one(Input).value = value
            self.query_one(Input).selection = Selection(0, len(value))
        else:
            self.query_one(Input).value = ""


### widget.py ends here
