import os
import sys
import shlex
import subprocess
from typing import List
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import typer
import cmd
from prompt_toolkit import prompt
import difflib
import shutil 

from rich import print as rprint
from rich.console import Console
from rich.style import Style

from init import initialize_powershell
from commands import (do_cd, do_ls, do_dir, do_tree, do_taskkill, do_tasklist, do_systeminfo, do_whoami, do_hostname, do_touch, do_mkdir, do_rmdir, do_rm, do_rename, do_copy, do_move, do_ping, do_nslookup, do_ipconfig, do_tracert, do_netstat, do_diskpart, do_chkdsk, do_wmic, do_append, do_exit, do_help) 

app = typer.Typer()
console = Console()

# Rich Configuration
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)
            
### 🚀 Enhanced Interactive Shell
class PowerShell(cmd.Cmd):
    prompt = "✨ > "

    def __init__(self):
        super().__init__()
        init_data = initialize_powershell()
        self.commands = init_data["commands"]
        self.completer = init_data["completer"]
        self.intro = init_data["intro"]
        self.command_history = init_data["command_history"]
        self.history = init_data["history"]
        
    
    def get_system_commands(self) -> List[str]:
        """Get available system commands with caching"""
        paths = os.getenv("PATH", "").split(os.pathsep)
        commands = {"cls", "help", "exit", "cd", "dir", "copy", "del", "mkdir", "rmdir", "echo", "type"}
        
        for path in filter(os.path.isdir, paths):
            try:
                commands.update(
                    f.split(".")[0] 
                    for f in os.listdir(path) 
                    if f.endswith((".exe", ".bat", ".cmd"))
                )
            except PermissionError:
                continue
                
        return list(commands)

    def cmdloop(self, intro=None):
        console.print(self.intro)
        while True:
            try:
                user_input = prompt(
                    self.prompt,
                    completer=self.completer,
                    history=self.history,  # Add history here
                    complete_while_typing=True,
                    mouse_support=True
                )
                self.onecmd(user_input)
            except KeyboardInterrupt:
                console.print("\n[bold yellow]⚠ Use 'exit' to quit[/]")
            except EOFError:
                self.do_exit("")

    def onecmd(self, line: str) -> bool:
        """Process command input, correct typos, and execute commands properly"""
        if not line.strip():
            return False

        parts = shlex.split(line)
        if not parts:
            return False

        cmd, args = parts[0], parts[1:]
        original_cmd = cmd

        # Command correction
        if cmd not in self.commands:
            closest = difflib.get_close_matches(cmd, self.commands, n=1, cutoff=0.7)
            if closest:
                corrected = closest[0]
                console.print(f"[yellow]✅ Auto-correcting '{original_cmd}' to '{corrected}'[/]")
                cmd = corrected  # Use corrected command

        # Check if it's a built-in command (implemented as do_<cmd>)
        method_name = f"do_{cmd.replace('-', '_')}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(" ".join(args))

        # Run system command
        undo_cmd = self.get_undo_command(cmd, args)
        self.run_system_command(cmd, args, msg, undo_cmd)
        return False

    def run_system_command(self, cmd: str, args: List[str], msg: str, undo_cmd: str):
        """Execute system command and save undo action with confirmation prompts."""
        try:
            full_command = f"{cmd} {' '.join(args)}" if args else cmd

            # List of destructive commands requiring confirmation
            # destructive_commands = {"del", "rm", "rmdir", "undo"}

            # # Prompt user before executing destructive commands
            # if cmd in destructive_commands:
            #     confirm = console.input(f"[bold red]⚠ Are you sure you want to execute '{full_command}'? (y/N): [/]")
            #     if confirm.lower() != "y":
            #         console.print("[bold yellow]🚫 Operation canceled.[/]")
            #         return

            # Ensure Windows commands work properly
            if os.name == "nt":
                full_command = f"cmd.exe /c {full_command}"

            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )

            with console.status(f"[bold cyan]Running {cmd}...[/]", spinner="dots2"):
                for line in process.stdout:
                    console.print(line.strip())
                for err in process.stderr:
                    console.print(f"[bold red]{err.strip()}[/]")

            process.wait()

            if process.returncode == 0:
                if undo_cmd:
                    self.command_history.append((full_command, undo_cmd))  # Store command history
                console.print(f"[bold green]✅ {msg}[/]")
            else:
                console.print(f"[bold red]❌ Command failed (code {process.returncode})[/]")

        except FileNotFoundError:
            console.print(f"[bold red]❌ Command not found: {cmd}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ Unexpected error: {str(e)}[/]")

    def get_undo_command(self, cmd: str, args: List[str]) -> str:
        """Generate undo commands for supported operations"""
        if cmd == "mkdir" and args:
            dir_path = os.path.abspath(args[0])  # Ensure full path
            return f'rmdir /s /q "{dir_path}"'  # Windows needs /s /q

        if cmd == "rmdir" and args:
            dir_path = os.path.abspath(args[0])
            return f'mkdir "{dir_path}"'  # Recreate the deleted directory

        if cmd == "del" and args:
            # Only create a backup if the file exists
            if os.path.exists(args[0]):
                backup_path = f"backup_{args[0]}"
                shutil.copy(args[0], backup_path)  # Backup before deleting
                return f'copy "{backup_path}" "{args[0]}"'
            return ""

        if cmd == "copy" and len(args) == 2:
            return f'del "{args[1]}"'

        if cmd == "move" and len(args) == 2:
            return f'move "{args[1]}" "{args[0]}"'

        if cmd == "cd":
            # Store the current directory before changing it
            current_dir = os.getcwd()
            return f'cd "{current_dir}"'  # Return to the previous working directory

        if cmd == "touch" and args:
            return f'del "{args[0]}"'

        if cmd == "rename" and len(args) == 2:
            return f'rename "{args[1]}" "{args[0]}"'

        if cmd == "append" and len(args) == 2:
            backup_path = f"backup_{args[0]}"
            if os.path.exists(args[0]):
                shutil.copy(args[0], backup_path)  # Backup before appending
            return f'copy "{backup_path}" "{args[0]}"' if os.path.exists(backup_path) else ""
            
        return ""
      
    def do_undo(self, arg: str):
            """Undo the last executed command"""
            if not self.command_history:
                console.print("[bold yellow]⚠  Nothing to undo[/]")
                return
            
            last_command, undo_command = self.command_history.pop()  # Get last command
            # Extract the folder or file name from the last command
            if "rmdir" in last_command:
                folder_name = last_command.split("rmdir ")[1].strip()
                console.print(f"[bold cyan]🔄 Restoring '{folder_name}' folder...[/]")
            elif "rm" in last_command:
                file_name = last_command.split("rm ")[1].strip()
                console.print(f"[bold cyan]🔄 Restoring '{file_name}' file...[/]")
            else:
                console.print(f"[bold cyan]🔄 Undoing: {last_command}[/]")
            
            # Check if the command requires confirmation
            # destructive_commands = {"del", "rm", "rmdir"}
            # if "undo" in self.destructive_commands and not self.confirm_destructive_action("undo", undo_command):
            #     console.print("[bold yellow]🚫 Operation canceled.[/]")
            #     return
            #  # Check if the command requires confirmation
            if undo_command and isinstance(undo_command, dict) and "command" in undo_command and "message" in undo_command:
                # Split the undo_command into parts and pass them as arguments
                command_parts = shlex.split(undo_command["command"])
                self.run_system_command(command_parts[0], command_parts[1:], undo_command["message"], undo_cmd="")
            else:
                console.print("[bold red]❌ Cannot undo this command[/]")
            
    def do_cd(self, arg):
        do_cd(self, arg, self.command_history)  

    def do_ls(self, arg):
        do_ls(self, arg)

    def do_dir(self, arg):
        do_dir(self, arg)

    def do_tree(self, arg):
        do_tree(self, arg)

    def do_taskkill(self, arg):
        do_taskkill(self, arg)

    def do_tasklist(self, arg):
        do_tasklist(self, arg)

    def do_systeminfo(self, arg):
        do_systeminfo(self, arg)

    def do_whoami(self, arg):
        do_whoami(self, arg)

    def do_hostname(self, arg):
        do_hostname(self, arg)

    def do_touch(self, arg):
        do_touch(self, arg, self.command_history)

    def do_mkdir(self, arg):
        do_mkdir(self, arg, self.command_history)

    def do_rmdir(self, arg):
        do_rmdir(self, arg, self.command_history)

    def do_rm(self, arg):
        do_rm(self, arg, self.command_history)

    def do_rename(self, arg):
        do_rename(self, arg, self.command_history)

    def do_copy(self, arg):
        do_copy(self, arg, self.command_history)

    def do_move(self, arg):
        do_move(self, arg, self.command_history)

    def do_ping(self, arg):
        do_ping(self, arg)

    def do_nslookup(self, arg):
        do_nslookup(self, arg)

    def do_ipconfig(self, arg):
        do_ipconfig(self, arg)

    def do_tracert(self, arg):
        do_tracert(self, arg)

    def do_netstat(self, arg):
        do_netstat(self, arg)

    def do_diskpart(self, arg):
        do_diskpart(self, arg)

    def do_chkdsk(self, arg):
        do_chkdsk(self, arg)

    def do_wmic(self, arg):
        do_wmic(self, arg)

    def do_append(self, arg):
        do_append(self, arg, self.command_history)

    def do_exit(self, arg):
        do_exit(self, arg)

    def do_help(self, arg):
        do_help(self, arg)
        
@app.command("shell")
def start_shell():
    """Launch interactive shell"""
    print("Starting shell...")  # Debugging statement
    PowerShell().cmdloop()

if __name__ == "__main__":
    app()