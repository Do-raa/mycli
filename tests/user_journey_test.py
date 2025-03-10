import subprocess
import time
import platform
import pytest

# Global variable to hold the shell process
shell_process = None

# Function to start the shell process
def start_shell():
    global shell_process
    if platform.system() == "Windows":
        shell_process = subprocess.Popen(
            ["python", "cli/main.py"],  # Adjust if necessary
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True  # Required for Windows
        )
    else:
        shell_process = subprocess.Popen(
            ["python3", "cli/main.py"],  # Adjust if necessary
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    # Wait for the shell to initialize
    time.sleep(2)

# Function to send a command to the shell and read output
def send_command(command):
    shell_process.stdin.write(command + "\n")
    shell_process.stdin.flush()
    time.sleep(0.5)  # Allow time for execution
    output = shell_process.stdout.readline().strip()
    return output

# Function to read all available output from the shell
def read_shell_output():
    output = []
    while True:
        line = shell_process.stdout.readline().strip()
        if not line:  # Break if there's no more output
            break
        output.append(line)
    return "\n".join(output)

# Function to stop the shell process
def stop_shell():
    if shell_process:
        shell_process.terminate()
        shell_process.wait()

# Fixture to start and stop the shell for each test
@pytest.fixture(scope="module", autouse=True)
def shell_fixture():
    start_shell()
    yield
    stop_shell()

# 🟢 TEST: Basic shell startup
def test_shell_startup():
    startup_output = read_shell_output()
    print(f"🛠 Debug: Shell startup output = {startup_output}")
    assert "✨ >" in startup_output, f"❌ Shell startup failed: {startup_output}"

# 🟢 TEST: Create & navigate directories
def test_create_and_navigate_directories():
    assert "✨ >" in send_command("mkdir testdir"), "❌ mkdir failed"
    assert "✨ >" in send_command("cd testdir"), "❌ cd failed"

# 🟢 TEST: Create and modify files
def test_create_and_modify_files():
    assert "✨ >" in send_command("touch myfile.txt"), "❌ touch command failed"
    assert "✨ >" in send_command("append myfile.txt 'Hello, world!'"), "❌ append failed"

# 🟢 TEST: Undo last action
def test_undo_last_action():
    assert "✨ >" in send_command("undo"), "❌ Undo failed"

# 🟢 TEST: Auto-correction
def test_auto_correction():
    output = send_command("mkdr anotherdir")
    assert "✅ Auto-correcting 'mkdr' to 'mkdir'" in output, "❌ Auto-correction failed"

# 🟢 TEST: History navigation (simulate pressing 'Up' arrow key)
def test_history_navigation():
    send_command("up")  # Simulate pressing the 'Up' arrow key
    time.sleep(0.5)
    send_command("\n")  # Simulate pressing 'Enter'
    history_output = shell_process.stdout.readline().strip()
    assert "mkdir anotherdir" in history_output, "❌ History navigation failed"

# 🟢 TEST: Tab Autocompletion (if supported by shell)
def test_tab_autocompletion():
    send_command("touch samplefile.txt")
    time.sleep(0.5)
    send_command("cat s\t")  # Simulate typing 'cat s' and pressing Tab
    time.sleep(0.5)
    send_command("\n")  # Simulate pressing Enter
    autocomplete_output = shell_process.stdout.readline().strip()
    assert "samplefile.txt" in autocomplete_output, "❌ Autocompletion failed"

# 🟢 TEST: Interactive prompt (simulating input prompt)
def test_interactive_prompt():
    send_command("confirm 'Are you sure?'")
    time.sleep(1)
    send_command("y")  # Simulate pressing 'y' for yes
    confirm_output = shell_process.stdout.readline().strip()
    assert "Confirmed" in confirm_output, "❌ Interactive prompt failed"

# 🟢 TEST: Exit shell
def test_exit_shell():
    send_command("exit")
    time.sleep(1)  # Allow time for the shell to exit
    assert shell_process.poll() is not None, "❌ Shell did not exit correctly"