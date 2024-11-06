"""Installation command implementation"""
import click
import sys
from pathlib import Path

def create_install_command():
    @click.command(help="Add 'setopt INC_APPEND_HISTORY' to your .zshrc file if it's not already present", 
                  short_help="Install shell settings")
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
