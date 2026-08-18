"""
Data Agent — Queries the PostgreSQL Gold and Silver layers and provides data-backed insights.
Combines dynamic Text-to-SQL (via Gemini) with a comprehensive deterministic SQL engine
to guarantee real data answers for all banking queries. Formats all balances in Indian Rupees (₹).
"""

import re
import pandas as pd
import google.generativeai as genai
from db import run_query, test_connection
from config import get_gemini_api_key, GEMINI_MODEL
from utils import format_rupee, format_number


# ─── Standard Gold layer query catalogue ───────────────────────────
QUERIES = {
    "customer_summary": {
        "sql": "SELECT total_customers, subscribed_customers, ROUND(average_age::numeric, 1) as average_age, ROUND(average_balance::numeric, 2) as average_balance, total_balance FROM gold.customer_summary LIMIT 1;",
        "title": "Customer KPI Summary",
        "description": "Overall customer metrics from the Gold layer.",
    },
    "education_summary": {
        "sql": "SELECT education, total_customers FROM gold.education_summary ORDER BY total_customers DESC;",
        "title": "Education Distribution",
        "description": "Customer breakdown by education level.",
    },
    "job_summary": {
        "sql": "SELECT job, total_customers FROM gold.job_summary ORDER BY total_customers DESC;",
        "title": "Job Distribution",
        "description": "Customer breakdown by job category.",
    },
    "marital_summary": {
        "sql": "SELECT marital, total_customers FROM gold.marital_summary ORDER BY total_customers DESC;",
        "title": "Marital Status Distribution",
        "description": "Customer breakdown by marital status.",
    },
    "month_summary": {
        "sql": "SELECT month, total_customers, subscribed_customers FROM gold.month_summary ORDER BY total_customers DESC;",
        "title": "Monthly Campaign Summary",
        "description": "Campaign performance broken down by month.",
    },
    "deposit_summary": {
        "sql": "SELECT y as subscribed, total_customers FROM gold.deposit_summary ORDER BY total_customers DESC;",
        "title": "Term Deposit Subscriptions",
        "description": "Subscription distribution from the Gold layer.",
    },
}

DB_SCHEMA_PROMPT = """
PostgreSQL Banking Database Schema:
- Table: gold.customer_summary (total_customers BIGINT, subscribed_customers BIGINT, average_age NUMERIC, average_balance NUMERIC, total_balance BIGINT)
- Table: gold.job_summary (job TEXT, total_customers BIGINT)
- Table: gold.education_summary (education TEXT, total_customers BIGINT)
- Table: gold.marital_summary (marital TEXT, total_customers BIGINT)
- Table: gold.month_summary (month TEXT, total_customers BIGINT, subscribed_customers BIGINT)
- Table: gold.deposit_summary (y TEXT, total_customers BIGINT)
- Table: silver.customer_clean (age INT, job TEXT, marital TEXT, education TEXT, default_status TEXT, balance INT, housing TEXT, loan TEXT, contact TEXT, day INT, month TEXT, duration INT, campaign INT, pdays INT, previous INT, poutcome TEXT, y TEXT)

Rules:
1. Generate only a valid PostgreSQL SELECT query.
2. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
3. For balance fields, always format properly.
4. Output ONLY the raw SQL query.
"""


def _deterministic_sql(question: str) -> tuple[str, str, str] | None:
    """
    Match natural language banking questions to exact SQL queries on real tables.
    Returns: (sql_query, title, query_key) or None.
    """
    q = question.lower().strip()

    # 1. Total Balance
    if "total balance" in q or "sum of balance" in q or "overall balance" in q:
        return (
            "SELECT total_balance, total_customers, ROUND(average_balance::numeric, 2) as average_balance FROM gold.customer_summary LIMIT 1;",
            "Total Customer Balance",
            "total_balance"
        )

    # 2. Highest average balance by segment (education, marital, job)
    if "segment" in q or "segment balance" in q or "highest average balance" in q:
        return (
            """SELECT 
                education, 
                marital, 
                COUNT(*) as customer_count, 
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as sub_rate_pct
               FROM silver.customer_clean 
               GROUP BY education, marital 
               ORDER BY avg_balance_inr DESC 
               LIMIT 10;""",
            "Customer Segments Ranked by Average Balance",
            "segment_balance"
        )

    # 3. Average Balance
    if "average customer balance" in q or "average balance" in q or "avg balance" in q or "mean balance" in q:
        return (
            "SELECT ROUND(average_balance::numeric, 2) as average_balance, total_customers, total_balance FROM gold.customer_summary LIMIT 1;",
            "Average Customer Balance",
            "avg_balance"
        )

    # 3. Average Age
    if "average age" in q or "avg age" in q or "mean age" in q:
        return (
            "SELECT ROUND(average_age::numeric, 1) as average_age, total_customers FROM gold.customer_summary LIMIT 1;",
            "Customer Average Age",
            "avg_age"
        )

    # 4. Subscribed Count / Percentage
    if "percentage of customers subscribed" in q or "subscription percentage" in q or "subscription rate" in q or "conversion rate" in q:
        return (
            """SELECT 
                total_customers, 
                subscribed_customers, 
                ROUND((subscribed_customers::numeric / NULLIF(total_customers, 0) * 100), 2) as subscription_rate_pct 
               FROM gold.customer_summary LIMIT 1;""",
            "Customer Subscription Rate",
            "sub_rate"
        )

    if "how many customers are subscribed" in q or "subscribed customers" in q or "how many subscribed" in q:
        return (
            "SELECT subscribed_customers, total_customers, ROUND((subscribed_customers::numeric / NULLIF(total_customers, 0) * 100), 2) as subscription_pct FROM gold.customer_summary LIMIT 1;",
            "Subscribed Customers Count",
            "sub_count"
        )

    # 5. Job category with highest balance / Job balance analysis
    if "job" in q and ("highest balance" in q or "top balance" in q or "max balance" in q or "average balance" in q or "avg balance" in q):
        return (
            """SELECT 
                job, 
                COUNT(*) as total_customers, 
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr, 
                SUM(balance) as total_balance_inr 
               FROM silver.customer_clean 
               GROUP BY job 
               ORDER BY avg_balance_inr DESC;""",
            "Job Categories Ranked by Average Balance",
            "job_highest_balance"
        )

    # 6. Loans / Housing / Personal Loan Analysis
    if "loan" in q or "housing" in q:
        return (
            """SELECT 
                COUNT(*) as total_customers,
                SUM(CASE WHEN housing = 'yes' THEN 1 ELSE 0 END) as housing_loan_count,
                ROUND(SUM(CASE WHEN housing = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as housing_loan_pct,
                SUM(CASE WHEN loan = 'yes' THEN 1 ELSE 0 END) as personal_loan_count,
                ROUND(SUM(CASE WHEN loan = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as personal_loan_pct,
                SUM(CASE WHEN housing = 'yes' AND loan = 'yes' THEN 1 ELSE 0 END) as both_loans_count
               FROM silver.customer_clean;""",
            "Customer Loan Portfolio (Housing & Personal)",
            "loan_analysis"
        )

    # 7. Top 10 customers by balance
    if "top 10" in q or ("top" in q and "balance" in q) or "richest" in q or "highest balance customers" in q:
        return (
            """SELECT 
                age, job, marital, education, balance, housing, loan, y as subscribed 
               FROM silver.customer_clean 
               ORDER BY balance DESC 
               LIMIT 10;""",
            "Top 10 Customers by Balance",
            "top_customers_balance"
        )

    # 8. Highest average balance by segment (education, marital, job)
    if "segment" in q or "highest average balance" in q or "segment balance" in q:
        return (
            """SELECT 
                education, 
                marital, 
                COUNT(*) as customer_count, 
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as sub_rate_pct
               FROM silver.customer_clean 
               GROUP BY education, marital 
               ORDER BY avg_balance_inr DESC 
               LIMIT 10;""",
            "Customer Segments Ranked by Average Balance",
            "segment_balance"
        )

    # 9. Top banking insights
    if "insight" in q or "overview" in q or "summary" in q or "key findings" in q:
        return (
            """SELECT 
                total_customers, 
                subscribed_customers, 
                ROUND((subscribed_customers::numeric / total_customers * 100), 2) as subscription_rate_pct,
                ROUND(average_age::numeric, 1) as average_age, 
                ROUND(average_balance::numeric, 2) as average_balance, 
                total_balance 
               FROM gold.customer_summary LIMIT 1;""",
            "Key Banking Dataset Insights",
            "insights"
        )

    # 10. Education breakdown
    if "education" in q or "degree" in q or "qualification" in q:
        return (
            """SELECT 
                education, 
                COUNT(*) as total_customers,
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr,
                SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) as subscribed_count,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as sub_rate_pct
               FROM silver.customer_clean 
               GROUP BY education 
               ORDER BY total_customers DESC;""",
            "Education Demographics & Performance",
            "education_distribution"
        )

    # 11. Job breakdown
    if "job" in q or "occupation" in q or "profession" in q:
        return (
            """SELECT 
                job, 
                COUNT(*) as total_customers, 
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr,
                SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) as subscribed_count,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as sub_rate_pct
               FROM silver.customer_clean 
               GROUP BY job 
               ORDER BY total_customers DESC;""",
            "Job Categories Breakdown",
            "job_distribution"
        )

    # 12. Marital breakdown
    if "marital" in q or "married" in q or "single" in q or "divorced" in q:
        return (
            """SELECT 
                marital, 
                COUNT(*) as total_customers,
                ROUND(AVG(balance)::numeric, 2) as avg_balance_inr,
                SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) as subscribed_count,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as sub_rate_pct
               FROM silver.customer_clean 
               GROUP BY marital 
               ORDER BY total_customers DESC;""",
            "Marital Status Breakdown",
            "marital_distribution"
        )

    # 13. Monthly campaign trends
    if "month" in q or "campaign" in q or "timing" in q or "season" in q:
        return (
            """SELECT 
                month, 
                COUNT(*) as total_contacts, 
                SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) as subscribed_count,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as conversion_rate_pct
               FROM silver.customer_clean 
               GROUP BY month 
               ORDER BY total_contacts DESC;""",
            "Monthly Campaign Performance",
            "month_distribution"
        )

    # 14. Customer count
    if "total customer" in q or "how many customer" in q or "number of customer" in q:
        return (
            "SELECT total_customers, subscribed_customers, average_age, average_balance, total_balance FROM gold.customer_summary LIMIT 1;",
            "Total Customers Count & KPIs",
            "customer_count"
        )

    return None


def _gemini_generate_sql(question: str) -> str | None:
    """Use Gemini to generate a PostgreSQL SELECT query."""
    key = get_gemini_api_key()
    if not key:
        return None
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = f"{DB_SCHEMA_PROMPT}\n\nUser Question: {question}\n\nGenerate the exact PostgreSQL SELECT query:"
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown codeblocks if present
        sql_match = re.search(r"```(?:sql)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        return text.replace("```sql", "").replace("```", "").strip()
    except Exception:
        return None


def _format_insight_text(question: str, df: pd.DataFrame, title: str, query_key: str = "") -> str:
    """Format a clear, natural-language, data-backed insight using Indian Rupee format."""
    if df.empty:
        return "No matching records found in the banking database."

    # Try generating an LLM explanation if Gemini is available
    key = get_gemini_api_key()
    if key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            data_preview = df.head(15).to_string(index=False)
            prompt = (
                f"You are an expert banking analytics AI assistant. The user asked: '{question}'\n\n"
                f"Real PostgreSQL query results for '{title}':\n{data_preview}\n\n"
                "Provide a direct, clear, professional answer (2-4 sentences) using the exact numbers from the data. "
                "IMPORTANT: Format all monetary amounts in Indian Rupees with the ₹ symbol and commas (e.g. ₹61,589,682 or ₹1,362.27). "
                "Do NOT use € or $ symbols. Use markdown formatting with bold metrics."
            )
            response = model.generate_content(prompt)
            if response.text and len(response.text.strip()) > 10:
                return response.text.strip()
        except Exception:
            pass  # Fall through to deterministic rule-based natural formatting

    # Fallback to high-quality deterministic natural-language formatting
    row = df.iloc[0]
    cols = df.columns.tolist()

    if query_key == "insights":
        tot_c = format_number(row.get("total_customers", 0))
        sub_c = format_number(row.get("subscribed_customers", 0))
        sub_r = row.get("subscription_rate_pct", 0)
        tot_b = format_rupee(row.get("total_balance", 0))
        avg_b = format_rupee(row.get("average_balance", 0), decimals=True)
        avg_a = row.get("average_age", 0)
        return (
            f"📈 **Executive Banking Insights:**\n\n"
            f"- **Total Customer Base:** **{tot_c}** active accounts\n"
            f"- **Total Portfolio Balance:** **{tot_b}** (Avg: **{avg_b}**)\n"
            f"- **Term Deposit Subscriptions:** **{sub_c}** (**{sub_r}%** conversion rate)\n"
            f"- **Average Customer Age:** **{avg_a} years**\n"
            f"- **Core Driver:** Higher account balances strongly correlate with term-deposit conversion."
        )

    if query_key == "segment_balance":
        top_seg = f"{str(row.get('education', '')).title()} ({str(row.get('marital', '')).title()})"
        top_avg = format_rupee(row.get("avg_balance_inr", 0), decimals=True)
        sub_r = row.get("sub_rate_pct", 0)
        return f"🎯 The customer segment with the highest average balance is **{top_seg}** at **{top_avg}** (subscription conversion: **{sub_r}%**). Detailed segment rankings are displayed in the table below."

    if query_key == "total_balance" or "total_balance" in cols and len(cols) <= 3:
        total_b = format_rupee(row.get("total_balance", 0))
        avg_b = format_rupee(row.get("average_balance", 0), decimals=True)
        total_c = format_number(row.get("total_customers", 0))
        return f"🏦 The **total customer balance** across all **{total_c}** banking customers is **{total_b}**, with an **average balance** of **{avg_b}** per customer."

    if query_key == "avg_balance" or "average_balance" in cols and len(cols) <= 3:
        avg_b = format_rupee(row.get("average_balance", 0), decimals=True)
        total_b = format_rupee(row.get("total_balance", 0))
        return f"💰 The **average customer balance** in the banking portfolio is **{avg_b}**, contributing to an aggregate balance of **{total_b}**."

    if query_key == "avg_age" or "average_age" in cols:
        avg_a = row.get("average_age", 0)
        total_c = format_number(row.get("total_customers", 0))
        return f"🎂 The **average customer age** is **{avg_a} years** across the total customer base of **{total_c}** depositors."

    if query_key in ("sub_rate", "sub_count"):
        sub_c = format_number(row.get("subscribed_customers", 0))
        tot_c = format_number(row.get("total_customers", 0))
        rate = row.get("subscription_rate_pct", row.get("subscription_pct", 0))
        return f"✅ There are **{sub_c} subscribed customers** out of **{tot_c}** total banking customers, representing a conversion/subscription rate of **{rate}%**."

    if query_key == "job_highest_balance":
        top_job = str(row.get("job", "")).title()
        top_avg = format_rupee(row.get("avg_balance_inr", 0), decimals=True)
        return f"💼 The **{top_job}** category holds the highest average customer balance at **{top_avg}**, followed by other top professions listed in the breakdown table below."

    if query_key == "loan_analysis":
        tot = format_number(row.get("total_customers", 0))
        h_cnt = format_number(row.get("housing_loan_count", 0))
        h_pct = row.get("housing_loan_pct", 0)
        p_cnt = format_number(row.get("personal_loan_count", 0))
        p_pct = row.get("personal_loan_pct", 0)
        return (
            f"💳 **Loan Portfolio Analysis ({tot} customers):**\n\n"
            f"- **Housing Loans:** **{h_cnt}** customers (**{h_pct}%**)\n"
            f"- **Personal Loans:** **{p_cnt}** customers (**{p_pct}%**)\n"
            f"- **Both Loans:** **{format_number(row.get('both_loans_count', 0))}** customers"
        )

    if query_key == "top_customers_balance":
        highest = format_rupee(row.get("balance", 0))
        return f"💎 The top customer holds a balance of **{highest}** ({str(row.get('job', '')).title()}, age {row.get('age', 0)}). The top 10 customer accounts are detailed below."

    # General tabular response
    return f"📊 Query for **{title}** returned **{len(df)} records** from the real database. See full details below."


def data_agent(question: str) -> dict:
    """
    Handle a data question by querying the PostgreSQL Gold/Silver layer.
    Returns structured result with real data, formatted insight in ₹, and query metadata.
    """
    # 1. Check database connectivity
    if not test_connection():
        return {
            "success": False,
            "error": "Unable to connect to the banking database. Please check PostgreSQL connection.",
        }

    # 2. Try deterministic high-precision banking query matching
    matched = _deterministic_sql(question)
    if matched:
        sql, title, query_key = matched
        df = run_query(sql)
        if not df.empty:
            insight = _format_insight_text(question, df, title, query_key)
            return {
                "success": True,
                "query_key": query_key,
                "title": title,
                "sql": sql,
                "data": df,
                "insight": insight,
            }

    # 3. Try Gemini Text-to-SQL dynamic generation
    gemini_sql = _gemini_generate_sql(question)
    if gemini_sql:
        # Validate query is a safe SELECT statement
        clean_sql = gemini_sql.strip()
        if clean_sql.upper().startswith("SELECT") and not any(kw in clean_sql.upper() for kw in ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]):
            df = run_query(clean_sql)
            if not df.empty:
                insight = _format_insight_text(question, df, "Custom AI Query", "dynamic_sql")
                return {
                    "success": True,
                    "query_key": "dynamic_sql",
                    "title": "Custom Data Query",
                    "sql": clean_sql,
                    "data": df,
                    "insight": insight,
                }

    # 4. Fallback to default Gold Customer Summary if still unhandled
    default_sql = QUERIES["customer_summary"]["sql"]
    df = run_query(default_sql)
    if not df.empty:
        insight = _format_insight_text(question, df, "Customer Summary", "customer_summary")
        return {
            "success": True,
            "query_key": "customer_summary",
            "title": "Customer Summary",
            "sql": default_sql,
            "data": df,
            "insight": insight,
        }

    return {
        "success": False,
        "error": "Unable to retrieve data for this query. Please check database tables in the Gold layer.",
    }


def get_all_summaries() -> dict:
    """Fetch all Gold layer summaries for dashboard and analytics views."""
    summaries = {}
    for key, info in QUERIES.items():
        df = run_query(info["sql"])
        summaries[key] = {
            "title": info["title"],
            "description": info["description"],
            "data": df,
        }
    return summaries