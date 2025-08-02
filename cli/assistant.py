# assistant.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from help_data import HELP_TOPICS

load_dotenv()
console = Console()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize client only if API key is available
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def ask_gpt_assistant(user_question: str, history: list, current_dir: str):
    """Ask GPT with context and stream output. Fallback to offline help if needed."""

    if not client:
        console.print("[yellow]⚠ No API key found. Using offline fallback.[/]")
        return offline_help(user_question)

    cli_context = "\n".join(f"{cmd}: {desc}" for cmd, desc in HELP_TOPICS.items())
    history_context = "\n".join(f"- {cmd}" for cmd, _ in history[-5:]) or "No recent commands."

    system_message = (
        f"You are a helpful assistant for Windows CLI users.\n"
        f"Available commands:\n{cli_context}\n\n"
        f"Current working directory: {current_dir}\n"
        f"Recent commands:\n{history_context}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_question}
    ]

    try:
        # Use streaming to show content live
        with console.status("[cyan]Thinking...[/]", spinner="dots"):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                stream=True
            )

            full_answer = ""
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer += delta
                    console.print(delta, end="", soft_wrap=True)

        return "\n" + full_answer.strip()

    except Exception as e:
        if "401" in str(e) or "Invalid API key" in str(e):
            return "[red]❌ Invalid or missing API key.[/]"
        return f"[bold red]❌ Error:[/] {str(e)}"


def offline_help(question: str) -> str:
    """Fallback help when API key is missing."""
    from difflib import get_close_matches
    keywords = question.lower().split()
    matched = []

    for cmd in HELP_TOPICS:
        for word in keywords:
            if word in cmd.lower() or word in HELP_TOPICS[cmd].lower():
                matched.append((cmd, HELP_TOPICS[cmd]))

    if matched:
        output = "\n".join(f"[green]{cmd}[/]: {desc}" for cmd, desc in matched)
    else:
        # Fallback to fuzzy match
        best = get_close_matches(question, HELP_TOPICS.keys(), n=3, cutoff=0.3)
        output = "\n".join(f"[green]{cmd}[/]: {HELP_TOPICS[cmd]}" for cmd in best) if best else "[yellow]No relevant commands found.[/]"

    return output
