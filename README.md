# ez-cmd

A simple CLI tool that allows you to save and replay commands easily across different systems.

## Installation

```bash
pip install ez-cmd
```

## Usage

Save a command:
```bash
ez save <name> <command>
```

Execute a saved command:
```bash
ez <name>
```

List all saved commands:
```bash
ez list
```

Update a command:
```bash
ez update <name> <new_command>
```

Delete a command:
```bash
ez delete <name>
```

Save multiple commands to a single name:
```bash
ez save <name> "<command1> && <command2>"
```

## Configuration

Commands are stored in a JSON configuration file located at `~/.ez-cmd/config.json`. This file can be copied and shared across systems.
