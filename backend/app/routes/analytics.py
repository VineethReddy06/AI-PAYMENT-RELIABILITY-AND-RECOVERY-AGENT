from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.models.payment_attempt import PaymentAttempt


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ==========================================================
# 1. OVERALL PAYMENT OVERVIEW
# ==========================================================

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):

    total = (
        db.query(func.count(Transaction.id))
        .scalar()
        or 0
    )

    successful = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.status == "success"
        )
        .scalar()
        or 0
    )

    recovered = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.status == "recovered"
        )
        .scalar()
        or 0
    )

    failed = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.status == "failed"
        )
        .scalar()
        or 0
    )

    # Direct success + recovered payments
    successful_outcomes = successful + recovered

    success_rate = (
        round(
            (successful_outcomes / total) * 100,
            2
        )
        if total
        else 0
    )

    failure_rate = (
        round(
            (failed / total) * 100,
            2
        )
        if total
        else 0
    )

    recovery_rate = (
        round(
            (recovered / (failed + recovered)) * 100,
            2
        )
        if (failed + recovered)
        else 0
    )

    return {
        "total_transactions": total,

        "successful_transactions": successful,

        "recovered_transactions": recovered,

        "failed_transactions": failed,

        "successful_outcomes": successful_outcomes,

        "success_rate_percent": success_rate,

        "failure_rate_percent": failure_rate,

        "recovery_rate_percent": recovery_rate
    }


# ==========================================================
# 2. GATEWAY PERFORMANCE
# ==========================================================

@router.get("/gateways")
def get_gateway_performance(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            Transaction.gateway,

            func.count(
                Transaction.id
            ).label("total"),

            func.sum(
                case(
                    (
                        Transaction.status.in_(
                            ["success", "recovered"]
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("successful"),

            func.sum(
                case(
                    (
                        Transaction.status == "failed",
                        1
                    ),
                    else_=0
                )
            ).label("failed")
        )
        .group_by(
            Transaction.gateway
        )
        .all()
    )

    gateways = {}

    for row in results:

        total = row.total or 0

        successful = row.successful or 0

        failed = row.failed or 0

        gateways[row.gateway] = {

            "total_transactions": total,

            "successful": successful,

            "failed": failed,

            "success_rate_percent": (
                round(
                    (successful / total) * 100,
                    2
                )
                if total
                else 0
            ),

            "failure_rate_percent": (
                round(
                    (failed / total) * 100,
                    2
                )
                if total
                else 0
            )
        }

    return gateways


# ==========================================================
# 3. FAILURE ANALYSIS
# ==========================================================

@router.get("/failures")
def get_failure_analysis(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            Transaction.failure_reason,

            func.count(
                Transaction.id
            ).label("count")
        )
        .filter(
            Transaction.failure_reason.isnot(None)
        )
        .group_by(
            Transaction.failure_reason
        )
        .order_by(
            func.count(
                Transaction.id
            ).desc()
        )
        .all()
    )

    total_failures = sum(
        row.count
        for row in results
    )

    failures = []

    for row in results:

        percentage = (
            round(
                (row.count / total_failures) * 100,
                2
            )
            if total_failures
            else 0
        )

        failures.append({

            "failure_reason":
                row.failure_reason,

            "count":
                row.count,

            "percentage":
                percentage
        })

    return {

        "total_failures":
            total_failures,

        "failure_reasons":
            failures
    }


# ==========================================================
# 4. RECOVERY ANALYSIS
# ==========================================================

@router.get("/recovery")
def get_recovery_analysis(
    db: Session = Depends(get_db)
):

    # ======================================================
    # ALL PAYMENT ATTEMPTS
    # ======================================================

    total_attempts = (
        db.query(
            func.count(PaymentAttempt.id)
        )
        .scalar()
        or 0
    )

    failed_attempts = (
        db.query(
            func.count(PaymentAttempt.id)
        )
        .filter(
            PaymentAttempt.status == "failed"
        )
        .scalar()
        or 0
    )

    successful_attempts = (
        db.query(
            func.count(PaymentAttempt.id)
        )
        .filter(
            PaymentAttempt.status == "success"
        )
        .scalar()
        or 0
    )

    # ======================================================
    # TRANSACTIONS THAT ACTUALLY HAD PAYMENT ATTEMPTS
    # ======================================================

    attempted_transaction_ids = (
        db.query(
            PaymentAttempt.transaction_id
        )
        .distinct()
        .subquery()
    )

    # ======================================================
    # RECOVERED TRANSACTIONS AMONG TESTED PAYMENTS
    # ======================================================

    recovered_transactions = (
        db.query(
            func.count(Transaction.id)
        )
        .filter(
            Transaction.id.in_(
                db.query(
                    attempted_transaction_ids.c.transaction_id
                )
            ),
            Transaction.status == "recovered"
        )
        .scalar()
        or 0
    )

    # ======================================================
    # FAILED TRANSACTIONS AMONG TESTED PAYMENTS
    # ======================================================

    failed_transactions = (
        db.query(
            func.count(Transaction.id)
        )
        .filter(
            Transaction.id.in_(
                db.query(
                    attempted_transaction_ids.c.transaction_id
                )
            ),
            Transaction.status == "failed"
        )
        .scalar()
        or 0
    )

    # ======================================================
    # RECOVERY CANDIDATES
    # ======================================================

    recovery_candidates = (
        recovered_transactions +
        failed_transactions
    )

    recovery_success_rate = (
        round(
            (
                recovered_transactions /
                recovery_candidates
            ) * 100,
            2
        )
        if recovery_candidates
        else 0
    )

    # ======================================================
    # AVERAGE ATTEMPTS FOR RECOVERED TRANSACTIONS
    # ======================================================

    recovered_transaction_ids = (
        db.query(
            Transaction.id
        )
        .filter(
            Transaction.id.in_(
                db.query(
                    attempted_transaction_ids.c.transaction_id
                )
            ),
            Transaction.status == "recovered"
        )
        .subquery()
    )

    attempts_for_recovered = (
        db.query(
            func.count(PaymentAttempt.id)
        )
        .filter(
            PaymentAttempt.transaction_id.in_(
                db.query(
                    recovered_transaction_ids.c.id
                )
            )
        )
        .scalar()
        or 0
    )

    average_attempts = (
        round(
            attempts_for_recovered /
            recovered_transactions,
            2
        )
        if recovered_transactions
        else 0
    )

    return {

        "total_attempts":
            total_attempts,

        "failed_attempts":
            failed_attempts,

        "successful_attempts":
            successful_attempts,

        "recovered_transactions":
            recovered_transactions,

        "failed_transactions":
            failed_transactions,

        "recovery_success_rate_percent":
            recovery_success_rate,

        "average_attempts_per_recovery":
            average_attempts
    }
    
# ==========================================================
# 5. TRANSACTION HISTORY
# ==========================================================

@router.get("/transactions")
def get_transaction_history(
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.id.desc())
        .limit(50)
        .all()
    )

    history = []

    for transaction in transactions:

        history.append({
            "transaction_id": str(transaction.id),

            "amount": getattr(
                transaction,
                "amount",
                None
            ),

            "payment_method": getattr(
                transaction,
                "payment_method",
                None
            ),

            "bank": getattr(
                transaction,
                "bank",
                None
            ),

            "gateway": getattr(
                transaction,
                "gateway",
                None
            ),

            "status": getattr(
                transaction,
                "status",
                None
            ),

            "failure_reason": getattr(
                transaction,
                "failure_reason",
                None
            )
        })

    return {
        "total": len(history),
        "transactions": history
    }