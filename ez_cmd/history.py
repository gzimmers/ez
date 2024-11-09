"""History command implementation"""
import click
import sys
from pathlib import Path
from .config import Config, RESERVED_COMMANDS

def create_replay_command(config: Config):
    @click.command(help="Save a command from shell history. Optionally filter by text.", 
                  short_help="Save from history")
    @click.argument('name')
    @click.argument('filter_text', required=False)
    def replay(name, filter_text):
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
                    # If filter_text is provided, only include commands that contain it
                    if not filter_text or filter_text.lower() in cmd.lower():
                        commands.append(cmd)

            # Reverse to show most recent first
            commands = list(reversed(commands))

            if not commands:
                if filter_text:
                    click.echo(f"No commands found matching '{filter_text}'.", err=True)
                else:
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
                if filter_text:
                    click.echo(click.style(f"Filtered by: {filter_text}", fg="yellow"))
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
