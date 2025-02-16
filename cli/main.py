import os
import sys
import time
import shlex
import subprocess
from typing import List
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import typer
import cmd
from supabase_config import supabase
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import difflib
import shutil

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

app = typer.Typer()
console = Console() 

# Rich Configuration
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)

### 🎨 Enhanced Typer Commands with Rich
@app.command("list-users")
def list_users():
    """Fetch and display users from Supabase"""
    with console.status("[bold green]Fetching users from database...[/]", spinner="dots"):
        try:
            response = supabase.table("users").select("*").execute()
            time.sleep(0.5)  # Simulate delay for better UI effect
            
            if response.data:
                table = Table(title="📊 User Database", style="cyan", title_style="bold magenta")
                table.add_column("ID", style="dim")
                table.add_column("Name", justify="left")
                table.add_column("Email", justify="left")
                
                for user in response.data:
                    table.add_row(str(user['id']), user['name'], user['email'])
                console.print(table)
            else:
                console.print("[bold yellow]⚠ No users found in the database[/]")
                
        except Exception as e:
            console.print(f"[bold red]❌ Database error: {str(e)}[/]")

@app.command("add-user")
def add_user(name: str, email: str):
    """Add a new user to Supabase"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Adding user...", total=100)
        
        for _ in range(10):
            progress.update(task, advance=10)
            time.sleep(0.05)
            
        try:
            response = supabase.table("users").insert({"name": name, "email": email}).execute()
            console.print(f"[bold green]✅ Successfully added user: [cyan]{name}[/] ({email})[/]")
        except Exception as e:
            console.print(f"[bold red]❌ Failed to add user: {str(e)}[/]")

### 🚀 Enhanced Interactive Shell
class PowerShell(cmd.Cmd):
    prompt = "✨ > "
    
    def __init__(self):
        super().__init__()
        self.commands = self.get_system_commands() + ["list-users", "add-user", "exit", "cd", "shell"]
        self.completer = WordCompleter(self.commands, ignore_case=True)
        self.intro = Panel.fit(
            Text("🚀 Welcome to PowerCLI!\nType 'help' for commands", justify="center"), 
            style="bold magenta"
        ) 
        self.command_history = [] 

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
            self.run_system_command(cmd, args, undo_cmd)
            return False

    def run_system_command(self, cmd: str, args: List[str], undo_cmd: str):
        """Execute system command and save undo action"""
        try:
            full_command = f"{cmd} {' '.join(args)}" if args else cmd

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

            if process.returncode == 0 and undo_cmd:
                self.command_history.append((full_command, undo_cmd))  # Store command history
            elif process.returncode != 0:
                console.print(f"[bold red]❌ Command failed (code {process.returncode})[/]")

        except FileNotFoundError:
            console.print(f"[bold red]❌ Command not found: {cmd}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ Error executing command: {str(e)}[/]")
            
    def get_undo_command(self, cmd: str, args: List[str]) -> str:
        """Generate undo commands for supported operations"""
        
        if cmd == "mkdir" and args:
            dir_path = os.path.abspath(args[0])  # Ensure full path
            return f'rmdir /s /q "{dir_path}"'  # Windows needs /s /q

        if cmd == "rmdir" and args:
            dir_path = os.path.abspath(args[0])
            return f'mkdir "{dir_path}"'  # Recreate the deleted directory

        if cmd == "del" and args:
            backup_path = f"backup_{args[0]}"
            if os.path.exists(args[0]):
                shutil.copy(args[0], backup_path)  # Backup before deleting
            return f'copy "{backup_path}" "{args[0]}"' if os.path.exists(backup_path) else ""

        if cmd == "copy" and len(args) == 2:
            return f'del "{args[1]}"'

        if cmd == "move" and len(args) == 2:
            return f'move "{args[1]}" "{args[0]}"'

        if cmd == "cd":
            # Store the current directory before changing it
            current_dir = os.getcwd()
            return f'cd "{current_dir}"'  # Return to the previous working directory

         # touch -> del
        if cmd == "touch" and args:
            return f'del "{args[0]}"'

        # rename -> rename back
        if cmd == "rename" and len(args) == 2:
            return f'rename "{args[1]}" "{args[0]}"'

        # append -> restore from backup
        if cmd == "append" and len(args) == 2:
            backup_path = f"backup_{args[0]}"
            if os.path.exists(args[0]):
                shutil.copy(args[0], backup_path)  # Backup before appending
            return f'copy "{backup_path}" "{args[0]}"' if os.path.exists(backup_path) else ""

        # set -> restore previous value
        if cmd == "set" and len(args) == 2:
            previous_value = os.getenv(args[0])
            if previous_value is not None:
                return f'set "{args[0]}={previous_value}"'
            else:
                return f'set "{args[0]}="'  # Unset if no previous value
            
        return ""

    def do_undo(self, arg: str):
        """Undo the last executed command"""
        if not self.command_history:
            console.print("[bold yellow]⚠ Nothing to undo[/]")
            return
        
        last_command, undo_command = self.command_history.pop()  # Get last command
        console.print(f"[bold cyan]🔄 Undoing: {last_command} -> {undo_command}[/]")
        
        if undo_command:
            # Split the undo_command into parts and pass them as arguments
            command_parts = shlex.split(undo_command)
            self.run_system_command(command_parts[0], command_parts[1:], undo_cmd="")
        else:
            console.print("[bold red]❌ Cannot undo this command[/]")

    # Command implementations
    def do_cd(self, arg: str):
        """Change directory: cd <path>"""
        try:
            # Store the current directory before changing it
            current_dir = os.getcwd()
            os.chdir(arg)
            console.print(f"[bold cyan]📂 Current directory: [underline]{os.getcwd()}[/][/]")
            
            # Store the undo command in history
            undo_command = f'cd "{current_dir}"'
            self.command_history.append((f"cd {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Directory error: {str(e)}[/]")

    def do_touch(self, arg: str):
        """Create an empty file: touch <filename>"""
        try:
            with open(arg, "w") as f:
                pass  # Create an empty file
            console.print(f"[bold green]✅ Created file: [cyan]{arg}[/][/]")
            
            # Store the undo command in history
            undo_command = f'del "{arg}"'
            self.command_history.append((f"touch {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Error creating file: {str(e)}[/]")
            
    def do_rename(self, arg: str):
        """Rename a file or directory: rename <old_name> <new_name>"""
        try:
            parts = shlex.split(arg)
            if len(parts) != 2:
                console.print("[bold red]❌ Usage: rename <old_name> <new_name>[/]")
                return
            
            old_name, new_name = parts
            os.rename(old_name, new_name)
            console.print(f"[bold green]✅ Renamed: [cyan]{old_name}[/] -> [cyan]{new_name}[/][/]")
            
            # Store the undo command in history
            undo_command = f'rename "{new_name}" "{old_name}"'
            self.command_history.append((f"rename {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Error renaming: {str(e)}[/]")
            
    def do_append(self, arg: str):
        """Append text to a file: append <filename> <text>"""
        try:
            parts = shlex.split(arg)
            if len(parts) < 2:
                console.print("[bold red]❌ Usage: append <filename> <text>[/]")
                return
            
            filename, text = parts[0], " ".join(parts[1:])
            
            # Backup the file before appending
            backup_path = f"backup_{filename}"
            shutil.copy(filename, backup_path)
            
            with open(filename, "a") as f:
                f.write(text + "\n")
            console.print(f"[bold green]✅ Appended to file: [cyan]{filename}[/][/]")
            
            # Store the undo command in history
            undo_command = f'copy "{backup_path}" "{filename}"'
            self.command_history.append((f"append {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Error appending to file: {str(e)}[/]")
    
    def do_set(self, arg: str):
        """Set an environment variable: set <variable> <value>"""
        try:
            parts = shlex.split(arg)
            if len(parts) != 2:
                console.print("[bold red]❌ Usage: set <variable> <value>[/]")
                return
            
            variable, value = parts
            previous_value = os.getenv(variable)
            os.environ[variable] = value
            console.print(f"[bold green]✅ Set environment variable: [cyan]{variable}[/] = [cyan]{value}[/][/]")
            
            # Store the undo command in history
            if previous_value is not None:
                undo_command = f'set "{variable}={previous_value}"'
            else:
                undo_command = f'set "{variable}="'  # Unset if no previous value
            self.command_history.append((f"set {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Error setting environment variable: {str(e)}[/]")
            
    def do_exit(self, arg: str) -> bool:
        """Exit the shell"""
        console.print(Panel.fit("👋 Goodbye!", style="bold magenta"))
        return True

    def do_list_users(self, arg: str):
        """List all users"""
        list_users()

    def do_add_user(self, arg: str):
        """Add new user: add_user <name> <email>"""
        try:
            parts = shlex.split(arg)
            if len(parts) != 2:
                console.print("[bold red]❌ Usage: add_user 'Name' 'email@example.com'[/]")
                return
            name, email = parts
            add_user(name, email)
        except Exception as e:
            console.print(f"[bold red]❌ Error: {str(e)}[/]")

### 🚀 Main Entry Point
@app.command("shell")
def start_shell():
    """Launch interactive shell"""
    PowerShell().cmdloop()

if __name__ == "__main__":
    app()