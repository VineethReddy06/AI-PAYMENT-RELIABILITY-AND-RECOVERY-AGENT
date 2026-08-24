from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

from backend.app.database import Base


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False,
        index=True
    )

    attempt_number = Column(Integer, nullable=False)

    gateway = Column(String(50), nullable=False)

    status = Column(String(30), nullable=False)

    response_time = Column(Float, nullable=False)

    failure_reason = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )