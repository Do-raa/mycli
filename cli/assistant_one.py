
import os
from openai import OpenAI
from help_data import HELP_TOPICS
from dotenv import load_dotenv

load_dotenv() 
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def ask_gpt_assistant(user_question: str) -> str:
    """Call OpenRouter to answer CLI-related questions intelligently."""
    context = "\n".join(
        f"{cmd}: {desc}" for cmd, desc in HELP_TOPICS.items()
    )

    messages = [
        {
            "role": "system",
            "content": f"You are a helpful CLI assistant for Windows commands. Only answer questions related to these:\n{context}"
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",  # ✅ Free model
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        if "402" in str(e) or "Insufficient credits" in str(e):
            return "[Error] 🪙 You’re out of credits on OpenRouter. Visit https://openrouter.ai/settings/credits to add more, or switch to a free model."
        return f"[Error] {str(e)}"


# def ask_gpt_assistant(user_question: str) -> str:
#     """Call OpenAI to answer CLI-related questions."""
#     context = "\n".join(
#         f"{cmd}: {desc}" for cmd, desc in HELP_TOPICS.items()
#     )

#     messages = [
#         {"role": "system", "content": f"You are a helpful CLI assistant. Only answer questions related to these commands:\n{context}"},
#         {"role": "user", "content": user_question}
#     ]

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             temperature=0.3,
#             max_tokens=300,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"[Error] {str(e)}"
