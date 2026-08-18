"""
Support Agent — Answers application, pipeline, and domain questions.
Uses Gemini for natural-language responses; falls back to rule-based FAQs.
"""

import google.generativeai as genai
from config import get_gemini_api_key, GEMINI_MODEL


# ─── Pre-built FAQ database ────────────────────────────────────────
FAQ = {
    "pipeline": (
        "Our data pipeline follows the **Medallion Architecture** "
        "(Bronze → Silver → Gold):\n\n"
        "• **Bronze Layer** — Raw CSV data ingested into `bronze.customer_raw`\n"
        "• **Silver Layer** — Cleaned & validated data in `silver.customer_clean`\n"
        "• **Gold Layer** — Aggregated summaries (customer, education, job, marital, month)\n\n"
        "The pipeline is orchestrated by **Apache Airflow** and processed via **Apache Spark**, "
        "with data stored in **PostgreSQL**."
    ),
    "features": (
        "This application offers:\n\n"
        "🤖 **AI Assistant** — Ask natural-language questions routed to specialised agents\n"
        "📊 **Data Analytics** — Interactive charts & tables from the Gold layer\n"
        "🧠 **Machine Learning** — Subscription prediction with Random Forest\n"
        "👥 **Customer Segmentation** — K-Means clustering analysis\n"
        "📄 **Reports** — AI-generated executive summaries & downloadable reports"
    ),
    "agents": (
        "We have three intelligent agents:\n\n"
        "🛟 **Support Agent** — Answers app & pipeline questions (that's me!)\n"
        "📊 **Data Agent** — Queries the Gold layer and explains results\n"
        "🧠 **ML Agent** — Runs predictions and explains model insights\n\n"
        "The **AI Router** automatically selects the best agent for your question."
    ),
    "data": (
        "The dataset is from a **Portuguese banking institution** marketing campaign. "
        "It contains **45,211 records** with 17 attributes including:\n\n"
        "• Demographics: age, job, marital status, education\n"
        "• Financial: balance, housing loan, personal loan\n"
        "• Campaign: contact type, day, month, duration, campaign count\n"
        "• Outcome: whether the customer subscribed to a term deposit (yes/no)"
    ),
    "technology": (
        "**Tech Stack:**\n\n"
        "• **Orchestration:** Apache Airflow\n"
        "• **Processing:** Apache Spark (PySpark)\n"
        "• **Storage:** PostgreSQL 15\n"
        "• **Containerisation:** Docker & Docker Compose\n"
        "• **AI / ML:** Gemini AI, scikit-learn (Random Forest)\n"
        "• **Frontend:** Streamlit with Plotly charts"
    ),
}


def _match_faq(question: str) -> str | None:
    """Simple keyword matching against the FAQ database."""
    q = question.lower()
    if any(w in q for w in ["pipeline", "bronze", "silver", "gold", "airflow", "spark", "etl"]):
        return FAQ["pipeline"]
    if any(w in q for w in ["feature", "can you do", "what can", "capability", "module"]):
        return FAQ["features"]
    if any(w in q for w in ["agent", "router", "support agent", "data agent", "ml agent"]):
        return FAQ["agents"]
    if any(w in q for w in ["dataset", "data source", "bank data", "records", "attributes", "columns"]):
        return FAQ["data"]
    if any(w in q for w in ["technology", "tech stack", "built with", "framework", "tools used"]):
        return FAQ["technology"]
    return None


def _gemini_answer(question: str) -> str:
    """Use Gemini to generate a support answer."""
    key = get_gemini_api_key()
    if not key:
        return ""
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        system_prompt = (
            "You are a helpful support agent for the Banking AI Analytics application. "
            "The application is built on a data engineering pipeline (Airflow + Spark + PostgreSQL) "
            "with a Bronze → Silver → Gold Medallion Architecture. "
            "It also includes ML-based subscription prediction and AI-powered analytics. "
            "Answer the user's question concisely and helpfully. "
            "Use markdown formatting. Keep answers under 200 words."
        )

        response = model.generate_content(f"{system_prompt}\n\nUser question: {question}")
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini unavailable: {e}"


def support_agent(question: str) -> dict:
    """
    Handle a support question. Tries FAQ first, then Gemini.
    Returns: {"success": bool, "answer": str, "source": str}
    """
    # 1. Try FAQ
    faq_answer = _match_faq(question)
    if faq_answer:
        return {"success": True, "answer": faq_answer, "source": "FAQ Knowledge Base"}

    # 2. Try Gemini
    gemini_answer = _gemini_answer(question)
    if gemini_answer and not gemini_answer.startswith("⚠️"):
        return {"success": True, "answer": gemini_answer, "source": "Gemini AI"}

    # 3. Fallback
    err_msg = ""
    if gemini_answer.startswith("⚠️"):
        err_msg = "\n\n*(Note: Gemini returned an authentication/connection error. Please verify your API Key in the sidebar.)*"

    return {
        "success": True,
        "answer": (
            "I'm the Support Agent! I can help with questions about:\n\n"
            "• The data pipeline and architecture\n"
            "• Application features and modules\n"
            "• The banking dataset\n"
            "• Technology stack\n\n"
            "Try asking: *'How does the pipeline work?'* or *'What features are available?'*"
            f"{err_msg}"
        ),
        "source": "Default Response (Fallback)",
    }
