# assistant.py
"""
Expert AI Agent Module - Provides intelligent Windows CLI assistance
with conversation memory and domain-specific expertise.

This module implements a specialized AI agent for command-line operations,
featuring context-aware responses and professional-grade architecture.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from help_data import HELP_TOPICS

load_dotenv()
console = Console()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Conversation memory
conversation_history = []

def is_windows_cli_related(question: str) -> bool:
    """Check if question is related to Windows CLI in general"""
    question_lower = question.lower()
    
    # Broad Windows CLI keywords
    windows_cli_keywords = [
        # Core CLI concepts
        "cmd", "command", "cli", "terminal", "shell", "powershell", "command prompt",
        "dos", "console", "prompt", "batch", "script",
        
        # Common CLI actions
        "navigate", "directory", "folder", "file", "create", "delete", "remove", 
        "copy", "move", "rename", "list", "show", "display", "find", "search",
        "execute", "run", "launch", "install", "configure", "set up",
        
        # Windows-specific
        "windows", "microsoft", "c:\\", "c:/", "system32", "environment variable",
        "registry", "service", "process", "task", "administrator", "admin",
        
        # Networking
        "network", "ip", "ping", "tracert", "netstat", "ipconfig", "dns", 
        "connection", "port", "router", "gateway", "subnet",
        
        # System management
        "system", "disk", "partition", "volume", "drive", "memory", "cpu",
        "process", "service", "user", "group", "permission", "security",
        
        # File operations
        "text", "edit", "view", "read", "write", "append", "concatenate",
        "sort", "filter", "grep", "findstr", "more", "type", "echo",
        
        # Development tools (when used in CLI context)
        "git", "docker", "npm", "pip", "python", "java", "node", "compile",
        
        # Command patterns
        "how to", "how do i", "command for", "what is", "explain",
        "usage of", "syntax for", "example of", "help with", "tutorial"
    ]
    
    # Check if question contains any Windows CLI keywords
    has_cli_keyword = any(keyword in question_lower for keyword in windows_cli_keywords)
    
    # Check for command mentions (from HELP_TOPICS or common commands)
    common_commands = list(HELP_TOPICS.keys()) + [
        "attrib", "chmod", "chown", "cls", "color", "date", "del", "echo",
        "fc", "find", "format", "ftype", "grep", "help", "more", "path",
        "pause", "popd", "pushd", "rd", "reg", "robocopy", "sc", "schtasks",
        "set", "setx", "sfc", "shutdown", "sort", "start", "subst", "time",
        "title", "ver", "vol", "where", "xcopy"
    ]
    
    has_command_mention = any(cmd in question_lower for cmd in common_commands)
    
    return has_cli_keyword or has_command_mention

def ask_gpt_assistant(user_question: str, current_dir: str):
    """Ask GPT about any Windows CLI-related questions with conversation memory"""
    
    # ✅ Step 1: Broad Windows CLI filtering
    if not is_windows_cli_related(user_question):
        return (
            "🚫 I can only answer questions about Windows Command Line (CLI) topics.\n"
            "This includes commands, scripting, terminal usage, file operations, "
            "networking, system administration, and related Windows CLI concepts.\n\n"
            "Please ask about Windows command prompt, PowerShell, or CLI tools."
        )

    # ✅ Step 2: API check
    if not client:
        console.print("[yellow]⚠ No API key found. Using offline fallback.[/]")
        return offline_help(user_question)

    # ✅ Step 3: Build comprehensive CLI context
    cli_context = "\n".join(f"• {cmd}: {desc}" for cmd, desc in HELP_TOPICS.items())

    # ✅ Step 4: Maintain conversation history
    global conversation_history
    conversation_history.append({"role": "user", "content": user_question})
    
    # Keep only last 10 messages to avoid context overflow
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    system_message = (
        "You are an expert Windows CLI assistant. Answer questions about ANY Windows Command Line topics including:\n\n"
        "• Command syntax and usage\n• PowerShell and CMD commands\n• File system operations\n• Networking commands\n"
        "• System administration\n• Scripting and automation\n• Environment variables\n• Process management\n"
        "• And any other Windows CLI-related topics\n\n"
        f"Common commands reference:\n{cli_context}\n\n"
        "RULES:\n"
        "1. Provide accurate, technical answers about Windows CLI\n"
        "2. Give clear examples and syntax\n"
        "3. If unsure, say so rather than guessing\n"
        "4. Keep responses concise but informative\n"
        "5. Maintain conversation context\n\n"
        f"Current directory: {current_dir}\n"
        "User is a Windows CLI user seeking technical assistance."
    )

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history  # Include all conversation history
    ]

    try:
        # ✅ Step 5: Get response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=400,
            stream=False
        )

        assistant_response = response.choices[0].message.content.strip()
        
        # Add assistant response to history
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response

    except Exception as e:
        if "401" in str(e) or "Invalid API key" in str(e):
            return "[red]❌ Invalid or missing API key.[/]"
        return f"[bold red]❌ Error:[/] {str(e)}"

def offline_help(question: str) -> str:
    """Fallback help when API key is missing"""
    from difflib import get_close_matches
    
    question_lower = question.lower()
    matched_commands = []
    
    # Direct command matching
    for cmd, desc in HELP_TOPICS.items():
        if cmd in question_lower:
            matched_commands.append((cmd, desc))
    
    # If no direct match, try fuzzy matching
    if not matched_commands:
        best_matches = get_close_matches(question, HELP_TOPICS.keys(), n=3, cutoff=0.3)
        matched_commands = [(cmd, HELP_TOPICS[cmd]) for cmd in best_matches]
    
    if matched_commands:
        output = "🤖 Offline Help (limited to known commands):\n\n"
        for cmd, desc in matched_commands:
            output += f"[green]● {cmd}[/]: {desc}\n\n"
        return output
    else:
        return (
            "🤖 I can help with Windows CLI questions, but I need API access for detailed answers.\n"
            "Available offline commands: " + ", ".join(HELP_TOPICS.keys()) + "\n"
            "Try asking about specific commands or enable API access for full assistance."
        )

def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []