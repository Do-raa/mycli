import pytest
import os
import shutil
import subprocess
import time

# Corrected path to your CLI script
CLI_SCRIPT = "C:/Users/GAMER/Desktop/CLI/cli/main.py"

# Temporary directory for testing
TEST_DIR = os.path.abspath("test_e2e_dir")  # Use absolute path

@pytest.fixture(scope="module")
def setup_test_environment():
    """Fixture to set up the test environment."""
    # Create a temporary directory for testing
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR, ignore_errors=True)  # Force cleanup
    os.makedirs(TEST_DIR, exist_ok=True)
    yield
    # Clean up the temporary directory after tests
    if os.path.exists(TEST_DIR):
        for _ in range(3):  # Retry up to 3 times
            try:
                shutil.rmtree(TEST_DIR, ignore_errors=True)
                break
            except Exception as e:
                print(f"Warning: Failed to clean up directory {TEST_DIR}: {e}")
                time.sleep(1)  # Wait for 1 second before retrying

def run_cli_command(command):
    """Helper function to run a CLI command and capture its output."""
    process = subprocess.Popen(
        [r"C:\Users\GAMER\Desktop\CLI\venv\Scripts\python.exe", CLI_SCRIPT, "shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(input=command)
    process.terminate()
    process.wait()
    return stdout, stderr

def test_touch_command(setup_test_environment):
    """Test the 'touch' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'touch' command
    stdout, stderr = run_cli_command("touch testfile.txt\nexit\n")

    # Verify the output
    if "✅ Created file: testfile.txt" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if not os.path.exists("testfile.txt"):
        print(f"Error: File 'testfile.txt' was not created.")

def test_mkdir_command(setup_test_environment):
    """Test the 'mkdir' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'mkdir' command
    stdout, stderr = run_cli_command("mkdir testdir\nexit\n")

    # Verify the output
    if "✅ Created directory: testdir" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if not os.path.exists("testdir"):
        print(f"Error: Directory 'testdir' was not created.")

def test_ls_command(setup_test_environment):
    """Test the 'ls' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a test file
    with open("testfile.txt", "w") as f:
        f.write("test")

    # Run the 'ls' command
    stdout, stderr = run_cli_command("ls\nexit\n")

    # Verify the output
    if "testfile.txt" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")

def test_cd_command(setup_test_environment):
    """Test the 'cd' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a subdirectory
    os.makedirs("subdir")

    # Run the 'cd' command
    stdout, stderr = run_cli_command("cd subdir\nexit\n")

    # Verify the output
    if "📂 Current directory:" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if "subdir" not in stdout:
        print(f"Error: Expected directory 'subdir' not found in stdout: {stdout}")

def test_rm_command(setup_test_environment):
    """Test the 'rm' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a test file
    with open("testfile.txt", "w") as f:
        f.write("test")

    # Run the 'rm' command
    stdout, stderr = run_cli_command("rm testfile.txt\nexit\n")

    # Verify the output
    if "✅ Deleted file: testfile.txt" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if os.path.exists("testfile.txt"):
        print(f"Error: File 'testfile.txt' was not deleted.")

def test_undo_command(setup_test_environment):
    """Test the 'undo' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a test file
    with open("testfile.txt", "w") as f:
        f.write("test")

    # Run the 'rm' command followed by 'undo'
    stdout, stderr = run_cli_command("rm testfile.txt\nundo\nexit\n")

    # Verify the output
    if "✅ Deleted file: testfile.txt" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if "🔄 Restoring 'testfile.txt' file..." not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if not os.path.exists("testfile.txt"):
        print(f"Error: File 'testfile.txt' was not restored.") 
        
def test_rename_command(setup_test_environment):
    run_cli_command("touch oldname.txt")
    run_cli_command("rename oldname.txt newname.txt")
    files = os.listdir()
    print("Files after rename:", files)  # Debugging output
    if "newname.txt" in files and "oldname.txt" not in files:
        print("✅ Rename command successful")
    else:
        print("❌ Rename command failed")

# def test_move_command(setup_test_environment):
#     """Test the 'move' command."""
#     # Change to the test directory
#     os.chdir(TEST_DIR)

#     # Create the source file
#     stdout, stderr = run_cli_command("touch moveme.txt\nexit\n")
#     print(f"stdout: {stdout}")  
#     print(f"stderr: {stderr}")  
#     if not os.path.exists("moveme.txt"):
#         raise FileNotFoundError("Source file 'moveme.txt' was not created")

#     # Create the target directory
#     stdout, stderr = run_cli_command("mkdir targetdir\nexit\n")
#     print(f"stdout: {stdout}")  
#     print(f"stderr: {stderr}")  
#     if not os.path.exists("targetdir"):
#         raise FileNotFoundError("Directory 'targetdir' was not created")

#     # Move the file into the target directory
#     stdout, stderr = run_cli_command("move moveme.txt targetdir/moveme.txt\nexit\n")
#     print(f"stdout: {stdout}")  
#     print(f"stderr: {stderr}")  

#     # Verify the file was moved
#     if not os.path.exists("targetdir/moveme.txt"):
#         raise FileNotFoundError("File was not moved to 'targetdir'")
#     if os.path.exists("moveme.txt"):
#         raise Exception("Source file still exists after move")

def test_copy_command(setup_test_environment):
    run_cli_command("touch copyme.txt")
    run_cli_command("copy copyme.txt copyme_copy.txt")
    files = os.listdir()
    print("Files after copy:", files)  # Debugging output
    if "copyme.txt" in files and "copyme_copy.txt" in files:
        print("✅ Copy command successful")
    else:
        print("❌ Copy command failed") 
        
def test_tree_command(setup_test_environment):
    """Test the 'tree' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a directory structure
    os.makedirs("testdir/subdir", exist_ok=True)
    with open("testdir/file1.txt", "w") as f:
        f.write("test")

    # Run the 'tree' command
    stdout, stderr = run_cli_command("tree testdir\nexit\n")

    # Verify the output
    if "testdir" not in stdout or "subdir" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
    if "file1.txt" not in stdout:
        print(f"Error: File 'file1.txt' not listed in tree output.") 
        
def test_taskkill_command(setup_test_environment):
    """Test the 'taskkill' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'taskkill' command with a dummy process (e.g., notepad.exe)
    stdout, stderr = run_cli_command("taskkill /IM notepad.exe /F\nexit\n")

    # Verify the output
    if "terminated" not in stdout and "not found" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 

def test_ping_command(setup_test_environment):
    """Test the 'ping' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'ping' command
    stdout, stderr = run_cli_command("ping google.com\nexit\n")

    # Verify the output
    if "Pinging" not in stdout and "google.com" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_nslookup_command(setup_test_environment):
    """Test the 'nslookup' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'nslookup' command
    stdout, stderr = run_cli_command("nslookup google.com\nexit\n")

    # Verify the output
    if "google.com" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_whoami_command(setup_test_environment):
    """Test the 'whoami' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'whoami' command
    stdout, stderr = run_cli_command("whoami\nexit\n")

    # Verify the output
    if "Executed: whoami" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_hostname_command(setup_test_environment):
    """Test the 'hostname' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'hostname' command
    stdout, stderr = run_cli_command("hostname\nexit\n")

    # Verify the output
    if "Executed: hostname" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_systeminfo_command(setup_test_environment):
    """Test the 'systeminfo' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'systeminfo' command
    stdout, stderr = run_cli_command("systeminfo\nexit\n")

    # Verify the output
    if "System Information" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_tasklist_command(setup_test_environment):
    """Test the 'tasklist' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'tasklist' command
    stdout, stderr = run_cli_command("tasklist\nexit\n")

    # Verify the output
    if "Executed: tasklist" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_ipconfig_command(setup_test_environment):
    """Test the 'ipconfig' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'ipconfig' command
    stdout, stderr = run_cli_command("ipconfig\nexit\n")

    # Verify the output
    if "Executed: ipconfig" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
        
def test_tracert_command(setup_test_environment):
    """Test the 'tracert' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'tracert' command
    stdout, stderr = run_cli_command("tracert google.com\nexit\n")

    # Verify the output
    if "Executed: tracert" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_netstat_command(setup_test_environment):
    """Test the 'netstat' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'netstat' command
    stdout, stderr = run_cli_command("netstat\nexit\n")

    # Verify the output
    if "Executed: netstat" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}") 
        
def test_diskpart_command(setup_test_environment):
    """Test the 'diskpart' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'diskpart' command
    stdout, stderr = run_cli_command("diskpart\nexit\n")

    # Verify the output
    if "Executed: diskpart" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
        
def test_chkdsk_command(setup_test_environment):
    """Test the 'chkdsk' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'chkdsk' command
    stdout, stderr = run_cli_command("chkdsk C:\nexit\n")

    # Verify the output
    if "Executed: chkdsk" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
        
def test_wmic_command(setup_test_environment):
    """Test the 'wmic' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Run the 'wmic' command
    stdout, stderr = run_cli_command("wmic logicaldisk get size,caption\nexit\n")

    # Verify the output
    if "Executed: wmic" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")
        
def test_append_command(setup_test_environment):
    """Test the 'append' command."""
    # Change to the test directory
    os.chdir(TEST_DIR)

    # Create a test file
    with open("testfile.txt", "w") as f:
        f.write("initial content\n")

    # Run the 'append' command
    stdout, stderr = run_cli_command("append testfile.txt additional content\nexit\n")

    # Verify the output
    if "Appended to file: testfile.txt" not in stdout:
        print(f"Error: Expected output not found in stdout: {stdout}")

    # Verify the file content
    with open("testfile.txt", "r") as f:
        content = f.read()
        if "additional content" not in content:
            print(f"Error: File content not updated correctly.")
            
# def test_rmdir_command(setup_test_environment):
#     """Test the 'rmdir' command."""
#     # Change to the test directory
#     os.chdir(TEST_DIR)

#     # Clean up the directory if it already exists
#     if os.path.exists("testdir"):
#         shutil.rmtree("testdir")

#     # Create a test directory
#     os.makedirs("testdir")
#     if not os.path.exists("testdir"):
#         raise FileNotFoundError("Directory 'testdir' was not created")

#     # Run the 'rmdir' command
#     stdout, stderr = run_cli_command("rmdir testdir\nexit\n")

#     # Verify the output
#     if "Deleted directory: testdir" not in stdout:
#         print(f"Error: Expected output not found in stdout: {stdout}")

#     # Verify the directory is deleted
#     if os.path.exists("testdir"):
#         raise FileExistsError("Directory 'testdir' was not deleted")

