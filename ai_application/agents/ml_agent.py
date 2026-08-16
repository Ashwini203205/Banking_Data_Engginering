import psycopg2


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "banking_db",
    "user": "admin",
    "password": "password123"
}


def get_customer_data():

    query = """
    SELECT
        age,
        job,
        marital,
        education,
        balance,
        housing,
        loan,
        duration,
        campaign,
        pdays,
        previous,
        poutcome,
        y
    FROM silver.customer_clean;
    """

    connection = None
    cursor = None

    try:

        connection = psycopg2.connect(**DB_CONFIG)

        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]

        return {
            "success": True,
            "columns": columns,
            "data": rows
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


def ml_agent(question):

    question_lower = question.lower()

    # -------------------------------------------------
    # Check whether the question is a prediction question
    # -------------------------------------------------

    prediction_keywords = [
        "predict",
        "prediction",
        "likely",
        "probability",
        "subscribe",
        "subscription",
        "machine learning",
        "ml model"
    ]

    if not any(
        keyword in question_lower
        for keyword in prediction_keywords
    ):

        return {
            "success": False,
            "message": "This does not appear to be an ML prediction question."
        }

    # -------------------------------------------------
    # Load customer data
    # -------------------------------------------------

    customer_data = get_customer_data()

    if not customer_data["success"]:

        return customer_data

    # -------------------------------------------------
    # Return dataset information for now
    # -------------------------------------------------

    return {
        "success": True,
        "agent": "ML Agent",
        "message": "Customer data successfully loaded for machine learning.",
        "rows": len(customer_data["data"]),
        "columns": customer_data["columns"]
    }