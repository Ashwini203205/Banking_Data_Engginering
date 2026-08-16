import psycopg2
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "banking_db",
    "user": "admin",
    "password": "password123"
}


def load_data():

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

    connection = psycopg2.connect(**DB_CONFIG)

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


def train_model():

    df = load_data()

    # Remove rows where target is missing
    df = df.dropna(subset=["y"])

    # Convert target
    df["target"] = df["y"].map({
        "yes": 1,
        "no": 0
    })

    # Remove original target column
    X = df.drop(columns=["y", "target"])
    y = df["target"]

    # Identify categorical and numerical columns
    categorical_columns = [
        "job",
        "marital",
        "education",
        "housing",
        "loan",
        "poutcome"
    ]

    numerical_columns = [
        "age",
        "balance",
        "duration",
        "campaign",
        "pdays",
        "previous"
    ]

    # Numerical preprocessing
    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            )
        ]
    )

    # Categorical preprocessing
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    # Combine preprocessing
    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                numerical_columns
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_columns
            )
        ]
    )

    # Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

    # Complete ML pipeline
    pipeline = Pipeline(
        steps=[
            (
                "preprocessing",
                preprocessing
            ),
            (
                "model",
                model
            )
        ]
    )

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Train
    pipeline.fit(X_train, y_train)

    # Predict
    predictions = pipeline.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    return pipeline, accuracy


if __name__ == "__main__":

    print("Starting ML model training...")

    model, accuracy = train_model()

    print("ML model training completed.")

    print(
        f"Model Accuracy: {accuracy:.4f}"
    )