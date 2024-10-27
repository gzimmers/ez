import click
import subprocess
import sys
from .config import Config, RESERVED_COMMANDS

config = Config()

class EzCLI(click.MultiCommand):
    def list_commands(self, ctx):
        # Return built-in commands
        return RESERVED_COMMANDS

    def get_command(self, ctx, cmd_name):
        # Check for built-in commands first
        if cmd_name == 'save':
            @click.command()
            @click.argument('name')
            @click.argument('command')
            def save(name, command):
                """Save a command with the given name."""
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot save command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                config.add_command(name, command)
                click.echo(f"Saved command '{name}'")
            return save

        elif cmd_name == 'rename':
            @click.command()
            @click.argument('old_name')
            @click.argument('new_name')
            def rename(old_name, new_name):
                """Rename a command while preserving its aliases."""
                if new_name in RESERVED_COMMANDS:
                    click.echo(f"Cannot rename to '{new_name}': it is a reserved command name.", err=True)
                    sys.exit(1)
                if config.rename_command(old_name, new_name):
                    click.echo(f"Renamed command '{old_name}' to '{new_name}'")
                else:
                    click.echo(f"Command '{old_name}' not found or invalid new name.", err=True)
                    sys.exit(1)
            return rename

        elif cmd_name == 'alias':
            @click.command()
            @click.option('-d', '--delete', is_flag=True, help='Delete the alias')
            @click.argument('command_name')
            @click.argument('alias')
            def alias(delete, command_name, alias):
                """Add or remove an alias for a command."""
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
            @click.command()
            @click.argument('name')
            @click.argument('command')
            def append(name, command):
                """Append a command to an existing command sequence."""
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
            @click.command()
            @click.argument('name')
            def pop(name):
                """Remove the last command from a command sequence."""
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot pop from command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.pop_command(name):
                    click.echo(f"Removed last command from '{name}'")
                else:
                    click.echo(f"Command '{name}' not found or empty.", err=True)
                    sys.exit(1)
            return pop

        elif cmd_name == 'list':
            @click.command()
            def list():
                """List all saved commands."""
                commands = config.list_commands()
                if not commands:
                    click.echo("No commands saved.")
                    return

                click.echo("\n" + click.style("📋 Saved Commands", fg="blue", bold=True))
                click.echo(click.style("═" * 50, fg="blue"))

                for name, (cmds, aliases) in sorted(commands.items()):
                    # Command name header with aliases if present
                    header = f"▶ {name}"
                    if aliases:
                        alias_list = ", ".join(sorted(aliases))
                        header += click.style(f" (aliases: {alias_list})", fg="yellow")
                    click.echo("\n" + click.style(header, fg="green", bold=True))
                    
                    # Print each operation with proper indentation
                    for i, cmd in enumerate(cmds, 1):
                        # Operation number in cyan
                        num = click.style(f"{i}.", fg="cyan")
                        # Command in white
                        formatted_cmd = click.style(cmd, fg="white")
                        # Add indentation for better readability
                        click.echo(f"   {num} {formatted_cmd}")
                
                # Add a final newline for spacing
                click.echo()
            return list

        elif cmd_name == 'update':
            @click.command()
            @click.argument('name')
            @click.argument('command')
            def update(name, command):
                """Update an existing command."""
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot update command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.update_command(name, command):
                    click.echo(f"Updated command '{name}'")
                else:
                    click.echo(f"Command '{name}' not found.", err=True)
                    sys.exit(1)
            return update

        elif cmd_name == 'delete':
            @click.command()
            @click.argument('name')
            def delete(name):
                """Delete a saved command."""
                if name in RESERVED_COMMANDS:
                    click.echo(f"Cannot delete command: '{name}' is a reserved command name.", err=True)
                    sys.exit(1)
                if config.delete_command(name):
                    click.echo(f"Deleted command '{name}' and its aliases")
                else:
                    click.echo(f"Command '{name}' not found.", err=True)
                    sys.exit(1)
            return delete

        # If not a built-in command, check if it's a saved command
        cmds = config.get_command(cmd_name)
        if cmds:
            @click.command()
            def saved_command():
                """Run a saved command sequence."""
                for cmd in cmds:
                    try:
                        result = subprocess.run(cmd, shell=True)
                        if result.returncode != 0:
                            sys.exit(result.returncode)
                    except Exception as e:
                        click.echo(f"Error executing command: {e}", err=True)
                        sys.exit(1)
            return saved_command

        return None

@click.command(cls=EzCLI)
def cli():
    """ez-cmd - Save and replay commands easily."""
    pass

if __name__ == '__main__':
    cli()
