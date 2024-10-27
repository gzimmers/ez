import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".ez-cmd"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_exists()
        self.commands = self._load_commands()

    def _ensure_config_exists(self):
        """Ensure the config directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.config_file.write_text("{}")

    def _load_commands(self):
        """Load commands from the config file."""
        try:
            commands = json.loads(self.config_file.read_text())
            # Convert any string commands to lists for backward compatibility
            for name, cmd in commands.items():
                if isinstance(cmd, str):
                    commands[name] = [cmd]
            return commands
        except json.JSONDecodeError:
            return {}

    def _save_commands(self):
        """Save commands to the config file."""
        self.config_file.write_text(json.dumps(self.commands, indent=2))

    def add_command(self, name: str, command: str):
        """Add a new command."""
        self.commands[name] = [command]
        self._save_commands()

    def append_command(self, name: str, command: str):
        """Append a command to an existing command sequence."""
        if name in self.commands:
            self.commands[name].append(command)
            self._save_commands()
            return True
        return False

    def pop_command(self, name: str):
        """Remove the last command from a command sequence."""
        if name in self.commands and self.commands[name]:
            self.commands[name].pop()
            if not self.commands[name]:  # If no commands left, delete the entry
                del self.commands[name]
            self._save_commands()
            return True
        return False

    def get_command(self, name: str) -> list:
        """Get a command by name."""
        return self.commands.get(name)

    def list_commands(self):
        """List all commands."""
        return self.commands

    def update_command(self, name: str, command: str):
        """Update an existing command."""
        if name in self.commands:
            self.commands[name] = [command]
            self._save_commands()
            return True
        return False

    def delete_command(self, name: str):
        """Delete a command."""
        if name in self.commands:
            del self.commands[name]
            self._save_commands()
            return True
        return False
