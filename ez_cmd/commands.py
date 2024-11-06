"""Command definitions for the CLI"""
import click
import subprocess
import sys
from pathlib import Path
from typing import List
from .config import Config, RESERVED_COMMANDS

def create_save_command(config: Config):
    @click.command(help="Save a new command (use {0}, {1}, etc. for arguments)", 
                  short_help="Save a new command")
    @click.argument('name')
    @click.argument('command')
    def save(name, command):
        if name in RESERVED_COMMANDS:
            click.echo(f"Cannot save command: '{name}' is a reserved command name.", err=True)
            sys.exit(1)
        config.add_command(name, command)
        click.echo(f"Saved command '{name}'")
    return save

def create_update_command(config: Config):
    @click.command(help="Update an existing command", 
                  short_help="Update an existing command")
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

def create_delete_command(config: Config):
    @click.command(help="Delete a command and its aliases", 
                  short_help="Delete a command")
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

def create_rename_command(config: Config):
    @click.command(help="Rename a command while keeping its aliases", 
                  short_help="Rename a command")
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

def create_alias_command(config: Config):
    @click.command(help="Add or remove command aliases", 
                  short_help="Manage command aliases")
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

def create_append_command(config: Config):
    @click.command(help="Add a command to an existing sequence", 
                  short_help="Add to command sequence")
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

def create_pop_command(config: Config):
    @click.command(help="Remove the last command from a sequence", 
                  short_help="Remove from sequence")
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

def create_list_command(config: Config):
    @click.command(help="Show all saved commands", 
                  short_help="List all commands")
    def list_commands():
        commands = config.list_commands()
        if not commands:
            click.echo("No commands saved.")
            return

        click.echo("\n" + click.style("📋 Saved Commands", fg="blue", bold=True))
        click.echo(click.style("═" * 50, fg="blue"))

        # Group commands by type (single vs sequence)
        single_commands = {name: (cmds, aliases) for name, (cmds, aliases) in commands.items() 
                         if len(cmds) == 1}
        sequences = {name: (cmds, aliases) for name, (cmds, aliases) in commands.items() 
                    if len(cmds) > 1}

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

def create_saved_command(config: Config, cmds: List[str]):
    @click.command(context_settings=dict(
        ignore_unknown_options=True,
    ))
    @click.argument('args', nargs=-1, type=click.UNPROCESSED)
    def saved_command(args):
        """Run a saved command sequence with arguments."""
        for cmd in cmds:
            try:
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
