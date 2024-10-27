# ez-cmd

A simple CLI tool that allows you to save and replay commands easily across different systems.

## Installation

```bash
pip install ez-cmd
```

## Usage

Commands are organized into the following groups:

### Command Management

Save a new command:
```bash
ez save <name> <command>
```

Update an existing command:
```bash
ez update <name> <command>
```

Delete a command and its aliases:
```bash
ez delete <name>
```

Rename a command while keeping its aliases:
```bash
ez rename <old_name> <new_name>
```

### Alias Management

Add an alias for a command:
```bash
ez alias <command_name> <alias>
```

Remove a command alias:
```bash
ez alias -d <command_name> <alias>
```

### Sequence Management

Add a command to an existing sequence:
```bash
ez append <name> <command>
```

Remove the last command from a sequence:
```bash
ez pop <name>
```

### Utility

Show all saved commands:
```bash
ez list
```

### Command Arguments

Commands can include argument placeholders that are replaced when executing the command. Use `{0}`, `{1}`, etc. to define argument positions:

```bash
# Save a command with one argument
ez save list-files "ls {0}"
ez list-files /path/to/dir

# Save a command with multiple arguments
ez save copy-file "cp {0} {1}"
ez copy-file source.txt destination.txt

# Use in command sequences
ez save build-project "cd {0} && npm install && npm run build"
ez build-project ./my-project
```

### Examples

Save a simple command:
```bash
ez save build "npm run build"
```

Create a command sequence:
```bash
ez save deploy "git pull"
ez append deploy "npm install"
ez append deploy "npm run build"
ez append deploy "npm run deploy"
```

Add aliases for frequently used commands:
```bash
ez save serve "npm run dev"
ez alias serve dev
ez alias serve start
```

Save commands with arguments:
```bash
# Create a command for searching files
ez save find-in "grep -r {0} {1}"
ez find-in "TODO" ./src

# Create a command for git operations
ez save commit "git add . && git commit -m {0}"
ez commit "Updated documentation"
```

Execute a saved command or alias:
```bash
ez deploy    # Runs the deploy sequence
ez dev       # Runs the serve command via alias
```

## Configuration

Commands are stored in a JSON configuration file located at `~/.ez-cmd/config.json`. This file can be copied and shared across systems.

## Command Overview

- **Command Management**
  - `save`: Save a new command (supports argument placeholders)
  - `update`: Update an existing command
  - `delete`: Delete a command and its aliases
  - `rename`: Rename a command while keeping its aliases

- **Alias Management**
  - `alias`: Add or remove command aliases

- **Sequence Management**
  - `append`: Add a command to an existing sequence
  - `pop`: Remove the last command from a sequence

- **Utility**
  - `list`: Show all saved commands with their aliases and sequences
