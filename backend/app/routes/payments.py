import random
import uuid
from pathlib import Path

import joblib
import pandas as pd

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.schema import PaymentCreate
from backend.app.services.recovery_agent import RecoveryAgent
from backend.app.services.payment_processor import PaymentProcessor
from backend.app.models.payment_attempt import PaymentAttempt
from backend.app.services.rag_service import PaymentRAG
from backend.app.services.llm_service import PaymentLLM


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# ==========================================================
# LOAD ML MODEL
# ==========================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "ml"
    / "failure_model.joblib"
)

failure_model = joblib.load(MODEL_PATH)


# ==========================================================
# SERVICES
# ==========================================================

recovery_agent = RecoveryAgent()
payment_processor = PaymentProcessor()

rag = PaymentRAG()
llm = PaymentLLM()


# ==========================================================
# CREATE PAYMENT
# ==========================================================

@router.post("/")
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):

    transaction_id = (
        f"TXN-{uuid.uuid4().hex[:8].upper()}"
    )


    # ======================================================
    # 1. SIMULATED PAYMENT ENVIRONMENT
    # ======================================================

    response_time = round(
        random.uniform(0.3, 6.0),
        2
    )

    previous_failures = random.randint(
        0,
        4
    )

    device_type = random.choice([
        "mobile",
        "desktop",
        "tablet"
    ])

    risk_score = round(
        random.uniform(0.0, 1.0),
        2
    )


    # ======================================================
    # 2. ML FAILURE PREDICTION
    # ======================================================

    model_input = pd.DataFrame([{
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "bank": payment.bank,
        "gateway": payment.gateway,
        "response_time": response_time,
        "previous_failures": previous_failures,
        "device_type": device_type,
        "risk_score": risk_score
    }])

    failure_probability = float(
        failure_model.predict_proba(
            model_input
        )[0][1]
    )


    # ======================================================
    # 3. INITIAL PAYMENT ATTEMPT
    # ======================================================

    initial_result = (
        payment_processor.process_payment(
            payment.gateway
        )
    )

    status = initial_result["status"]

    failure_reason = (
        initial_result["failure_reason"]
    )


    # ======================================================
    # 4. RECOVERY AGENT
    # ======================================================

    transaction_context = {

        "gateway": payment.gateway,

        "previous_failures":
            previous_failures,

        "risk_score":
            risk_score
    }

    recovery_result = (
        recovery_agent.recover_payment(
            transaction_context,
            initial_result
        )
    )


    # ======================================================
    # 4.1 RAG + LLM
    # ======================================================

    ai_explanation = None

    retrieved_policies = []


    if initial_result["status"] == "failed":

        # --------------------------------------------------
        # RAG QUERY
        # --------------------------------------------------

        rag_query = f"""
        Payment failed.

        Failure reason:
        {initial_result.get("failure_reason")}

        Gateway:
        {payment.gateway}

        Risk score:
        {risk_score}

        Previous failures:
        {previous_failures}

        What payment recovery policy should be applied?
        """


        # --------------------------------------------------
        # RETRIEVE POLICIES
        # --------------------------------------------------

        retrieved_policies = rag.retrieve(
            rag_query,
            k=3
        )


        # --------------------------------------------------
        # RECOVERY DECISION
        # --------------------------------------------------

        recovery_decision = (
            recovery_result.get(
                "recovery",
                {}
            )
        )


        # --------------------------------------------------
        # TRANSACTION DATA FOR LLM
        # --------------------------------------------------

        transaction_for_llm = {

            "amount":
                payment.amount,

            "payment_method":
                payment.payment_method,

            "bank":
                payment.bank,

            "gateway":
                payment.gateway,

            "risk_score":
                risk_score,

            "previous_failures":
                previous_failures,

            "status":
                initial_result["status"],

            "failure_reason":
                initial_result.get(
                    "failure_reason"
                )
        }


        # --------------------------------------------------
        # LLM EXPLANATION
        # --------------------------------------------------

        ai_explanation = (
            llm.explain_recovery(
                transaction_for_llm,
                recovery_decision,
                retrieved_policies
            )
        )


    # ======================================================
    # 5. SAVE TRANSACTION
    # ======================================================

    transaction = Transaction(

        transaction_id=
            transaction_id,

        amount=
            payment.amount,

        payment_method=
            payment.payment_method,

        bank=
            payment.bank,

        gateway=
            payment.gateway,

        response_time=
            response_time,

        previous_failures=
            previous_failures,

        device_type=
            device_type,

        risk_score=
            risk_score,

        status=
            recovery_result["status"],

        failure_reason=
            failure_reason
    )

    db.add(transaction)

    db.commit()

    db.refresh(transaction)


    # ======================================================
    # 5.1 SAVE PAYMENT ATTEMPTS
    # ======================================================

    attempts = (
        recovery_result.get(
            "attempts",
            []
        )
    )


    for index, attempt in enumerate(
        attempts,
        start=1
    ):

        payment_attempt = PaymentAttempt(

            transaction_id=
                transaction.id,

            attempt_number=
                index,

            gateway=
                attempt["gateway"],

            status=
                attempt["status"],

            response_time=
                attempt["response_time"],

            failure_reason=
                attempt.get(
                    "failure_reason"
                )
        )

        db.add(payment_attempt)


    db.commit()


    # ======================================================
    # 6. RAG POLICY RESPONSE
    # ======================================================

    rag_policy_evidence = []


    for policy in retrieved_policies:

        rag_policy_evidence.append({

            "score":
                round(
                    policy.get(
                        "score",
                        0
                    ),
                    4
                ),

            "document":
                policy.get(
                    "document",
                    ""
                ),

            "source":
                "payment_recovery_policies.txt"
        })


    # ======================================================
    # 7. RETURN COMPLETE PAYMENT INTELLIGENCE
    # ======================================================

    return {

        # --------------------------------------------------
        # TRANSACTION
        # --------------------------------------------------

        "transaction_id":
            transaction.transaction_id,


        # --------------------------------------------------
        # PAYMENT
        # --------------------------------------------------

        "payment": {

            "amount":
                transaction.amount,

            "payment_method":
                transaction.payment_method,

            "bank":
                transaction.bank,

            "initial_gateway":
                payment.gateway
        },


        # --------------------------------------------------
        # RISK ANALYSIS
        # --------------------------------------------------

        "risk_analysis": {

            "response_time":
                response_time,

            "previous_failures":
                previous_failures,

            "device_type":
                device_type,

            "risk_score":
                risk_score
        },


        # --------------------------------------------------
        # ML PREDICTION
        # --------------------------------------------------

        "ml_prediction": {

            "failure_probability":
                round(
                    failure_probability,
                    4
                ),

            "failure_probability_percent":
                round(
                    failure_probability * 100,
                    2
                )
        },


        # --------------------------------------------------
        # INITIAL PAYMENT
        # --------------------------------------------------

        "initial_payment":
            initial_result,


        # --------------------------------------------------
        # RECOVERY
        # --------------------------------------------------

        "recovery":
            recovery_result,


        # --------------------------------------------------
        # RAG POLICY EVIDENCE
        # --------------------------------------------------

        "rag_policy": {

            "query":
                rag_query.strip()
                if initial_result["status"] == "failed"
                else None,

            "documents_retrieved":
                len(rag_policy_evidence),

            "policies":
                rag_policy_evidence
        },


        # --------------------------------------------------
        # LLM EXPLANATION
        # --------------------------------------------------

        "ai_explanation":
            ai_explanation
    }