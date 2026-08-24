from backend.app.services.recovery_agent import RecoveryAgent


agent = RecoveryAgent()


transaction = {
    "amount": 5000,
    "payment_method": "UPI",
    "bank": "SBI",
    "gateway": "Gateway_A",
    "previous_failures": 1,
    "risk_score": 0.35
}


result = agent.recover_payment(transaction)


print("\n" + "=" * 60)
print("AUTOMATIC PAYMENT RECOVERY")
print("=" * 60)

print("Final Status:", result["status"])
print("Final Gateway:", result["final_gateway"])

print("\nAttempts:")

for i, attempt in enumerate(result["attempts"], start=1):

    print(f"\nAttempt {i}")
    print("Gateway:", attempt["gateway"])
    print("Status:", attempt["status"])
    print("Response Time:", attempt["response_time"])
    print("Failure Reason:", attempt["failure_reason"])