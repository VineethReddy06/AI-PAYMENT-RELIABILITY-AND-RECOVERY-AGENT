import pandas as pd
from sqlalchemy import text

from backend.app.database import engine


def load_data():
    query = text("""
        SELECT
            transaction_id,
            amount,
            payment_method,
            bank,
            gateway,
            response_time,
            previous_failures,
            device_type,
            risk_score,
            status,
            failure_reason,
            created_at
        FROM transactions
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df

def analyze_data(df):

    print("\n" + "=" * 60)
    print("PAYMENT TRANSACTION DATASET")
    print("=" * 60)

    print(f"\nTotal transactions: {len(df)}")

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 transactions:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\n" + "=" * 60)
    print("PAYMENT STATUS")
    print("=" * 60)

    status_counts = df["status"].value_counts()

    print(status_counts)

    print("\nStatus percentage:")

    status_percentage = (
        df["status"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print(status_percentage)

    print("\n" + "=" * 60)
    print("FAILURE REASONS")
    print("=" * 60)

    failure_counts = (
        df[df["status"] == "failed"]["failure_reason"]
        .value_counts()
    )

    print(failure_counts)

    print("\n" + "=" * 60)
    print("FAILURE RATE BY PAYMENT METHOD")
    print("=" * 60)

    payment_method_analysis = (
        pd.crosstab(
            df["payment_method"],
            df["status"],
            normalize="index"
        )
        .mul(100)
        .round(2)
    )

    print(payment_method_analysis)

    print("\n" + "=" * 60)
    print("FAILURE RATE BY BANK")
    print("=" * 60)

    bank_analysis = (
        pd.crosstab(
            df["bank"],
            df["status"],
            normalize="index"
        )
        .mul(100)
        .round(2)
    )

    print(bank_analysis)

    print("\n" + "=" * 60)
    print("FAILURE RATE BY GATEWAY")
    print("=" * 60)

    gateway_analysis = (
        pd.crosstab(
            df["gateway"],
            df["status"],
            normalize="index"
        )
        .mul(100)
        .round(2)
    )

    print(gateway_analysis)

    print("\n" + "=" * 60)
    print("AVERAGE RESPONSE TIME")
    print("=" * 60)

    response_analysis = (
        df.groupby("status")["response_time"]
        .agg(["mean", "median", "min", "max"])
        .round(2)
    )

    print(response_analysis)

    print("\n" + "=" * 60)
    print("AVERAGE RISK SCORE")
    print("=" * 60)

    risk_analysis = (
        df.groupby("status")["risk_score"]
        .agg(["mean", "median", "min", "max"])
        .round(3)
    )

    print(risk_analysis)

    print("\n" + "=" * 60)
    print("PREVIOUS FAILURES")
    print("=" * 60)

    previous_failure_analysis = (
        df.groupby("status")["previous_failures"]
        .agg(["mean", "median", "min", "max"])
        .round(2)
    )

    print(previous_failure_analysis)


if __name__ == "__main__":

    print("Loading transactions from PostgreSQL...")

    df = load_data()

    analyze_data(df)