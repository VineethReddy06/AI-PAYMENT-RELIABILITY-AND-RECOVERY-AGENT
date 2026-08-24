from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime

from backend.app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(String(30), nullable=False)

    bank = Column(String(50), nullable=False)

    gateway = Column(String(50), nullable=False)

    response_time = Column(Float, nullable=False)

    previous_failures = Column(Integer, default=0)

    device_type = Column(String(30), nullable=False)

    risk_score = Column(Float, nullable=False)

    status = Column(String(30), nullable=False)

    failure_reason = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )