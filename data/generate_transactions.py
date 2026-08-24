import random
import uuid
from datetime import datetime, timedelta

from backend.app.database import SessionLocal
from backend.app.models.transaction import Transaction


PAYMENT_METHODS = ["UPI", "CARD", "NET_BANKING", "WALLET"]

BANKS = [
    "SBI",
    "HDFC",
    "ICICI",
    "AXIS",
    "KOTAK"
]

GATEWAYS = [
    "Gateway_A",
    "Gateway_B",
    "Gateway_C"
]

DEVICES = [
    "mobile",
    "desktop",
    "tablet"
]


def generate_transaction():
    amount = round(random.uniform(100, 50000), 2)

    payment_method = random.choice(PAYMENT_METHODS)
    bank = random.choice(BANKS)
    gateway = random.choice(GATEWAYS)
    device_type = random.choice(DEVICES)

    response_time = round(random.uniform(0.2, 6.0), 2)

    previous_failures = random.randint(0, 5)

    risk_score = round(random.uniform(0.0, 1.0), 2)

    # Base failure probability
    failure_probability = 0.08

    # Slow response → higher failure probability
    if response_time > 4:
        failure_probability += 0.25

    # Previous failures → higher probability
    if previous_failures >= 3:
        failure_probability += 0.20

    # High risk → higher probability
    if risk_score > 0.75:
        failure_probability += 0.20

    # High-value transactions → slightly higher probability
    if amount > 30000:
        failure_probability += 0.10

    # Decide outcome
    is_failed = random.random() < failure_probability

    if is_failed:

        status = "failed"

        if response_time > 4:
            failure_reason = "BANK_TIMEOUT"

        elif risk_score > 0.75:
            failure_reason = "RISK_BLOCK"

        elif previous_failures >= 3:
            failure_reason = "NETWORK_ERROR"

        else:
            failure_reason = random.choice([
                "GATEWAY_ERROR",
                "INSUFFICIENT_FUNDS"
            ])

    else:

        status = "success"
        failure_reason = None

    created_at = datetime.utcnow() - timedelta(
        days=random.randint(0, 90)
    )

    return Transaction(
        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
        amount=amount,
        payment_method=payment_method,
        bank=bank,
        gateway=gateway,
        response_time=response_time,
        previous_failures=previous_failures,
        device_type=device_type,
        risk_score=risk_score,
        status=status,
        failure_reason=failure_reason,
        created_at=created_at
    )


def generate_transactions(count=10000):

    db = SessionLocal()

    try:

        batch = []

        for i in range(count):

            transaction = generate_transaction()
            batch.append(transaction)

            # Insert in batches
            if len(batch) == 500:

                db.add_all(batch)
                db.commit()

                print(f"Inserted {i + 1} transactions")

                batch = []

        # Insert remaining transactions
        if batch:
            db.add_all(batch)
            db.commit()

        print(f"\nSuccessfully generated {count} transactions.")

    except Exception as e:

        db.rollback()
        print("Error:", e)

    finally:

        db.close()


if __name__ == "__main__":
    generate_transactions(10000)