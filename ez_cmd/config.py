import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Reserved command names that can't be saved
RESERVED_COMMANDS = {
    'save', 'list', 'update', 'delete', 'append', 'pop', 'alias', 
    'rename', 'ls', 'a', 'd', 'r', 's', 'u', 'replay'
}

class ConfigFileManager:
    """Handles file operations for configuration management"""
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"

    def ensure_config_exists(self):
        """Ensure the config directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.save_data({}, {})

    def save_data(self, commands: Dict[str, List[str]], aliases: Dict[str, str]):
        """Save both commands and aliases to the config file."""
        data = {
            "commands": commands,
            "aliases": aliases
        }
        self.config_file.write_text(json.dumps(data, indent=2))

    def load_data(self) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
        """Load data from the config file."""
        try:
            data = json.loads(self.config_file.read_text())
            commands = data.get("commands", {})
            aliases = data.get("aliases", {})
            
            # Convert any string commands to lists for backward compatibility
            for name, cmd in commands.items():
                if isinstance(cmd, str):
                    commands[name] = [cmd]
            
            return commands, aliases
        except json.JSONDecodeError:
            return {}, {}

class CommandValidator:
    """Handles validation logic for commands"""
    @staticmethod
    def is_valid_new_name(name: str, commands: Dict[str, List[str]], aliases: Dict[str, str]) -> bool:
        """Check if a name is valid for a new command."""
        return name not in RESERVED_COMMANDS and name not in commands and name not in aliases

    @staticmethod
    def is_valid_existing_name(name: str, commands: Dict[str, List[str]]) -> bool:
        """Check if a name exists as a valid command."""
        return name in commands

class Config:
    def __init__(self):
        self.file_manager = ConfigFileManager(Path.home() / ".ez-cmd")
        self.validator = CommandValidator()
        self.file_manager.ensure_config_exists()
        self.commands, self.aliases = self.file_manager.load_data()

    def _save(self):
        """Save current state to config file."""
        self.file_manager.save_data(self.commands, self.aliases)

    def _get_primary_name(self, name: str) -> str:
        """Get the primary name for a command (resolves aliases)."""
        return self.aliases.get(name, name)

    def _get_all_aliases(self, primary_name: str) -> Set[str]:
        """Get all aliases for a primary name."""
        return {name for name, target in self.aliases.items() if target == primary_name}

    def _remove_command_aliases(self, primary_name: str):
        """Remove all aliases for a given command."""
        aliases_to_remove = [alias for alias, target in self.aliases.items() 
                           if target == primary_name]
        for alias in aliases_to_remove:
            del self.aliases[alias]

    # Command Management Methods
    def add_command(self, name: str, command: str):
        """Add a new command."""
        self.commands[name] = [command]
        self._save()

    def update_command(self, name: str, command: str) -> bool:
        """Update an existing command."""
        primary_name = self._get_primary_name(name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands):
            return False
        self.commands[primary_name] = [command]
        self._save()
        return True

    def delete_command(self, name: str) -> bool:
        """Delete a command and all its aliases."""
        primary_name = self._get_primary_name(name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands):
            return False
        
        self._remove_command_aliases(primary_name)
        del self.commands[primary_name]
        self._save()
        return True

    def copy_command(self, old_name: str, new_name: str) -> bool:
        """Copy an existing command to a new name."""
        if not self.validator.is_valid_new_name(new_name, self.commands, self.aliases):
            return False
        
        primary_name = self._get_primary_name(old_name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands):
            return False
        
        self.commands[new_name] = self.commands[primary_name].copy()
        self._save()
        return True

    def rename_command(self, old_name: str, new_name: str) -> bool:
        """Rename a primary command while preserving its aliases."""
        old_primary = self._get_primary_name(old_name)
        if not self.validator.is_valid_existing_name(old_primary, self.commands) or \
           not self.validator.is_valid_new_name(new_name, self.commands, self.aliases):
            return False

        # Update all aliases pointing to the old name
        for alias, target in list(self.aliases.items()):
            if target == old_primary:
                self.aliases[alias] = new_name

        # Move the command list to the new name
        self.commands[new_name] = self.commands.pop(old_primary)
        self._save()
        return True

    # Sequence Management Methods
    def append_command(self, name: str, command: str) -> bool:
        """Append a command to an existing command sequence."""
        primary_name = self._get_primary_name(name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands):
            return False
        self.commands[primary_name].append(command)
        self._save()
        return True

    def pop_command(self, name: str) -> bool:
        """Remove the last command from a command sequence."""
        primary_name = self._get_primary_name(name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands) or \
           not self.commands[primary_name]:
            return False
        
        self.commands[primary_name].pop()
        if not self.commands[primary_name]:
            self.delete_command(primary_name)
        else:
            self._save()
        return True

    # Alias Management Methods
    def add_alias(self, command_name: str, alias: str) -> bool:
        """Add an alias for a command."""
        primary_name = self._get_primary_name(command_name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands) or \
           not self.validator.is_valid_new_name(alias, self.commands, self.aliases):
            return False
        
        self.aliases[alias] = primary_name
        self._save()
        return True

    def remove_alias(self, command_name: str, alias: str) -> bool:
        """Remove an alias for a command."""
        primary_name = self._get_primary_name(command_name)
        if not self.validator.is_valid_existing_name(primary_name, self.commands) or \
           self.aliases.get(alias) != primary_name:
            return False
        
        del self.aliases[alias]
        self._save()
        return True

    # Query Methods
    def get_command(self, name: str) -> Optional[List[str]]:
        """Get a command by name or alias."""
        primary_name = self._get_primary_name(name)
        return self.commands.get(primary_name)

    def list_commands(self) -> Dict[str, Tuple[List[str], Set[str]]]:
        """List all commands with their aliases."""
        return {name: (cmds, self._get_all_aliases(name)) 
                for name, cmds in self.commands.items()}
