import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from cli.main import PowerShell

def test_shell_initialization():
    shell = PowerShell()
    assert isinstance(shell, PowerShell)
    assert shell.prompt == "✨ > "

@pytest.fixture
def shell():
    """Fixture to initialize the PowerShell object before each test."""
    return PowerShell()

def test_cd(shell):
    """Test changing directories."""
    with patch("cli.main.do_cd") as mock_cd:
        shell.onecmd("cd C:Users")  
        mock_cd.assert_called_once_with(shell, "C:Users", shell.command_history)

def test_ls(shell):
    """Test listing files and directories."""
    with patch("cli.main.console.print") as mock_print:
        # Execute the real ls command
        shell.onecmd("ls")

        # Capture the output printed to the console
        output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call.args)
        print(f"Output: {output}")
        
def test_touch(shell):
    """Test creating an empty file."""
    with patch("cli.main.do_touch") as mock_touch:
        shell.onecmd("touch newfile.txt")
        mock_touch.assert_called_once_with(shell, "newfile.txt", shell.command_history)

def test_mkdir(shell):
    """Test creating a directory."""
    with patch("cli.main.do_mkdir") as mock_mkdir:
        shell.onecmd("mkdir testdir")
        mock_mkdir.assert_called_once_with(shell, "testdir", shell.command_history)

def test_rmdir(shell):
    """Test removing a directory."""
    with patch("cli.main.do_rmdir") as mock_rmdir:
        shell.onecmd("rmdir testdir")
        mock_rmdir.assert_called_once_with(shell, "testdir", shell.command_history)

def test_rm(shell):
    """Test deleting a file."""
    with patch("cli.main.do_rm") as mock_rm:
        shell.onecmd("rm testfile.txt")
        mock_rm.assert_called_once_with(shell, "testfile.txt", shell.command_history)

def test_rename(shell):
    """Test renaming a file or directory."""
    with patch("cli.main.do_rename") as mock_rename:
        shell.onecmd("rename oldname.txt newname.txt")
        mock_rename.assert_called_once_with(shell, "oldname.txt newname.txt", shell.command_history)

def test_copy(shell):
    """Test copying a file."""
    with patch("cli.main.do_copy") as mock_copy:
        shell.onecmd("copy source.txt dest.txt")
        mock_copy.assert_called_once_with(shell, "source.txt dest.txt", shell.command_history)

def test_move(shell):
    """Test moving a file."""
    with patch("cli.main.do_move") as mock_move:
        shell.onecmd("move file.txt new_location/")
        mock_move.assert_called_once_with(shell, "file.txt new_location/", shell.command_history) 
        
def check_output(mock_print, expected_output):
    output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call.args)
    if expected_output not in output:
        pytest.fail(f"Expected output not found: {expected_output}\nActual output: {output}")

def test_tree(shell):
    """Test displaying folder structure in tree format."""
    with patch("cli.main.do_tree") as mock_tree:
        shell.onecmd("tree")
        mock_tree.assert_called_once_with(shell, "") 
        
def test_whoami(shell):
    """Test displaying the current user."""
    with patch("cli.main.do_whoami") as mock_whoami:
        shell.onecmd("whoami")
        mock_whoami.assert_called_once_with(shell, "") 
        
def test_hostname(shell):
    """Test displaying the computer's hostname."""
    with patch("cli.main.do_hostname") as mock_hostname:
        shell.onecmd("hostname")
        mock_hostname.assert_called_once_with(shell, "") 
        
def test_systeminfo(shell):
    """Test displaying system information."""
    with patch("cli.main.do_systeminfo") as mock_systeminfo:
        shell.onecmd("systeminfo")
        mock_systeminfo.assert_called_once_with(shell, "")
        
def test_tasklist(shell):
    """Test listing running processes."""
    with patch("cli.main.do_tasklist") as mock_tasklist:
        shell.onecmd("tasklist")
        mock_tasklist.assert_called_once_with(shell, "") 
        
def test_taskkill(shell):
    """Test killing a process by name or PID."""
    with patch("cli.main.do_taskkill") as mock_taskkill:
        shell.onecmd("taskkill /PID 1234 /F")
        mock_taskkill.assert_called_once_with(shell, "/PID 1234 /F")
        
def test_ipconfig(shell):
    """Test displaying network configuration."""
    with patch("cli.main.do_ipconfig") as mock_ipconfig:
        shell.onecmd("ipconfig")
        mock_ipconfig.assert_called_once_with(shell, "")
        
def test_ping(shell):
    """Test network connectivity."""
    with patch("cli.main.do_ping") as mock_ping:
        shell.onecmd("ping example.com")
        mock_ping.assert_called_once_with(shell, "example.com") 
        
def test_tracert(shell):
    """Test tracing the route to a destination."""
    with patch("cli.main.do_tracert") as mock_tracert:
        shell.onecmd("tracert example.com")
        mock_tracert.assert_called_once_with(shell, "example.com")
        
def test_netstat(shell):
    """Test displaying active network connections."""
    with patch("cli.main.do_netstat") as mock_netstat:
        shell.onecmd("netstat")
        mock_netstat.assert_called_once_with(shell, "")
        
def test_nslookup(shell):
    """Test getting DNS information for a domain."""
    with patch("cli.main.do_nslookup") as mock_nslookup:
        shell.onecmd("nslookup example.com")
        mock_nslookup.assert_called_once_with(shell, "example.com") 
        
def test_diskpart(shell):
    """Test managing disk partitions."""
    with patch("cli.main.do_diskpart") as mock_diskpart:
        shell.onecmd("diskpart")
        mock_diskpart.assert_called_once_with(shell, "") 
        
def test_chkdsk(shell):
    """Test checking the disk for errors."""
    with patch("cli.main.do_chkdsk") as mock_chkdsk:
        shell.onecmd("chkdsk")
        mock_chkdsk.assert_called_once_with(shell, "")
        
def test_wmic(shell):
    """Test Windows Management Instrumentation Command-line."""
    with patch("cli.main.do_wmic") as mock_wmic:
        shell.onecmd("wmic logical disk get")
        mock_wmic.assert_called_once_with(shell, "logical disk get")
        
def test_exit(shell):
    """Test exiting the shell."""
    with patch("cli.main.do_exit") as mock_exit:
        shell.onecmd("exit")
        mock_exit.assert_called_once_with(shell, "") 
        
def test_help(shell):
    """Test displaying help information."""
    with patch("cli.main.do_help") as mock_help:
        shell.onecmd("help")
        mock_help.assert_called_once_with(shell, "")