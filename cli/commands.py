import os
import sys
import psutil
import shutil
import shlex
import time
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.spinner import Spinner
from rich.style import Style
from rich.progress import Progress, SpinnerColumn, TextColumn
import platform
from rich.prompt import Prompt, Confirm 

console = Console()      
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)

def show_loader(task_name, func, *args, **kwargs):
    """Displays a spinner while executing a function."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold yellow]{task.fields[task_name]}...[/]"),
        transient=True,
    ) as progress:
        task = progress.add_task("", task_name=task_name, total=None)
        try:
            result = func(*args, **kwargs)
            time.sleep(0.5) 
            return result
        finally:
            progress.remove_task(task)
            
def do_cd(self, arg: str, command_history):
    """Change directory: cd <path>"""

    if arg in ["--help", "-h"]:
        console.print("[bold cyan]Usage: cd <path>[/]\n[bold #FF8C00]Change the current working directory.")
        return

    # If no directory is entered, prompt the user
    while not arg.strip():
        arg = Prompt.ask("[bold yellow]Please enter the directory path:[/]").strip()
        if not arg:  # Prevent infinite loop if user presses Enter without input
            console.print("[bold red]❌ Error: Directory path cannot be empty.[/]")
            return

    try:
        current_dir = os.getcwd()
        os.chdir(arg)
        console.print(f"[bold cyan]📂 Current directory: [underline]{os.getcwd()}[/][/]") 

        # Store the undo command in history
        undo_command = {
            "command": f'cd "{current_dir}"',
            "message": f'Returned to the previous directory: "{current_dir}".'
        }
        command_history.append((f"cd {arg}", undo_command))

    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/]") 
                
def do_ls(self, arg: str):
    """List files and directories with a loading indicator."""
    if arg in ["--help", "-h"]:
                console.print("[bold cyan]Usage: ls[/]\n[bold #FF8C00]List files and directories in the current directory.")
                return
    console.print("[bold cyan]📂 Scanning directory...[/]")
    
    with console.status("[bold yellow]Listing files...[/]"):
        time.sleep(1)  # Simulate loading time
        files = os.listdir(arg if arg else os.getcwd())

    console.print("\n[bold green]📁 Files & Directories:[/]")
    for file in files:
        console.print(f"  - {file}")

    console.print("[bold green]✅ Listing complete![/] 🎉")
                
def do_dir(self, arg: str):
            """List files and directories"""
            if arg in ["--help", "-h"]:
                console.print("[bold cyan]Usage: ls[/]\n[bold #FF8C00]List files and directories in the current directory.")
                return
            console.print("[bold cyan]📂 Scanning directory...[/]")
            
            with console.status("[bold yellow]Listing files...[/]"):
                time.sleep(1)  # Simulate loading time
                files = os.listdir(arg if arg else os.getcwd())

            console.print("\n[bold green]📁 Files & Directories:[/]")
            for file in files:
                console.print(f"  - {file}")

            console.print("[bold green]✅ Listing complete![/] 🎉")

def do_tree(self, arg: str):
    """Display folder structure with interactive mode"""

    if arg in ["--help", "-h"]:
        console.print(
            "[bold cyan]Usage: tree <options> <directory>[/]\n"
            "\nOptions:\n"
            "  [green]/f[/]  Show files\n"
            "  [green]/a[/]  Use ASCII characters\n"
            "[bold #FF8C00]Display folder structure.[/]"
        )
        return

    # Ask for the directory path if not provided
    directory = arg if arg else Prompt.ask("Enter directory path", default=os.getcwd())

    # Ask the user whether to include options
    include_files = Confirm.ask("Include files in the tree output? (Use '/f' option)", default=False)
    use_ascii = Confirm.ask("Use ASCII characters instead of Unicode? (Use '/a' option)", default=False)

    # Construct the command with options
    options = ""
    if include_files:
        options += "/f "
    if use_ascii:
        options += "/a "

    command = f"tree {options}{directory}"
    with Progress(SpinnerColumn(), TextColumn("[cyan]Building folder structure...[/]")) as progress:
        task = progress.add_task("", total=None)
        os.system(command)
        progress.update(task, completed=True)

    console.print(f"[bold green]✅ Executed:[/] {command}")
    
def do_taskkill(self, arg: str):
        """Kill a process by name or PID"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: taskkill /PID <id> /F or taskkill /IM <process_name> /F[/]\n"
                "Options:\n"
                "  [green]/PID <id>[/]   Kill process by ID\n"
                "  [green]/IM <name>[/]  Kill process by name\n"
                "  [red]/F[/]            Force kill the process\n"
                "[bold #FF8C00]Kill a process by name or PID"
            )
            return

        """Kill a process interactively"""
        if not arg:
            processes = [p.info for p in psutil.process_iter(['pid', 'name'])]

            if not processes:
                console.print("[bold red]No processes found.[/]")
                return

            # Create a table for better visibility
            table = Table(title="Running Processes", header_style="bold cyan")
            table.add_column("#", justify="right", style="bold yellow")
            table.add_column("Process Name", style="bold magenta")
            table.add_column("PID", justify="right", style="bold green")

            # Populate table
            pid_map = {}
            for index, proc in enumerate(processes, start=1):
                table.add_row(str(index), proc["name"], str(proc["pid"]))
                pid_map[str(index)] = proc["pid"]

            console.print(table)

            # Ask user to select a process by index
            choice = Prompt.ask("Enter the number corresponding to the process you want to kill")

            # Get the actual PID
            pid = pid_map[choice]

            if Confirm.ask(f"Are you sure you want to kill PID {pid} ({processes[int(choice) - 1]['name']})?"):
                os.system(f"taskkill /PID {pid} /F")
                console.print(f"[bold red]Process {pid} terminated.[/]")

            return

        os.system(f"taskkill {arg}")
        console.print(f"[bold green]Executed:[/] taskkill {arg}")

def do_ping(self, arg: str):
    """Test network connectivity with interactive mode and guided options"""
    
    if arg in ["--help", "-h"]:
        console.print(
            "[bold cyan]Usage: ping <host> [options][/]\n"
            "[bold yellow]Options:[/]\n"
            "  [green]-n <count>[/]  Number of echo requests to send (default: 4)\n"
            "  [green]-t[/]          Ping continuously until stopped (Ctrl + C)\n"
            "[bold #FF8C00]Test network connectivity with interactive mode.[/]"
        )
        return
    
    # Interactive mode: Ask for host if not provided
    while not arg.strip():
        arg = Prompt.ask("[bold yellow]Enter the host to ping (e.g., google.com):[/]").strip()
        if not arg:
            console.print("[bold red]❌ Error:[/] Hostname cannot be empty.")
            return

    # Ask if the user wants to customize options
    if Confirm.ask("[bold cyan]Would you like to specify additional options?[/]"):
        count = Prompt.ask("[bold yellow]How many packets to send? (default: 4)[/]", default="4")
        continuous = Confirm.ask("[bold yellow]Do you want to ping continuously until stopped? (Ctrl + C to stop)[/]")
        
        # Build command based on OS
        system = platform.system()
        if system == "Windows":
            cmd = f"ping {arg} -n {count}"
            if continuous:
                cmd = f"ping {arg} -t"
        else:  # Linux/macOS
            cmd = f"ping -c {count} {arg}"
            if continuous:
                cmd = f"ping {arg}"
    else:
        cmd = f"ping {arg}"

    # Execute the command
    console.print(f"[bold green]✅ Executing:[/] {cmd}")
    try:
        show_loader("Pinging", os.system, cmd)
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/] {str(e)}")

def do_nslookup(self, arg: str):
        """Get DNS information for a domain"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: nslookup <domain>[/]\n"
                "[bold #FF8C00]Get IP address and DNS records for a domain."
            )
            return
        
        if not arg:
            console.print("[bold yellow]Enter a domain to query:[/]")
            arg = input().strip()
            
            show_loader("Looking up DNS", os.system, f"nslookup {arg}")
            console.print(f"[bold green]Executed:[/] nslookup {arg}")
        
        show_loader("Looking up DNS", os.system, f"nslookup {arg}")
        console.print(f"[bold green]Executed:[/] nslookup {arg}")
        
def do_whoami(self, arg: str):
        """Display the current user"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: whoami[/]\n"
                "[bold #FF8C00]Shows the currently logged-in user."
            )
            return
        
        os.system("whoami")
        console.print("[bold green]Executed:[/] whoami")

def do_hostname(self, arg: str):
        """Show the computer’s hostname"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: hostname[/]\n"
                "[bold #FF8C00]Displays the name of the computer."
            )
            return
        
        os.system("hostname")
        console.print("[bold green]Executed:[/] hostname")

def do_systeminfo(self, arg: str):
    """Get detailed system information with enhanced UI"""

    if arg in ["--help", "-h"]:
        console.print(
            "[bold cyan]Usage: systeminfo[/]\n"
            "[bold #FF8C00]Displays detailed system information, including OS version, installed updates, memory, and more.[/]"
        )
        return

    # Interactive section selection
    sections = {"OS": "OS Name", "Memory": "Total Physical Memory", "CPU": "Processor"}
    choice = Prompt.ask(
        "Select section", choices=["OS", "Memory", "CPU", "All"], default="All"
    )

    console.print("\n[bold cyan]🔍 Gathering system information...[/]")
    
    with console.status("[bold yellow]Loading system details...[/]"):
        time.sleep(1.5)  # Simulate loading time

    table = Table(title="🖥️ System Information", show_lines=True)
    table.add_column("Category", style="bold cyan", justify="left")
    table.add_column("Details", style="bold white", justify="left")

    # Retrieve system information
    system_info = {
        "OS": platform.system() + " " + platform.release(),
        "Memory": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "CPU": platform.processor(),
    }

    # Populate table based on user choice
    if choice == "All":
        for key, value in system_info.items():
            table.add_row(key, value)
    else:
        table.add_row(choice, system_info[choice])

    console.print(table)
    console.print("[bold green]✅ System information retrieved successfully![/] 🎉")
      
def do_tasklist(self, arg: str):
        """List running processes"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: tasklist <options> [/]\n"
                "\nOptions:\n"
                "  [green]/fi \"IMAGENAME eq process.exe\"[/]  Filter by process name\n"
                "  [green]/v[/]  Show detailed task information\n"
                "  [green]/svc[/]  Display services associated with tasks\n"
                "[bold #FF8C00]List running processes"
            )
            return
        
        """List running processes with filtering options"""
        if not arg:
            console.print("[bold yellow]Interactive Mode: Listing processes...[/]")

            filter_by = Prompt.ask("Filter by (name/memory/cpu/all)", choices=["name", "memory", "cpu", "all"], default="all")

            processes = [p.info for p in psutil.process_iter(['pid', 'name', 'memory_info'])]

            if filter_by == "name":
                process_name = Prompt.ask("Enter process name")
                processes = [p for p in processes if process_name.lower() in p['name'].lower()]
            elif filter_by == "memory":
                processes.sort(key=lambda p: p['memory_info'].rss, reverse=True)

            with Progress(SpinnerColumn(), TextColumn("[cyan]Fetching process list...[/]")) as progress:
                task = progress.add_task("", total=None)
                for proc in processes[:10]:
                    console.print(f"[bold yellow]{proc['name']}[/] (PID: {proc['pid']}) - Memory: {proc['memory_info'].rss / 1024:.2f} KB")
                progress.update(task, completed=True)

        os.system(f"tasklist {arg}")
        console.print(f"[bold green]✅ Executed:[/] tasklist {arg}")
        
def do_ipconfig(self, arg: str):
        """Show network configuration"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: ipconfig <options> [/]\n"
                "\nOptions:\n"
                "  [green]/all[/]     Show detailed network configuration\n"
                "  [green]/release[/] Release current IP address\n"
                "  [green]/renew[/]   Renew IP address\n"
                "[bold #FF8C00]Show network configuration"
            )
            return
        
        os.system(f"ipconfig {arg}")
        console.print(f"[bold green]Executed:[/] ipconfig {arg}")

def do_tracert(self, arg: str):
        """Trace the route packets take to a destination"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: tracert <destination>[/]\n"
                "[bold #FF8C00]Traces the path packets take to reach a destination."
            )
            return
        while True:
            console.print("[bold yellow]Enter filter (e.g., -p tcp) or press Enter to continue:[/]")
            filter_opt = input().strip()
            
            show_loader("Fetching network stats", os.system, f"netstat {filter_opt}")
            console.print(f"[bold green]Executed:[/] netstat {filter_opt}")
            
            console.print("[bold cyan]Run again with a different filter? (y/n)[/]")
            if input().strip().lower() != 'y':
                break
        # if not arg:
        #     console.print(f"[bold cyan]Tracing route to {arg}... Press Enter to continue each hop.")
        #     process = os.popen(f"tracert {arg}")
        #     for line in process:
        #         console.print(line.strip())
        #         input("[bold yellow]Press Enter to continue...[/]")
        #     process.close()
        #     console.print(f"[bold green]Executed:[/] tracert {arg}")
            
        #     show_loader("Fetching network stats", os.system, f"netstat {filter_opt}")
        #     console.print(f"[bold green]Executed:[/] tracert {arg}")
            
        # os.system(f"tracert {arg}")
        # console.print(f"[bold green]Executed:[/] tracert {arg}")

def do_netstat(self, arg: str):
        """Display active network connections"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: netstat <options> [/]\n"
                "\nOptions:\n"
                "  [green]-a[/]  Show all connections and listening ports\n"
                "  [green]-n[/]  Display addresses in numerical form\n"
                "  [green]-o[/]  Show process IDs (PIDs) for connections\n"
                "[bold #FF8C00]Display active network connections"
            )
            return
     
        while True:
            console.print("[bold yellow]Enter filter (e.g., -p tcp) or press Enter to continue:[/]")
            filter_opt = input().strip()
            os.system(f"netstat {filter_opt}")
            console.print(f"[bold green]Executed:[/] netstat {filter_opt}")
            
            console.print("[bold cyan]Run again with a different filter? (y/n)[/]")
            if input().strip().lower() != 'y':
                break
        os.system(f"netstat {arg}")
        console.print(f"[bold green]Executed:[/] netstat {arg}") 

def do_diskpart(self, arg: str):
        """Manage disk partitions"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: diskpart [/]\n"
                "[bold #FF8C00]Opens the disk partition management tool."
            )
            return
        if not Confirm.ask("[bold red]⚠ Warning: Disk partitioning can cause data loss! Continue? (y/n)[/]"):
            console.print("[bold red]❎ Aborted.[/]")
            return

        show_loader("Opening disk partition tool", os.system, "diskpart")
        console.print("[bold green]✅ Executed: diskpart[/]")
        # if not arg:
        #     console.print("[bold red]Warning:[/] Disk partitioning can cause data loss!")
        #     console.print("[bold cyan]Do you want to proceed? (y/n)[/]")
        #     if input().strip().lower() != 'y':
        #         console.print("[bold red]Aborted.[/]")
        #         return
            
        #     os.system("diskpart")
        #     console.print("[bold green]Executed:[/] diskpart")
        # os.system("diskpart")
        # console.print("[bold green]Executed:[/] diskpart")
        
def do_chkdsk(self, arg: str):
        """Check disk for errors interactively if no argument is given"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: chkdsk <drive> <options> [/]\n"
                "\nOptions:\n"
                "  [green]/f[/]  Fix errors on the disk\n"
                "  [green]/r[/]  Locate bad sectors and recover readable data\n"
                "[bold #FF8C00]Check disk for errors[/]"
            )
            return
        
        # Interactive mode if no argument is given
        if not arg:
            console.print("[bold yellow]Interactive Mode: Let's configure your chkdsk command![/]")
            
            # Ask for drive letter
            drive = Prompt.ask("Enter the drive letter (e.g., C:)")
            
            # Ask for options
            options = []
            if Confirm.ask("Do you want to fix errors on the disk? (/f)"):
                options.append("/f")
            if Confirm.ask("Do you want to locate bad sectors and recover readable data? (/r)"):
                options.append("/r")

            arg = f"{drive} {' '.join(options)}"

        show_loader(f"Running chkdsk on {arg}", os.system, f"chkdsk {arg}")
        console.print(f"[bold green]✅ Executed: chkdsk {arg}[/]")

def do_wmic(self, arg: str):
        """Retrieve disk information"""
        if arg in ["--help", "-h"]:
            console.print(
                "[bold cyan]Usage: wmic logicaldisk get <options> [/][/]\n"
                "[bold #FF8C00]Retrieves information about logical disks."
            )
            return
        
        show_loader("Fetching disk information", os.system, "wmic logicaldisk get size,caption")
        console.print("[bold green]✅ Executed: wmic logicaldisk get size,caption[/]")
        
def do_touch(self, arg: str, command_history):
    """Create an empty file with interactive mode"""
    if arg in ["--help", "-h"]:
        console.print("[bold cyan]Usage: touch <filename>[/]\n[bold #FF8C00]Create an empty file.")
        return
    
    # Interactive mode if no filename is given
    while not arg.strip():
        arg = Prompt.ask("[bold yellow]Please enter the filename to create:[/]").strip()
        if not arg:  # Prevent infinite loop if user presses Enter without input
            console.print("[bold red]❌ Error: Filename cannot be empty.[/]")
            return

    # Handle case where file already exists
    if os.path.exists(arg):
        choice = Prompt.ask(
            f"[bold yellow]File '{arg}' already exists. What do you want to do?[/]",
            choices=["overwrite", "cancel", "new"],
            default="cancel"
        )

        if choice == "cancel":
            console.print("[bold cyan]❎ Operation canceled.[/]")
            return
        elif choice == "new":
            base, ext = os.path.splitext(arg)
            counter = 1
            new_arg = f"{base}_{counter}{ext}"
            while os.path.exists(new_arg):
                counter += 1
                new_arg = f"{base}_{counter}{ext}"
            arg = new_arg
            console.print(f"[bold green]📄 Creating new file as '{arg}' instead.[/]")

    try:
        with open(arg, "w") as f:
            pass
        console.print(f"[bold green]✅ Created file: {arg}[/]")

        # Store the undo command in history
        undo_command = {
            "command": f'del "{arg}"' if os.name == "nt" else f'rm "{arg}"',
            "message": f'Deleted file "{arg}"'
        }
        command_history.append((f"touch {arg}", undo_command))
    except Exception as e:
        console.print(f"[bold red]❌ Error creating file: {str(e)}[/]")
            
def do_append(self, arg: str, command_history):
        """Append text to a file"""

        # Contextual Help System
        if arg in ["--help", "-h"]:
            console.print("[bold cyan]Usage: append <filename> <text>[/]\n[bold #FF8C00]Append text to the specified file.[/]")
            return
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
            undo_command = {
            "command":  f'copy "{backup_path}" "{filename}"',
            "message":  f'Restored previous version of "{filename}" before append operation.'
        }
            command_history.append((f"append {arg}", undo_command))
        except Exception as e:
            console.print(f"[bold red]❌ Error appending to file: {str(e)}[/]")
    
def do_mkdir(self, arg: str, command_history):
    """Create a new directory interactively or via command: mkdir <dirname>"""
    if arg in ["--help", "-h"]:
        console.print("[bold cyan]Usage: mkdir <dirname>[/]\n[bold #FF8C00]Create a new directory.[/]")
        return

    # Interactive mode if no arguments provided
    if not arg.strip():
        console.print("[bold yellow]📂 Interactive Directory Creation Mode Enabled[/]")

        while True:
            # Prompt user for directory name
            dirname = Prompt.ask("[bold cyan]Enter the name of the new directory[/]")

            # Check if directory already exists
            if os.path.exists(dirname):
                console.print(f"[bold red]❗ The directory '{dirname}' already exists.[/]")

                choice = Prompt.ask(
                    "[bold yellow]Choose an action: (o)verwrite, (r)ename, (c)ancel[/]",
                    choices=["o", "r", "c"]
                )

                if choice == "o":
                    try:
                        shutil.rmtree(dirname)  # Remove existing directory
                        console.print(f"[bold red]⚠️ Overwriting existing directory: {dirname}[/]")
                    except Exception as e:
                        console.print(f"[bold red]❌ Error removing existing directory: {str(e)}[/]")
                        return
                elif choice == "r":
                    continue  # Ask for a new name
                elif choice == "c":
                    console.print("[bold red]❌ Operation cancelled.[/]")
                    return
            break  # Exit loop if the name is valid
    else:
        dirname = arg

        # Check if directory exists in non-interactive mode
        if os.path.exists(dirname):
            console.print(f"[bold red]❌ Error: Directory '{dirname}' already exists.[/]")
            return

    # Attempt to create the directory
    try:
        os.makedirs(dirname, exist_ok=True)
        console.print(f"[bold green]✅ Created directory: {dirname}[/]")

        # Store the undo command in history
        undo_command = {
            "command": f'rd /s /q "{dirname}"' if os.name == "nt" else f'rm -r "{dirname}"',
            "message": f'Directory removed: {dirname}'
        }
        command_history.append((f"mkdir {dirname}", undo_command))
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/]")

def do_rm(self, arg: str, command_history):
    """Delete a file with interactive mode"""
    
    if arg in ["--help", "-h"]:
        console.print("[bold cyan]Usage: rm <filename>[/]\n[bold #FF8C00]Delete a file.")
        return
    
    # Interactive mode if no filename is provided
    while not arg.strip():
        arg = Prompt.ask("[bold yellow]Please enter the filename to delete:[/]").strip()
        if not arg:
            console.print("[bold red]❌ Error: Filename cannot be empty.[/]")
            return
    
    if not os.path.exists(arg):
        console.print(f"[bold red]❌ Error: File '{arg}' not found.[/]")
        return
    
    if not Confirm.ask(f"[bold yellow]Are you sure you want to delete '{arg}'?[/]"):
        console.print("[bold cyan]❎ Deletion canceled.[/]")
        return
    
    def delete_file():
        backup_path = f"{arg}.bak"
        shutil.copy(arg, backup_path)
        os.remove(arg)
        command_history.append((
            f"rm {arg}",
            {"command": f'cp "{backup_path}" "{arg}"' if os.name != "nt" else f'copy "{backup_path}" "{arg}"',
             "message": f'Restored file: {arg}'}
        ))

    show_loader("Deleting file", delete_file)
    console.print(f"[bold green]✅ Deleted file: {arg}[/]")
    # try:
    #     # Backup file before deletion
    #     backup_path = f"{arg}.bak"
    #     shutil.copy(arg, backup_path)

    #     os.remove(arg)
    #     console.print(f"[bold green]✅ Deleted file: {arg}[/]")

    #     # Store undo command in history
    #     undo_command = {
    #         "command": f'copy "{backup_path}" "{arg}"' if os.name == "nt" else f'cp "{backup_path}" "{arg}"',
    #         "message": f'Restored file: {arg}'
    #     }
    #     command_history.append((f"rm {arg}", undo_command))

    # except Exception as e:
    #     console.print(f"[bold red]❌ Error: {str(e)}[/]")

def do_rmdir(self, arg: str, command_history):
    """Delete a directory"""

    if arg in ["--help", "-h"]:
        console.print("[bold cyan]Usage: rmdir <dirname>[/]\n[bold #FF8C00]Delete a directory.")
        return 

    # If no directory is entered, prompt the user
    while not arg.strip():
        arg = Prompt.ask("[bold yellow]Please enter the directory name to delete:[/]").strip()
        if not arg:  # Prevent infinite loop if user presses Enter without input
            console.print("[bold red]❌ Error: Directory name cannot be empty.[/]")
            return

    if not os.path.exists(arg) or not os.path.isdir(arg):
        console.print(f"[bold red]❌ Error: Directory '{arg}' not found.[/]")
        return

    # Interactive prompt before deletion
    choice = Prompt.ask(
        f"[bold yellow]Are you sure you want to delete the directory '{arg}' and its contents?[/]",
        choices=["yes", "no", "backup"],
        default="no"
    )

    if choice.lower() == "no":
        console.print("[bold cyan]❎ Deletion canceled.[/]")
        return

    def delete_directory():
        backup_path = f"{arg}_backup"
        if choice == "backup":
            shutil.copytree(arg, backup_path)
            console.print(f"[bold green]📂 Backup created: {backup_path}[/]")
        shutil.rmtree(arg)
        command_history.append((
            f"rmdir {arg}",
            {"command": f'mv "{backup_path}" "{arg}"' if os.name != "nt" else f'robocopy "{backup_path}" "{arg}" /E && rmdir /s /q "{backup_path}"',
             "message": f'Restored directory: {arg}'}
        ))

    show_loader("Deleting directory", delete_directory)
    console.print(f"[bold green]✅ Deleted directory: {arg}[/]")
    # try:
    #     backup_path = f"{arg}_backup"

    #     # If the user chooses "backup," create a backup first
    #     if choice.lower() == "backup":
    #         shutil.copytree(arg, backup_path)
    #         console.print(f"[bold green]📂 Backup created: {backup_path}[/]")

    #     shutil.rmtree(arg)
    #     console.print(f"[bold green]✅ Deleted directory: {arg}[/]")

    #     undo_command = {
    #         "command": f'robocopy "{backup_path}" "{arg}" /E && rmdir /s /q "{backup_path}"' if os.name == "nt" else f'mv "{backup_path}" "{arg}"',
    #         "message": f'Restored directory: {arg}'
    #     }
    #     command_history.append((f"rmdir {arg}", undo_command))

    # except Exception as e:
    #     console.print(f"[bold red]❌ Error: {str(e)}[/]")

def do_rename(self, arg: str, command_history):
        """Rename a file or directory interactively or via command: rename <old_name> <new_name>"""
        if arg in ["--help", "-h"]:
            console.print("[bold cyan]Usage: rename <old> <new>[/]\n[bold #FF8C00]Rename a file or directory.")
            return

        # Interactive mode if no arguments provided
        if not arg.strip():
            console.print("[bold yellow]🔍 Interactive Rename Mode Enabled[/]")

            # List available files/directories
            items = os.listdir()
            if not items:
                console.print("[bold red]❌ No files or directories found in the current directory.[/]")
                return

            # Display options in a table
            table = Table(title="Files & Directories", show_lines=True)
            table.add_column("#", style="cyan", justify="center")
            table.add_column("Name", style="magenta")

            for idx, item in enumerate(items, start=1):
                table.add_row(str(idx), item)

            console.print(table)

            # Ask user to select a file/directory
            selected_index = Prompt.ask("[bold cyan]Enter the number of the item to rename[/]")
            old_name = items[int(selected_index) - 1]

            # Get the new name from the user
            new_name = Prompt.ask(f"[bold yellow]Enter new name for '{old_name}'[/]")

            # Confirm before renaming
            if not Confirm.ask(f"Rename [cyan]{old_name}[/] to [green]{new_name}[/]?"):
                console.print("[bold red]❌ Operation cancelled.[/]")
                return
        else:
            try:
                parts = shlex.split(arg)
                if len(parts) != 2:
                    console.print("[bold red]❌ Usage: rename <old_name> <new_name>[/]")
                    return
                
                old_name, new_name = parts
            except Exception:
                console.print("[bold red]❌ Invalid input. Use rename <old_name> <new_name>[/]")
                return

        # Perform the rename operation
        try:
            os.rename(old_name, new_name)
            console.print(f"[bold green]✅ Renamed: [cyan]{old_name}[/] -> [cyan]{new_name}[/][/]")

            # Store undo command
            undo_command = {
                    "command":  f'rename "{new_name}" "{old_name}"',
                    "message":  f'Renamed "{new_name}" to "{old_name}"'
                }
            command_history.append((f"rename {arg}", undo_command))

        except Exception as e:
            console.print(f"[bold red]❌ Error renaming: {str(e)}[/]")

def do_move(self, arg: str, command_history):
        """Move a file (interactive mode when no arguments are provided)"""
        if arg in ["--help", "-h"]:
            console.print("[bold cyan]Usage: move <source> <destination>[/]\n[bold #FF8C00]Move a file.[/]")
            return

        # Interactive mode if no argument is given
        if not arg:
            console.print("[bold yellow]Interactive Mode: Let's move a file![/]")
            source = Prompt.ask("[bold cyan]Enter the source file path:[/]")
            destination = Prompt.ask("[bold cyan]Enter the destination path:[/]")
        else:
            args = arg.split()
            if len(args) != 2:
                console.print("[bold red]❌ Usage: move <source> <destination>[/]")
                return
            source, destination = args

        if not os.path.exists(source):
            console.print(f"[bold red]❌ Error: Source file '{source}' not found.[/]")
            return

        if os.path.exists(destination):
            choice = Prompt.ask(
                f"[bold yellow]File '{destination}' already exists. Choose an action:[/]",
                choices=["overwrite", "rename", "cancel"],
                default="cancel"
            )

            if choice == "cancel":
                console.print("[bold cyan]❎ Move canceled.[/]")
                return
            elif choice == "rename":
                new_name = Prompt.ask("[bold yellow]Enter a new name for the moved file:[/]")
                destination = os.path.join(os.path.dirname(destination), new_name)

        with Progress(SpinnerColumn(), TextColumn("[cyan]Moving file...[/]")) as progress:
            task = progress.add_task("", total=None)
            try:
                shutil.move(source, destination)
                progress.update(task, completed=True)
                console.print(f"[bold green]✅ Moved '{source}' to '{destination}'[/]")
                full_source = os.path.abspath(source)
                full_destination = os.path.abspath(destination)
                undo_command = {
                    "command": f'move "{full_destination}" "{full_source}"' if os.name == "nt" else f'mv "{full_destination}" "{full_source}"',
                    "message": f'Restored "{source}" back to its original location.'
                }

                command_history.append((f"move {source} {destination}", undo_command))
            except Exception as e:
                console.print(f"[bold red]❌ Error: {str(e)}[/]")

def do_copy(self, arg: str, command_history):
        """Copy a file (interactive mode when no arguments are provided)"""
        if arg in ["--help", "-h"]:
            console.print("[bold cyan]Usage: copy <source> <destination>[/]\n[bold #FF8C00]Copy a file.[/]")
            return

        # Interactive mode if no argument is given
        if not arg:
            console.print("[bold yellow]Interactive Mode: Let's copy a file![/]")
            source = Prompt.ask("[bold cyan]Enter the source file path:[/]")
            destination = Prompt.ask("[bold cyan]Enter the destination path:[/]")
        else:
            args = arg.split()
            if len(args) < 2:
                console.print("[bold red]❌ Usage: copy <source> <destination>[/]")
                return
            source = args[0]
            destinations = args[1:]

        if not os.path.exists(source):
            console.print(f"[bold red]❌ Error: Source file '{source}' not found.[/]")
            return

        for destination in destinations:
            if os.path.exists(destination):
                overwrite = Confirm.ask(f"[bold yellow]File '{destination}' already exists. Overwrite?[/]")
                if not overwrite:
                    new_name = Prompt.ask("[bold yellow]Enter a new name for the copied file:[/]")
                    destination = os.path.join(os.path.dirname(destination), new_name)
            with Progress(SpinnerColumn(), TextColumn("[cyan]Copying file...[/]")) as progress:
                task = progress.add_task("", total=None)
                try:
                    shutil.copy(source, destination)
                    progress.update(task, completed=True)
                    console.print(f"[bold green]✅ Copied '{source}' to '{destination}'[/]")
                    undo_command = {
                        "command": f'del "{destination}"' if os.name == "nt" else f'rm "{destination}"',
                        "message": f'Removed copied file from : "{destination}".'
                    }

                    command_history.append((f"copy {source} {destination}", undo_command))
                except Exception as e:
                    console.print(f"[bold red]❌ Error: {str(e)}[/]")
            
def do_exit(self, arg: str) -> bool:
        """Exit the shell"""
        console.print(Panel.fit("👋 Goodbye!", style="bold magenta"))
        sys.exit(0)
        return True

def do_help(self, arg: str):
        """Show available commands or details for a specific command"""
        if arg:
            if arg in self.commands:
                console.print(f"[bold cyan]{arg}: {self.commands[arg]}[/]")
            else:
                console.print(f"[bold red]❌ No help available for '{arg}'[/]")
        else:
            console.print("[bold cyan]Available commands:[/]")
            for cmd, desc in self.commands.items():
                console.print(f"- [bold magenta]{cmd}[/]: {desc}")