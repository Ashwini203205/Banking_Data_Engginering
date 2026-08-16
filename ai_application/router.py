from ai_application.agents.data_agent import data_agent


def route_question(question):

    question_lower = question.lower().strip()

    # =====================================================
    # 1. ML AGENT
    # =====================================================

    ml_keywords = [
        "predict",
        "prediction",
        "probability",
        "machine learning",
        "ml",
        "model",
        "classification",
        "churn",
        "likely to subscribe",
        "likely to deposit",
        "will subscribe",
        "will deposit",
        "customer prediction"
    ]

    if any(keyword in question_lower for keyword in ml_keywords):

        return {
            "agent": "ML Agent",
            "question": question,
            "result": {
                "success": True,
                "message": "ML Agent will handle this question."
            }
        }

    # =====================================================
    # 2. DATA AGENT
    # =====================================================

    data_keywords = [
        "balance",
        "customer",
        "customers",
        "education",
        "job",
        "occupation",
        "profession",
        "marital",
        "married",
        "single",
        "month",
        "monthly",
        "transaction",
        "transactions",
        "deposit",
        "subscription",
        "subscribed",
        "average",
        "total",
        "statistics",
        "summary"
    ]

    if any(keyword in question_lower for keyword in data_keywords):

        result = data_agent(question)

        return {
            "agent": "Data Agent",
            "question": question,
            "result": result
        }

    # =====================================================
    # 3. SUPPORT AGENT
    # =====================================================

    support_keywords = [
        "help",
        "support",
        "how does",
        "how do",
        "what is this",
        "explain",
        "problem",
        "issue"
    ]

    if any(keyword in question_lower for keyword in support_keywords):

        return {
            "agent": "Support Agent",
            "question": question,
            "result": {
                "success": True,
                "message": "Support Agent will handle this question."
            }
        }

    # =====================================================
    # 4. UNKNOWN QUESTION
    # =====================================================

    return {
        "agent": "Unknown",
        "question": question,
        "result": {
            "success": False,
            "message": "I could not determine which agent should handle this question."
        }
    }  





    