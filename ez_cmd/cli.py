import click
import subprocess
import sys
from .config import Config

config = Config()

@click.group()
def cli():
    """ez-cmd - Save and replay commands easily."""
    pass

@cli.command()
@click.argument('name')
@click.argument('command')
def save(name, command):
    """Save a command with the given name."""
    config.add_command(name, command)
    click.echo(f"Saved command '{name}'")

@cli.command()
def list():
    """List all saved commands."""
    commands = config.list_commands()
    if not commands:
        click.echo("No commands saved.")
        return
    
    click.echo("Saved commands:")
    for name, cmd in commands.items():
        click.echo(f"{name}: {cmd}")

@cli.command()
@click.argument('name')
@click.argument('command')
def update(name, command):
    """Update an existing command."""
    if config.update_command(name, command):
        click.echo(f"Updated command '{name}'")
    else:
        click.echo(f"Command '{name}' not found.", err=True)
        sys.exit(1)

@cli.command()
@click.argument('name')
def delete(name):
    """Delete a saved command."""
    if config.delete_command(name):
        click.echo(f"Deleted command '{name}'")
    else:
        click.echo(f"Command '{name}' not found.", err=True)
        sys.exit(1)

@cli.command()
@click.argument('name')
def run(name):
    """Run a saved command."""
    cmd = config.get_command(name)
    if cmd:
        try:
            # Use shell=True to support command chaining (&&, ||, |)
            result = subprocess.run(cmd, shell=True)
            sys.exit(result.returncode)
        except Exception as e:
            click.echo(f"Error executing command: {e}", err=True)
            sys.exit(1)
    else:
        click.echo(f"Command '{name}' not found.", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
