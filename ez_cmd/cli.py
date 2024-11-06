import click
import subprocess
import sys
from .config import Config, RESERVED_COMMANDS
import os
from pathlib import Path
import re

config = Config()

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
  ez-cmd copy greet hello                 # Copy 'greet' command to 'hello'
  ez-cmd list                            # Show all saved commands"""

class EzCLI(click.MultiCommand):
    def list_commands(self, ctx):
        # Return built-in commands
        commands = RESERVED_COMMANDS.copy()
        commands.add('replay')
        commands.add('install')  # Added 'install' to the list of commands
        commands.add('copy')     # Added 'copy' to the list of commands
        return sorted(commands)

    def get_command(self, ctx, cmd_name):
        # Check for built-in commands first
        if cmd_name == 'save' or cmd_name == 's':
            @click.command(help="Save a new command (use {0}, {1}, etc. for arguments)", short_help="Save a new command")
            @click.argument('name')
            @click.argument('command')
            def save(name, command):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot save command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                config.add_command(name, command)
                click.echo(f"Saved command '{name}'")
            return save

        elif cmd_name == 'update' or cmd_name == "u":
            @click.command(help="Update an existing command", short_help="Update an existing command")
            @click.argument('name')
            @click.argument('command')
            def update(name, command):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot update command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.update_command(name, command):
                    click.echo(f"Updated command '{name}'")
                else:
                    click.echo(f"Command '{name}' not found.", err=True)
                    sys.exit(1)
            return update

        elif cmd_name == 'delete' or cmd_name == 'd':
            @click.command(help="Delete a command and its aliases", short_help="Delete a command")
            @click.argument('name')
            def delete(name):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot delete command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.delete_command(name):
                    click.echo(f"Deleted command '{name}' and its aliases")
                else:
                    click.echo(f"Command '{name}' not found.", err=True)
                    sys.exit(1)
            return delete

        elif cmd_name == 'rename' or cmd_name == 'r':
            @click.command(help="Rename a command while keeping its aliases", short_help="Rename a command")
            @click.argument('old_name')
            @click.argument('new_name')
            def rename(old_name, new_name):
                if new_name in RESERVED_COMMANDS:
                    click.echo(f"Cannot rename to '{new_name}': it is a reserved command name.", err=True)
                    sys.exit(1)
                if config.rename_command(old_name, new_name):
                    click.echo(f"Renamed command '{old_name}' to '{new_name}'")
                else:
                    click.echo(f"Command '{old_name}' not found or invalid new name.", err=True)
                    sys.exit(1)
            return rename

        elif cmd_name == 'alias' or cmd_name == 'a':
            @click.command(help="Add or remove command aliases", short_help="Manage command aliases")
            @click.option('-d', '--delete', is_flag=True, help='Delete the alias')
            @click.argument('command_name')
            @click.argument('alias')
            def alias(delete, command_name, alias):
                if alias in RESERVED_COMMANDS:
                    click.echo(f"Cannot use '{alias}' as an alias: it is a reserved command name.", err=True)
                    sys.exit(1)

                if delete:
                    if config.remove_alias(command_name, alias):
                        click.echo(f"Removed alias '{alias}' from command '{command_name}'")
                    else:
                        click.echo(f"Alias '{alias}' not found for command '{command_name}'", err=True)
                        sys.exit(1)
                else:
                    if config.add_alias(command_name, alias):
                        click.echo(f"Added alias '{alias}' for command '{command_name}'")
                    else:
                        click.echo(f"Command '{command_name}' not found", err=True)
                        sys.exit(1)
            return alias

        elif cmd_name == 'append':
            @click.command(help="Add a command to an existing sequence", short_help="Add to command sequence")
            @click.argument('name')
            @click.argument('command')
            def append(name, command):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot append to command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.append_command(name, command):
                    click.echo(f"Appended command to '{name}'")
                else:
                    click.echo(f"Command '{name}' not found.", err=True)
                    sys.exit(1)
            return append

        elif cmd_name == 'pop':
            @click.command(help="Remove the last command from a sequence", short_help="Remove from sequence")
            @click.argument('name')
            def pop(name):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot pop from command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.pop_command(name):
                    click.echo(f"Removed last command from '{name}'")
                else:
                    click.echo(f"Command '{name}' not found or empty.", err=True)
                    sys.exit(1)
            return pop

        elif cmd_name == 'list' or cmd_name == 'ls':
            @click.command(help="Show all saved commands", short_help="List all commands")
            def list_commands():
                commands = config.list_commands()
                if not commands:
                    click.echo("No commands saved.")
                    return

                click.echo("\n" + click.style("📋 Saved Commands", fg="blue", bold=True))
                click.echo(click.style("═" * 50, fg="blue"))

                # Group commands by type (single vs sequence)
                single_commands = {name: (cmds, aliases) for name, (cmds, aliases) in commands.items() if len(cmds) == 1}
                sequences = {name: (cmds, aliases) for name, (cmds, aliases) in commands.items() if len(cmds) > 1}

                # Print single commands
                if single_commands:
                    click.echo("\n" + click.style("Single Commands:", fg="cyan", bold=True))
                    for name, (cmds, aliases) in sorted(single_commands.items()):
                        header = f"▶ {name}"
                        if aliases:
                            alias_list = ", ".join(sorted(aliases))
                            header += click.style(f" (aliases: {alias_list})", fg="yellow")
                        click.echo(click.style(header, fg="green"))
                        click.echo(f"   {click.style(cmds[0], fg='white')}")

                # Print command sequences
                if sequences:
                    click.echo("\n" + click.style("Command Sequences:", fg="cyan", bold=True))
                    for name, (cmds, aliases) in sorted(sequences.items()):
                        header = f"▶ {name}"
                        if aliases:
                            alias_list = ", ".join(sorted(aliases))
                            header += click.style(f" (aliases: {alias_list})", fg="yellow")
                        click.echo(click.style(header, fg="green"))
                        for i, cmd in enumerate(cmds, 1):
                            click.echo(f"   {click.style(f'{i}.', fg='cyan')} {click.style(cmd, fg='white')}")

                click.echo()
            return list_commands

        elif cmd_name == 'replay':
            @click.command(help="Save a command from shell history", short_help="Save from history")
            @click.argument('name')
            def replay(name):
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot save command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)

                history_file = Path.home() / ".zsh_history"
                if not history_file.exists():
                    click.echo("Could not find zsh history file.", err=True)
                    sys.exit(1)

                try:
                    # Read zsh history file
                    with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    # Parse each line as a command
                    commands = []
                    for line in lines:
                        cmd = line.strip()
                        # Skip empty commands and ez commands
                        if cmd and not cmd.startswith('ez '):
                            commands.append(cmd)

                    # Reverse to show most recent first
                    commands = list(reversed(commands))

                    if not commands:
                        click.echo("No commands found in history.", err=True)
                        sys.exit(1)

                    # Show commands with pagination
                    page = 0
                    page_size = 5
                    while True:
                        click.clear()
                        start_idx = page * page_size
                        end_idx = start_idx + page_size
                        current_commands = commands[start_idx:end_idx]

                        click.echo(click.style("\nRecent Commands:", fg="blue", bold=True))
                        click.echo(click.style("═" * 50, fg="blue"))
                        
                        for idx, cmd in enumerate(current_commands, start=1):
                            click.echo(f"{click.style(str(idx), fg='green')}. {click.style(cmd, fg='white')}")

                        click.echo("\nActions:")
                        click.echo("1-5: Select command")
                        if start_idx > 0:
                            click.echo("p: Previous page")
                        if end_idx < len(commands):
                            click.echo("n: Next page")
                        click.echo("q: Quit")

                        choice = click.prompt("Choose an action", type=str).lower()

                        if choice == 'q':
                            sys.exit(0)
                        elif choice == 'n' and end_idx < len(commands):
                            page += 1
                        elif choice == 'p' and start_idx > 0:
                            page -= 1
                        elif choice.isdigit() and 1 <= int(choice) <= len(current_commands):
                            selected_cmd = current_commands[int(choice) - 1]
                            config.add_command(name, selected_cmd)
                            click.echo(f"\nSaved command '{name}': {selected_cmd}")
                            break
                        else:
                            click.echo("Invalid choice. Please try again.")
                except Exception as e:
                    click.echo(f"Error reading history: {str(e)}", err=True)
                    sys.exit(1)
            return replay

        elif cmd_name == 'install':
            @click.command(help="Add 'setopt INC_APPEND_HISTORY' to your .zshrc file if it's not already present", short_help="Install shell settings")
            def install():
                zshrc_path = Path.home() / ".zshrc"
                try:
                    if zshrc_path.exists():
                        with open(zshrc_path, 'r') as f:
                            lines = f.readlines()
                        if any('setopt INC_APPEND_HISTORY' in line for line in lines):
                            click.echo("`setopt INC_APPEND_HISTORY` is already set in your `.zshrc` file.")
                        else:
                            with open(zshrc_path, 'a') as f:
                                f.write('\nsetopt INC_APPEND_HISTORY\n')
                            click.echo("Successfully added `setopt INC_APPEND_HISTORY` to your `.zshrc` file.")
                    else:
                        with open(zshrc_path, 'w') as f:
                            f.write('setopt INC_APPEND_HISTORY\n')
                        click.echo("`.zshrc` file not found. Created and added `setopt INC_APPEND_HISTORY`.")
                except Exception as e:
                    click.echo(f"Failed to update `.zshrc`: {e}", err=True)
                    sys.exit(1)
            return install

        elif cmd_name == 'copy' or cmd_name == 'c':
            @click.command(help="Copy an existing command to a new name", short_help="Copy a command")
            @click.argument('old_name')
            @click.argument('new_name')
            def copy(old_name, new_name):
                if old_name in RESERVED_COMMANDS:
                    click.echo(f"Cannot copy command: '{old_name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if new_name in RESERVED_COMMANDS:
                    click.echo(f"Cannot copy to '{new_name}': it is a reserved command name.", err=True)
                    sys.exit(1)
                if config.copy_command(old_name, new_name):
                    click.echo(f"Copied command '{old_name}' to '{new_name}'")
                else:
                    click.echo(f"Failed to copy command '{old_name}'. It may not exist or the new name '{new_name}' is already in use.", err=True)
                    sys.exit(1)
            return copy

        cmds = config.get_command(cmd_name)
        if cmds:
            @click.command(context_settings=dict(
                ignore_unknown_options=True,
            ))
            @click.argument('args', nargs=-1, type=click.UNPROCESSED)
            def saved_command(args):
                """Run a saved command sequence with arguments."""
                for cmd in cmds:
                    try:
                        # Use str.format to replace placeholders
                        formatted_cmd = cmd.format(*args)
                        result = subprocess.run(formatted_cmd, shell=True)
                        if result.returncode != 0:
                            sys.exit(result.returncode)
                    except IndexError:
                        click.echo(f"Error: Not enough arguments provided for command '{cmd}'", err=True)
                        sys.exit(1)
                    except Exception as e:
                        click.echo(f"Error executing command: {e}", err=True)
                        sys.exit(1)
            return saved_command

        return None

@click.command(cls=EzCLI, help=HELP_TEXT)
def cli():
    pass

if __name__ == '__main__':
    cli()
