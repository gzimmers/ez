import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Reserved command names that can't be saved
RESERVED_COMMANDS = {
    'save', 'list', 'update', 'delete', 'append', 'pop', 'alias', 
    'rename', 'ls', 'a', 'd', 'r', 's', 'u', 'replay'
}

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".ez-cmd"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_exists()
        self.commands = self._load_commands()
        self.aliases = self._load_aliases()

    def _ensure_config_exists(self):
        """Ensure the config directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._save_data({}, {})

    def _save_data(self, commands: Dict[str, List[str]], aliases: Dict[str, str]):
        """Save both commands and aliases to the config file."""
        data = {
            "commands": commands,
            "aliases": aliases
        }
        self.config_file.write_text(json.dumps(data, indent=2))

    def _load_commands(self) -> Dict[str, List[str]]:
        """Load commands from the config file."""
        try:
            data = json.loads(self.config_file.read_text())
            commands = data.get("commands", {})
            # Convert any string commands to lists for backward compatibility
            for name, cmd in commands.items():
                if isinstance(cmd, str):
                    commands[name] = [cmd]
            return commands
        except json.JSONDecodeError:
            return {}

    def _load_aliases(self) -> Dict[str, str]:
        """Load aliases from the config file."""
        try:
            data = json.loads(self.config_file.read_text())
            return data.get("aliases", {})
        except json.JSONDecodeError:
            return {}

    def _save(self):
        """Save current state to config file."""
        self._save_data(self.commands, self.aliases)

    def _get_primary_name(self, name: str) -> Optional[str]:
        """Get the primary name for a command (resolves aliases)."""
        return self.aliases.get(name, name)

    def _get_all_aliases(self, primary_name: str) -> Set[str]:
        """Get all aliases for a primary name."""
        return {name for name, target in self.aliases.items() if target == primary_name}

    def rename_command(self, old_name: str, new_name: str) -> bool:
        """Rename a primary command while preserving its aliases."""
        old_primary = self._get_primary_name(old_name)
        if old_primary not in self.commands or new_name in RESERVED_COMMANDS:
            return False

        # Update all aliases pointing to the old name
        for alias, target in list(self.aliases.items()):
            if target == old_primary:
                self.aliases[alias] = new_name

        # Move the command list to the new name
        self.commands[new_name] = self.commands.pop(old_primary)
        self._save()
        return True

    def add_command(self, name: str, command: str):
        """Add a new command."""
        self.commands[name] = [command]
        self._save()

    def add_alias(self, command_name: str, alias: str) -> bool:
        """Add an alias for a command."""
        primary_name = self._get_primary_name(command_name)
        if primary_name not in self.commands:
            return False
        self.aliases[alias] = primary_name
        self._save()
        return True

    def remove_alias(self, command_name: str, alias: str) -> bool:
        """Remove an alias for a command."""
        primary_name = self._get_primary_name(command_name)
        if primary_name not in self.commands or self.aliases.get(alias) != primary_name:
            return False
        del self.aliases[alias]
        self._save()
        return True

    def append_command(self, name: str, command: str) -> bool:
        """Append a command to an existing command sequence."""
        primary_name = self._get_primary_name(name)
        if primary_name not in self.commands:
            return False
        self.commands[primary_name].append(command)
        self._save()
        return True

    def pop_command(self, name: str) -> bool:
        """Remove the last command from a command sequence."""
        primary_name = self._get_primary_name(name)
        if primary_name not in self.commands or not self.commands[primary_name]:
            return False
        self.commands[primary_name].pop()
        if not self.commands[primary_name]:
            self.delete_command(primary_name)
        else:
            self._save()
        return True

    def get_command(self, name: str) -> Optional[List[str]]:
        """Get a command by name or alias."""
        primary_name = self._get_primary_name(name)
        return self.commands.get(primary_name)

    def list_commands(self) -> Dict[str, Tuple[List[str], Set[str]]]:
        """List all commands with their aliases."""
        result = {}
        for name, cmds in self.commands.items():
            aliases = self._get_all_aliases(name)
            result[name] = (cmds, aliases)
        return result

    def update_command(self, name: str, command: str) -> bool:
        """Update an existing command."""
        primary_name = self._get_primary_name(name)
        if primary_name not in self.commands:
            return False
        self.commands[primary_name] = [command]
        self._save()
        return True

    def delete_command(self, name: str) -> bool:
        """Delete a command and all its aliases."""
        primary_name = self._get_primary_name(name)
        if primary_name not in self.commands:
            return False
        
        # Remove all aliases pointing to this command
        aliases_to_remove = [alias for alias, target in self.aliases.items() 
                           if target == primary_name]
        for alias in aliases_to_remove:
            del self.aliases[alias]
        
        # Remove the command itself
        del self.commands[primary_name]
        self._save()
        return True

    def copy_command(self, old_name: str, new_name: str) -> bool:
        """Copy an existing command to a new name."""
        if new_name in RESERVED_COMMANDS or new_name in self.commands or new_name in self.aliases:
            return False
        primary_name = self._get_primary_name(old_name)
        if primary_name not in self.commands:
            return False
        self.commands[new_name] = self.commands[primary_name].copy()
        self._save()
        return True
