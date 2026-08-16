def route_question(question):
    question = question.lower()

    support_keywords = [
        "help",
        "how to use",
        "what can you do",
        "support",
        "application",
        "feature"
    ]

    ml_keywords = [
        "predict",
        "prediction",
        "machine learning",
        "ml",
        "model",
        "cluster",
        "segment",
        "churn",
        "classification"
    ]

    data_keywords = [
        "customer",
        "customers",
        "balance",
        "education",
        "job",
        "marital",
        "month",
        "subscription",
        "subscribed",
        "average",
        "total",
        "count",
        "data",
        "analysis"
    ]

    for keyword in support_keywords:
        if keyword in question:
            return "Support Agent"

    for keyword in ml_keywords:
        if keyword in question:
            return "ML Agent"

    for keyword in data_keywords:
        if keyword in question:
            return "Data Agent"

    return "Data Agent"