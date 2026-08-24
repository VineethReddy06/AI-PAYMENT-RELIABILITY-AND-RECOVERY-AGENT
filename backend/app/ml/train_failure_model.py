import pandas as pd

from sqlalchemy import text
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    roc_auc_score
)
from xgboost import XGBClassifier
import joblib

print("\nModel saved successfully!")

from backend.app.database import engine


# --------------------------------------------------
# 1. Load data
# --------------------------------------------------

def load_data():

    query = text("""
        SELECT
            amount,
            payment_method,
            bank,
            gateway,
            response_time,
            previous_failures,
            device_type,
            risk_score,
            status
        FROM transactions
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


# --------------------------------------------------
# 2. Prepare data
# --------------------------------------------------

def prepare_data(df):

    # Convert target into binary
    # success = 0
    # failed  = 1

    df["target"] = (
        df["status"]
        .map({
            "success": 0,
            "failed": 1
        })
    )

    X = df.drop(
        columns=["status", "target"]
    )

    y = df["target"]

    return X, y


# --------------------------------------------------
# 3. Build model
# --------------------------------------------------

def build_model():

    categorical_features = [
        "payment_method",
        "bank",
        "gateway",
        "device_type"
    ]

    numerical_features = [
        "amount",
        "response_time",
        "previous_failures",
        "risk_score"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            )
        ],
        remainder="passthrough"
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    return pipeline


# --------------------------------------------------
# 4. Train and evaluate
# --------------------------------------------------

def train_model():

    print("\nLoading data...")

    df = load_data()

    print(
        f"Loaded {len(df)} transactions."
    )

    X, y = prepare_data(df)

    print("\nTarget distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(
        f"\nTraining samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    pipeline = build_model()

    print("\nTraining XGBoost model...")

    pipeline.fit(
        X_train,
        y_train
    )

    joblib.dump(
        pipeline,
        "backend/app/ml/failure_model.joblib"
    )

    print("\nModel saved successfully!")

    # Predictions
    y_pred = pipeline.predict(X_test)

    y_probability = pipeline.predict_proba(
        X_test
    )[:, 1]

    # Evaluation
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(
        f"\nAccuracy: "
        f"{accuracy_score(y_test, y_pred):.4f}"
    )

    print(
        f"ROC-AUC: "
        f"{roc_auc_score(y_test, y_probability):.4f}"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Success",
                "Failed"
            ]
        )
    )

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    return pipeline


if __name__ == "__main__":

    train_model()