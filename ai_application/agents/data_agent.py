import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "banking_db",
    "user": "admin",
    "password": "password123"
}


def execute_query(query):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute(query)

        result = cursor.fetchall()

        columns = [description[0] for description in cursor.description]

        return {
            "success": True,
            "columns": columns,
            "data": result
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


# ---------------------------------------------------------
# CUSTOMER SUMMARY
# ---------------------------------------------------------

def get_customer_summary():

    query = """
    SELECT
        total_customers,
        subscribed_customers,
        average_age,
        average_balance,
        total_balance
    FROM gold.customer_summary;
    """

    return execute_query(query)


# ---------------------------------------------------------
# EDUCATION SUMMARY
# ---------------------------------------------------------

def get_education_summary():

    query = """
    SELECT
        education,
        total_customers
    FROM gold.education_summary
    ORDER BY total_customers DESC;
    """

    return execute_query(query)


# ---------------------------------------------------------
# JOB SUMMARY
# ---------------------------------------------------------

def get_job_summary():

    query = """
    SELECT
        job,
        total_customers
    FROM gold.job_summary
    ORDER BY total_customers DESC;
    """

    return execute_query(query)


# ---------------------------------------------------------
# MARITAL SUMMARY
# ---------------------------------------------------------

def get_marital_summary():

    query = """
    SELECT
        marital,
        total_customers
    FROM gold.marital_summary
    ORDER BY total_customers DESC;
    """

    return execute_query(query)


# ---------------------------------------------------------
# MONTH SUMMARY
# ---------------------------------------------------------

def get_month_summary():

    query = """
    SELECT
        month,
        total_customers,
        subscribed_customers
    FROM gold.month_summary
    ORDER BY total_customers DESC;
    """

    return execute_query(query)


# ---------------------------------------------------------
# TRANSACTION SUMMARY
# ---------------------------------------------------------

def get_transaction_summary():

    query = """
    SELECT *
    FROM gold.transaction_summary;
    """

    return execute_query(query)


# ---------------------------------------------------------
# DATA AGENT
# ---------------------------------------------------------

def data_agent(question):

    question = question.lower().strip()

    # Customer / balance questions
    if (
        "average balance" in question
        or "total balance" in question
        or "average age" in question
        or "total customers" in question
        or "customer summary" in question
        or "customer statistics" in question
    ):
        return get_customer_summary()

    # Education questions
    if (
        "education" in question
        or "educational" in question
    ):
        return get_education_summary()

    # Job questions
    if (
        "job" in question
        or "occupation" in question
        or "profession" in question
    ):
        return get_job_summary()

    # Marital questions
    if (
        "marital" in question
        or "married" in question
        or "single" in question
    ):
        return get_marital_summary()

    # Month questions
    if (
        "month" in question
        or "monthly" in question
    ):
        return get_month_summary()

    # Transaction questions
    if (
        "transaction" in question
        or "transactions" in question
    ):
        return get_transaction_summary()

    return {
        "success": False,
        "error": "I could not identify the required banking data."
    }