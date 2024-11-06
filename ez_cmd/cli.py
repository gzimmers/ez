import click
from pathlib import Path
from .config import Config, RESERVED_COMMANDS
from .commands import (
    create_save_command, create_update_command, create_delete_command,
    create_rename_command, create_alias_command, create_append_command,
    create_pop_command, create_list_command, create_saved_command
)
from .history import create_replay_command
from .install import create_install_command

HELP_TEXT = """Command-line tool for saving and managing shell commands.

Commands are organized into the following groups:

\b
Command Management:
  save (s) NAME CMD     Save a new command (use {0}, {1}, etc. for arguments)
  update (u) NAME CMD   Update an existing command
  delete (d) NAME       Delete a command and its aliases
  rename (r) OLD NEW    Rename a command while keeping its aliases
  copy (c) OLD NEW      Copy an existing command to a new name

\b
Alias Management:
  alias (a) NAME ALIAS          Add a alias for a command
  alias -d (a -d) NAME ALIAS    Remove a command alias

\b
Sequence Management:
  append NAME CMD      Add a command to an existing sequence
  pop NAME            Remove the last command from a sequence

\b
History Management:
  replay NAME         Save a command from shell history

\b
Utility:
  list (ls)           Show all saved commands

\b
Arguments:
  Commands can include argument placeholders ({0}, {1}, etc.)
  which are replaced when executing the command.

\b
Examples:
  ez-cmd save greet "echo Hello {0}"     # Save a command with a placeholder
  ez-cmd greet World                     # Run command: echo Hello World
  ez-cmd alias greet hi                  # Create alias 'hi' for 'greet'
  ez-cmd copy greet hello                # Copy 'greet' command to 'hello'
  ez-cmd list                            # Show all saved commands"""

class EzCLI(click.MultiCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()

    def list_commands(self, ctx):
        commands = RESERVED_COMMANDS.copy()
        commands.add('replay')
        commands.add('install')
        commands.add('copy')
        return sorted(commands)

    def get_command(self, ctx, cmd_name):
        command_map = {
            'save': lambda: create_save_command(self.config),
            's': lambda: create_save_command(self.config),
            'update': lambda: create_update_command(self.config),
            'u': lambda: create_update_command(self.config),
            'delete': lambda: create_delete_command(self.config),
            'd': lambda: create_delete_command(self.config),
            'rename': lambda: create_rename_command(self.config),
            'r': lambda: create_rename_command(self.config),
            'alias': lambda: create_alias_command(self.config),
            'a': lambda: create_alias_command(self.config),
            'append': lambda: create_append_command(self.config),
            'pop': lambda: create_pop_command(self.config),
            'list': lambda: create_list_command(self.config),
            'ls': lambda: create_list_command(self.config),
            'replay': lambda: create_replay_command(self.config),
            'install': create_install_command,
            'copy': lambda: create_rename_command(self.config),
            'c': lambda: create_rename_command(self.config),
        }

        if cmd_name in command_map:
            return command_map[cmd_name]()

        cmds = self.config.get_command(cmd_name)
        if cmds:
            return create_saved_command(self.config, cmds)

        return None

cli = click.command(cls=EzCLI, help=HELP_TEXT)(lambda: None)

if __name__ == '__main__':
    cli()
