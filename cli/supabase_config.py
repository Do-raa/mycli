import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set!")

supabase: Client = create_client(url, key)


