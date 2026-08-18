"""
AI Router — Classifies user questions and routes to the appropriate specialized agent:
- Support Agent (Architecture, pipeline, technology, FAQ)
- Data Agent (PostgreSQL Gold & Silver layer analytics, SQL queries, balances, demographics, loans, conversions)
- ML Agent (Random Forest model, subscription predictions, feature importance, evaluations)
"""

import google.generativeai as genai
from config import get_gemini_api_key, GEMINI_MODEL

from agents.support_agent import support_agent
from agents.data_agent import data_agent
from agents.ml_agent import ml_agent


ML_KEYWORDS = [
    "predict", "prediction", "probability", "machine learning", "ml",
    "model", "classification", "churn", "likely to subscribe",
    "likely to deposit", "will subscribe", "will deposit",
    "customer prediction", "train model", "model accuracy", "feature importance",
    "random forest", "k-means", "clustering algorithm",
]

DATA_KEYWORDS = [
    "balance", "customer", "customers", "education", "job", "occupation",
    "profession", "marital", "married", "single", "divorced",
    "month", "monthly", "transaction", "deposit", "subscription",
    "subscribed", "average", "total", "statistics", "summary",
    "count", "how many", "show me data", "analytics", "analysis",
    "campaign", "distribution", "loan", "housing", "segment", "segments",
    "top 10", "highest", "percentage", "rate", "insight", "insights",
]

SUPPORT_KEYWORDS = [
    "help", "support", "how does", "how do", "what is this",
    "explain", "problem", "issue", "feature", "how to use",
    "what can you do", "pipeline", "bronze", "silver", "gold",
    "architecture", "technology", "tech stack", "airflow", "spark",
    "docker", "about", "guide", "tutorial",
]


def _keyword_route(question: str) -> str | None:
    """Match question to an agent via keyword analysis."""
    q = question.lower().strip()

    # If it asks for predictions/probability/model training explicitly -> ML
    if any(kw in q for kw in ["predict", "prediction", "probability", "will subscribe", "likely to subscribe", "train model", "random forest"]):
        return "ml"

    # If it asks for balance, customer count, loans, jobs, analytics -> DATA
    if any(kw in q for kw in DATA_KEYWORDS):
        return "data"

    # Other ML keywords
    if any(kw in q for kw in ML_KEYWORDS):
        return "ml"

    # Support / Pipeline / System questions
    if any(kw in q for kw in SUPPORT_KEYWORDS):
        return "support"

    return None


def _gemini_route(question: str) -> str:
    """Use Gemini to classify the question when keywords are ambiguous."""
    key = get_gemini_api_key()
    if not key:
        return "data"
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = (
            "Classify this banking query into exactly one category. "
            "Reply with ONLY one word: 'support', 'data', or 'ml'.\n\n"
            "- 'data': questions about banking data, customer statistics, balances, loans, jobs, education, conversion rates\n"
            "- 'ml': questions about predictions, probabilities, machine learning, models, accuracy\n"
            "- 'support': questions about the data engineering pipeline, tech stack, help, Airflow, Spark, Docker\n\n"
            f"Question: {question}\n\nCategory:"
        )
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        if result in ("support", "data", "ml"):
            return result
        return "data"
    except Exception:
        return "data"


def route_question(question: str) -> dict:
    """
    Route a user question to the appropriate agent and return the structured result.
    """
    # 1. Try keyword matching
    agent_key = _keyword_route(question)
    routing_method = "keyword"

    # 2. Fallback to Gemini
    if not agent_key:
        agent_key = _gemini_route(question)
        routing_method = "gemini"

    # 3. Dispatch to the agent
    agent_map = {
        "support": {"name": "Support Agent", "icon": "🛟", "func": support_agent},
        "data":    {"name": "Data Agent",    "icon": "📊", "func": data_agent},
        "ml":      {"name": "ML Agent",      "icon": "🧠", "func": ml_agent},
    }

    agent_info = agent_map.get(agent_key, agent_map["data"])
    result = agent_info["func"](question)

    return {
        "agent_key": agent_key,
        "agent_name": agent_info["name"],
        "agent_icon": agent_info["icon"],
        "question": question,
        "result": result,
        "routing_method": routing_method,
    }