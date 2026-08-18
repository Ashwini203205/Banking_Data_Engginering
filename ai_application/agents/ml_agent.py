"""
ML Agent — Trains a subscription prediction model and returns real data science insights.
Uses RandomForest from scikit-learn on silver.customer_clean data.
Caches trained model for high performance and formats all metrics in Indian Rupees (₹).
"""

import pandas as pd
import google.generativeai as genai

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
)

from db import run_query, test_connection
from config import get_gemini_api_key, GEMINI_MODEL
from utils import format_rupee, format_number


# Global cache for trained pipeline & metrics
_CACHED_MODEL_RESULT = None

CATEGORICAL_COLS = ["job", "marital", "education", "housing", "loan", "poutcome"]
NUMERICAL_COLS = ["age", "balance", "duration", "campaign", "pdays", "previous"]
TARGET_COL = "y"


def load_ml_data() -> pd.DataFrame:
    """Load real clean customer data from silver.customer_clean."""
    if not test_connection():
        return pd.DataFrame()
    sql = """
    SELECT age, job, marital, education, balance,
           housing, loan, duration, campaign,
           pdays, previous, poutcome, y
    FROM silver.customer_clean;
    """
    return run_query(sql)


def train_subscription_model(force_retrain: bool = False) -> dict:
    """
    Train a RandomForest model to predict term-deposit subscription.
    Returns model pipeline, metrics, confusion matrix, and feature importances.
    """
    global _CACHED_MODEL_RESULT

    if _CACHED_MODEL_RESULT is not None and not force_retrain:
        return _CACHED_MODEL_RESULT

    if not test_connection():
        return {
            "success": False,
            "error": "Unable to connect to the banking database. Please check PostgreSQL connection.",
        }

    df = load_ml_data()
    if df.empty:
        return {
            "success": False,
            "error": "No data found in silver.customer_clean. Please verify the data pipeline has loaded records.",
        }

    # Prepare target
    df = df.dropna(subset=[TARGET_COL])
    df["target"] = df[TARGET_COL].map({"yes": 1, "no": 0})
    df = df.dropna(subset=["target"])

    X = df.drop(columns=[TARGET_COL, "target"])
    y = df["target"].astype(int)

    if len(y.unique()) < 2:
        return {"success": False, "error": "Target variable has only one class in the dataset."}

    # Preprocessing pipelines
    num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("num", num_pipe, NUMERICAL_COLS),
        ("cat", cat_pipe, CATEGORICAL_COLS),
    ])

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    pipeline = Pipeline([("preprocessing", preprocessor), ("model", model)])

    # Split & train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    # Performance Evaluation Metrics
    acc = float(accuracy_score(y_test, preds))
    prec = float(precision_score(y_test, preds, zero_division=0))
    rec = float(recall_score(y_test, preds, zero_division=0))
    f1 = float(f1_score(y_test, preds, zero_division=0))
    cm = confusion_matrix(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)

    # Feature importances
    rf_model = pipeline.named_steps["model"]
    ohe = pipeline.named_steps["preprocessing"].named_transformers_["cat"].named_steps["encoder"]
    cat_feature_names = list(ohe.get_feature_names_out(CATEGORICAL_COLS))
    all_feature_names = NUMERICAL_COLS + cat_feature_names
    importances = rf_model.feature_importances_

    feat_imp_df = pd.DataFrame({
        "Feature": all_feature_names,
        "Importance": importances,
    }).sort_values("Importance", ascending=False).head(15)

    result = {
        "success": True,
        "pipeline": pipeline,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importance": feat_imp_df,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "total_samples": len(df),
        "class_distribution": dict(y.value_counts()),
    }

    _CACHED_MODEL_RESULT = result
    return result


def predict_single_customer(pipeline, customer_data: dict) -> dict:
    """Predict subscription probability for a single customer record."""
    try:
        df = pd.DataFrame([customer_data])
        prediction = pipeline.predict(df)[0]
        proba = pipeline.predict_proba(df)[0]
        return {
            "success": True,
            "prediction": int(prediction),
            "label": "Will Subscribe ✅" if prediction == 1 else "Will Not Subscribe ❌",
            "probability_yes": float(proba[1]),
            "probability_no": float(proba[0]),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def explain_ml_results(metrics: dict, question: str = "") -> str:
    """Generate a natural-language explanation of ML results (Gemini or deterministic)."""
    top_features = ", ".join([f"**{row['Feature']}** ({row['Importance']:.1%})" for _, row in metrics['feature_importance'].head(4).iterrows()])
    
    # Try Gemini explanation if available
    key = get_gemini_api_key()
    if key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = (
                "You are an expert Banking Data Scientist explaining ML classification results.\n\n"
                f"Model: Random Forest Classifier trained on real banking customer dataset.\n"
                f"Total Records: {metrics.get('total_samples', 45211):,}\n"
                f"Accuracy: {metrics['accuracy']:.2%}\n"
                f"Precision: {metrics['precision']:.2%}\n"
                f"Recall: {metrics['recall']:.2%}\n"
                f"F1 Score: {metrics['f1']:.2%}\n"
                f"Top Features: {top_features}\n"
                f"User Question: '{question}'\n\n"
                "Provide a clear, business-focused summary (3-4 sentences). "
                "Highlight what factors drive subscriptions and how this model assists bankers. "
                "Use markdown formatting with bold metrics."
            )
            response = model.generate_content(prompt)
            if response.text and len(response.text.strip()) > 10:
                return response.text.strip()
        except Exception:
            pass

    # Deterministic high-quality explanation fallback
    acc_pct = f"{metrics['accuracy']:.2%}"
    rec_pct = f"{metrics['recall']:.2%}"
    f1_pct = f"{metrics['f1']:.2%}"
    train_n = format_number(metrics.get("train_size", 0))
    test_n = format_number(metrics.get("test_size", 0))

    return (
        f"🧠 **Random Forest Model Performance:**\n\n"
        f"- **Model Accuracy:** **{acc_pct}** evaluated on **{test_n} test customers** (trained on **{train_n}** records).\n"
        f"- **Recall & F1 Score:** **{rec_pct}** Recall and **{f1_pct}** F1-Score with balanced class weighting.\n"
        f"- **Top Subscription Drivers:** {top_features}.\n"
        f"- **Business Action:** Customers with longer interaction duration and higher account balances demonstrate the highest likelihood of opening term deposits."
    )


def ml_agent(question: str) -> dict:
    """
    Handle an ML question by running the real Random Forest pipeline.
    """
    result = train_subscription_model()
    if not result["success"]:
        return result

    explanation = explain_ml_results(result, question)
    result["explanation"] = explanation
    return result