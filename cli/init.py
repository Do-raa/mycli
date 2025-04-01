# init.py
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.prompt import Prompt
from prompt_toolkit.history import InMemoryHistory

from prompt_toolkit.completion import  Completion, Completer  
import os

console = Console()

class ContextAwareCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands  # Dictionary of available commands

    def get_completions(self, document, complete_event):
        """Provide suggestions based on the command context"""
        text_before_cursor = document.text_before_cursor.strip()
        words = text_before_cursor.split()

        if not words:
            return  # No input yet

        # If typing first word, suggest commands
        if len(words) == 1:
            for command in self.commands.keys():
                if command.startswith(words[0]):
                    yield Completion(command, start_position=-len(words[0]))

        # If typing arguments, suggest files and directories
        else:
            current_dir = os.getcwd()
            try:
                for item in os.listdir(current_dir):
                    if item.startswith(words[-1]):  # Filter matching input
                        yield Completion(item, start_position=-len(words[-1]))
            except Exception:
                pass
            
def initialize_powershell():
    commands = {
        # File & Directory Operations
        "cd": "Change directory: cd <path> and use 'cd ..' to navigate back to the previous directory",
        "ls": "List files and directories",
        "dir": "List files and directories (Windows alternative to 'ls')",
        "touch": "Create an empty file: touch <filename>",
        "mkdir": "Create a new directory: mkdir <dirname>",
        "rmdir": "Delete a directory: rmdir <dirname>",
        "rm": "Delete a file: rm <filename>",
        "rename": "Rename a file or directory: rename <old> <new>",
        "copy": "Copy a file: copy <source> <destination>",
        "move": "Move a file: move <source> <destination>",
        "tree": "Display folder structure in tree format",

        # System Information & Management
        "whoami": "Display the current user",
        "hostname": "Show the computer’s hostname",
        "systeminfo": "Get detailed system information",
        "tasklist": "List running processes",
        "taskkill": "Kill a process by name or PID: taskkill /PID <id> /F",

        # Networking & IP Management
        "ipconfig": "Show network configuration",
        "ping": "Test network connectivity: ping <host>",
        "tracert": "Trace the route packets take to a destination",
        "netstat": "Display active network connections",
        "nslookup": "Get DNS information for a domain: nslookup <domain>",

        # Disk & Storage Commands
        "diskpart": "Manage disk partitions",
        "chkdsk": "Check disk for errors",
        "wmic": "Windows Management Instrumentation Command-line: wmic logical disk get",
        
        # Shell & Exit Commands
        "exit": "Exit the shell",
        "help": "Show available commands or details for a specific command using '<command> --help'.",
        "undo": "Undo the last command",
    }
    
    completer = ContextAwareCompleter(commands)
    intro = Panel.fit(
        Text("🚀 Welcome to PowerCLI!\nType 'help' for commands", justify="center"),
        style="bold magenta"
    )
    
    return {
        "commands": commands,
        "completer": completer,
        "intro": intro,
        "command_history": [],
        "history": InMemoryHistory(),
    }
