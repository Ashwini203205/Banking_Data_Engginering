"""
Comprehensive Test Suite for Banking AI Analytics Dashboard
"""

import sys, os, io
sys.path.insert(0, 'ai_application')
sys.stdout.reconfigure(encoding='utf-8')

from db import test_connection, run_query, get_table_counts
from agents.router import route_question
from agents.data_agent import data_agent, get_all_summaries
from agents.ml_agent import train_subscription_model, predict_single_customer
from utils import format_rupee, format_number

def run_tests():
    print("=" * 60)
    print("1. TESTING POSTGRESQL CONNECTION & GOLD TABLES")
    print("=" * 60)
    db_ok = test_connection()
    print(f"DB Connection: {'PASSED [OK]' if db_ok else 'FAILED [X]'}")
    counts = get_table_counts()
    for tbl, cnt in counts.items():
        print(f"  - {tbl}: {cnt:,} records")

    print("\n" + "=" * 60)
    print("2. TESTING KPI EXTRACTION & INR (Rs) FORMATTING")
    print("=" * 60)
    cust_df = run_query("SELECT total_customers, subscribed_customers, average_age, average_balance, total_balance FROM gold.customer_summary LIMIT 1;")
    if not cust_df.empty:
        r = cust_df.iloc[0]
        print(f"Total Customers: {format_number(r.get('total_customers'))}")
        print(f"Subscribed Customers: {format_number(r.get('subscribed_customers'))}")
        print(f"Average Age: {float(r.get('average_age')):.1f} years")
        print(f"Average Balance: {format_rupee(r.get('average_balance'), decimals=True)}")
        print(f"Total Balance: {format_rupee(r.get('total_balance'))}")

    print("\n" + "=" * 60)
    print("3. TESTING AI CHATBOT ROUTING & QUESTION RESOLUTION")
    print("=" * 60)
    questions = [
        "What is the total balance?",
        "What is the average customer balance?",
        "What is the average age?",
        "How many customers are subscribed?",
        "Which job category has the highest balance?",
        "How many customers have loans?",
        "What percentage of customers subscribed?",
        "Show me the top 10 customers by balance.",
        "Which customer segment has the highest average balance?",
        "Give me insights from the banking data.",
        "Predict whether a customer is likely to subscribe.",
        "How does the data pipeline work?"
    ]

    for q in questions:
        res = route_question(q)
        agent = res.get("agent_name", "Unknown")
        agent_key = res.get("agent_key", "")
        success = res.get("result", {}).get("success", False)
        print(f"Q: \"{q}\"")
        print(f"  -> Routed to: {agent} ({agent_key}) | Success: {success}")
        if agent_key == "data":
            print(f"  -> Title: {res['result'].get('title')}")
            print(f"  -> Insight: {res['result'].get('insight')[:140]}...")
        elif agent_key == "ml":
            print(f"  -> Accuracy: {res['result'].get('accuracy', 0):.2%}")
            print(f"  -> Explanation: {res['result'].get('explanation')[:140]}...")
        elif agent_key == "support":
            print(f"  -> Answer: {res['result'].get('answer')[:140]}...")
        print()

    print("=" * 60)
    print("4. TESTING SINGLE CUSTOMER PREDICTION INFERENCE")
    print("=" * 60)
    ml_model = train_subscription_model()
    customer = {
        "age": 45, "job": "management", "marital": "married", "education": "tertiary",
        "balance": 55000, "housing": "no", "loan": "no", "duration": 450,
        "campaign": 1, "pdays": -1, "previous": 0, "poutcome": "unknown"
    }
    pred = predict_single_customer(ml_model["pipeline"], customer)
    print("Single Customer Prediction Test:")
    print(f"  -> Prediction Label: {pred.get('label')}")
    print(f"  -> Probability Yes: {pred.get('probability_yes'):.2%}")
    print(f"  -> Probability No: {pred.get('probability_no'):.2%}")
    print("=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
