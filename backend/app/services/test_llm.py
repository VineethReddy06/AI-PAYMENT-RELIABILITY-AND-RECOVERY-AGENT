from backend.app.services.llm_service import PaymentLLM


llm = PaymentLLM()


transaction = {
    "amount": 5000,
    "payment_method": "UPI",
    "bank": "SBI",
    "gateway": "Gateway_A",
    "risk_score": 0.28,
    "previous_failures": 1,
    "status": "failed",
    "failure_reason": "BANK_TIMEOUT"
}


recovery = {
    "action": "RETRY",
    "decision": "Retry using alternate gateway",
    "recommended_gateway": "Gateway_B",
    "reason": "Bank timeout detected"
}


policies = [
    {
        "document": """
BANK_TIMEOUT

Bank timeout occurs when the payment bank does not respond
within the expected time window.

Recommended action:
Retry the payment using an alternate payment gateway.

Reason:
The failure may be specific to the current gateway or bank connection.
"""
    }
]


llm = PaymentLLM()

explanation = llm.explain_recovery(
    transaction,
    recovery,
    policies
)


print("\n" + "=" * 60)
print("AI RECOVERY EXPLANATION")
print("=" * 60)
print(explanation)