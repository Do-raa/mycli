HELP_TOPICS = {
    # 📁 File & Directory Operations
    "cd": "Changes the current working directory. Use 'cd <folder>' to enter a directory or 'cd ..' to go back one level.",
    "ls": "Lists files and directories in the current folder. Similar to 'dir' but often styled for Unix systems.",
    "dir": "Displays a list of files and subdirectories in a directory (Windows equivalent of 'ls').",
    "touch": "Creates a new, empty file. Example: 'touch notes.txt'.",
    "mkdir": "Creates a new folder. Usage: 'mkdir <folder-name>'.",
    "rmdir": "Deletes a directory. Use with caution as it removes the folder and its contents. Syntax: 'rmdir <folder-name>'.",
    "rm": "Removes a file. Example: 'rm file.txt'.",
    "rename": "Renames a file or directory. Syntax: 'rename oldname newname'.",
    "copy": "Copies a file from source to destination. Example: 'copy file.txt backup.txt'.",
    "move": "Moves a file or folder to a new location. Syntax: 'move source destination'.",
    "tree": "Displays the folder structure of the current directory in a tree-like format.",

    # 🖥️ System Information & Management
    "whoami": "Displays the current logged-in username.",
    "hostname": "Shows the name of the computer.",
    "systeminfo": "Displays detailed system configuration including OS version, memory, and hardware details.",
    "tasklist": "Lists all currently running processes and their details.",
    "taskkill": "Terminates a process using its name or process ID (PID). Syntax: 'taskkill /PID 1234 /F'.",

    # 🌐 Networking & IP Management
    "ipconfig": "Displays current network configuration details including IP address, gateway, and DNS.",
    "ping": "Checks connectivity to a host by sending ICMP packets. Usage: 'ping example.com'.",
    "tracert": "Traces the route that packets take to reach a network host. Helps with diagnosing network routing issues.",
    "netstat": "Displays network statistics and active connections. Useful for checking open ports and listening services.",
    "nslookup": "Performs DNS lookup to retrieve IP address information about a domain. Usage: 'nslookup google.com'.",

    # 💾 Disk & Storage Commands
    "diskpart": "Launches the disk partition utility for managing disks, volumes, and partitions.",
    "chkdsk": "Checks the file system and disk for errors. Syntax: 'chkdsk C: /f /r'. May require reboot for full scan.",
    "wmic": "Accesses Windows Management Instrumentation for querying system details. Example: 'wmic logicaldisk get size,freespace,caption'.",

    # 💡 Shell Behavior & Exit
    "exit": "Closes and exits the CLI assistant shell.",
    "help": "Lists all available commands or provides help for a specific command using '--help' or '-h'.",
    "undo": "Reverts the last file-related command if undo info is available (e.g., undo mkdir, undo move)."
}
