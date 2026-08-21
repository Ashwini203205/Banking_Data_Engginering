"""
Centralized configuration for the Banking AI Application.
Reads environment variables and defines constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


#  Load .env from project root 
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


#  Gemini AI 
GEMINI_MODEL = "gemini-2.0-flash"

def get_gemini_api_key():
    """Dynamically get Gemini API Key from Streamlit session state or .env."""
    import os
    import streamlit as st
    try:
        if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"].strip():
            return st.session_state["gemini_api_key"].strip()
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


# PostgreSQL 
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "banking_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
}

#  Chart Color Sequence 
CHART_COLORS = [
    "#00B4D8", "#2EC4B6", "#FFB703", "#E63946",
    "#7B2CBF", "#06D6A0", "#FB5607", "#3A86FF",
    "#8338EC", "#FF006E",
]