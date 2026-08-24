from typing import Dict, Any
from backend.app.services.payment_processor import PaymentProcessor
from backend.app.models.payment_attempt import PaymentAttempt


class RecoveryAgent:

    def analyze(self, transaction: Dict[str, Any]) -> Dict[str, Any]:

        status = transaction.get("status")
        failure_reason = transaction.get("failure_reason")
        gateway = transaction.get("gateway")
        previous_failures = transaction.get("previous_failures", 0)
        risk_score = transaction.get("risk_score", 0)

        # Successful payment
        if status == "success":
            return {
                "action": "NO_ACTION",
                "decision": "Payment successful",
                "recommended_gateway": gateway,
                "reason": "Transaction completed successfully"
            }

        # Risk-related failure
        if failure_reason == "RISK_BLOCK":
            return {
                "action": "MANUAL_REVIEW",
                "decision": "Do not automatically retry",
                "recommended_gateway": None,
                "reason": "Transaction was blocked by risk controls"
            }

        # Insufficient funds
        if failure_reason == "INSUFFICIENT_FUNDS":
            return {
                "action": "CUSTOMER_ACTION",
                "decision": "Ask customer to use another payment method",
                "recommended_gateway": None,
                "reason": "Insufficient funds"
            }

        # Too many previous failures
        if previous_failures >= 4:
            return {
                "action": "STOP_RETRY",
                "decision": "Stop automatic retries",
                "recommended_gateway": None,
                "reason": "Too many previous payment failures"
            }

        # Bank timeout
        if failure_reason == "BANK_TIMEOUT":
            return {
                "action": "RETRY",
                "decision": "Retry using alternate gateway",
                "recommended_gateway": self.get_alternate_gateway(gateway),
                "reason": "Bank timeout detected"
            }

        # Network error
        if failure_reason == "NETWORK_ERROR":
            return {
                "action": "RETRY",
                "decision": "Retry payment",
                "recommended_gateway": self.get_alternate_gateway(gateway),
                "reason": "Network error detected"
            }

        # Gateway error
        if failure_reason == "GATEWAY_ERROR":
            return {
                "action": "RETRY",
                "decision": "Switch gateway and retry",
                "recommended_gateway": self.get_alternate_gateway(gateway),
                "reason": "Gateway error detected"
            }

        # High risk transaction
        if risk_score >= 0.85:
            return {
                "action": "MANUAL_REVIEW",
                "decision": "Send transaction for risk review",
                "recommended_gateway": None,
                "reason": "High risk score"
            }

        # Default recovery
        return {
            "action": "RETRY",
            "decision": "Retry using alternate gateway",
            "recommended_gateway": self.get_alternate_gateway(gateway),
            "reason": "Recoverable payment failure"
        }

    @staticmethod
    def get_alternate_gateway(current_gateway: str) -> str:

        gateways = [
            "Gateway_A",
            "Gateway_B",
            "Gateway_C"
        ]

        available_gateways = [
            gateway for gateway in gateways
            if gateway != current_gateway
        ]

        return available_gateways[0] if available_gateways else current_gateway


    # 👇 ADD THE NEW METHOD HERE
    def recover_payment(self, transaction, initial_result):

        processor = PaymentProcessor()

        attempts = []

        current_gateway = transaction["gateway"]

        # --------------------------------------------------
        # 1. RECORD INITIAL PAYMENT ATTEMPT
        # --------------------------------------------------

        attempts.append({
            "status": initial_result["status"],
            "gateway": current_gateway,
            "response_time": initial_result["response_time"],
            "failure_reason": initial_result.get("failure_reason")
        })

        # If initial payment succeeded
        if initial_result["status"] == "success":
            return {
                "status": "recovered",
                "attempts": attempts,
                "final_gateway": current_gateway
            }

        # --------------------------------------------------
        # 2. ASK RECOVERY AGENT WHAT TO DO
        # --------------------------------------------------

        recovery = self.analyze({
            "status": "failed",
            "failure_reason": initial_result.get("failure_reason"),
            "gateway": current_gateway,
            "previous_failures": transaction.get("previous_failures", 0),
            "risk_score": transaction.get("risk_score", 0)
        })

        # Don't retry if recovery says not to
        if recovery["action"] != "RETRY":
            return {
                "status": "not_recovered",
                "attempts": attempts,
                "final_gateway": current_gateway,
                "recovery": recovery
            }

        # --------------------------------------------------
        # 3. FIRST RETRY - ALTERNATE GATEWAY
        # --------------------------------------------------

        alternate_gateway = recovery["recommended_gateway"]

        retry_result = processor.process_payment(
            alternate_gateway
        )

        attempts.append({
            "status": retry_result["status"],
            "gateway": alternate_gateway,
            "response_time": retry_result["response_time"],
            "failure_reason": retry_result.get("failure_reason")
        })

        if retry_result["status"] == "success":
            return {
                "status": "recovered",
                "attempts": attempts,
                "final_gateway": alternate_gateway,
                "recovery": recovery
            }

        # --------------------------------------------------
        # 4. SECOND RETRY
        # --------------------------------------------------

        second_gateway = self.get_alternate_gateway(
            alternate_gateway
        )

        second_retry = processor.process_payment(
            second_gateway
        )

        attempts.append({
            "status": second_retry["status"],
            "gateway": second_gateway,
            "response_time": second_retry["response_time"],
            "failure_reason": second_retry.get("failure_reason")
        })

        if second_retry["status"] == "success":
            return {
                "status": "recovered",
                "attempts": attempts,
                "final_gateway": second_gateway,
                "recovery": recovery
            }

        # --------------------------------------------------
        # 5. ALL ATTEMPTS FAILED
        # --------------------------------------------------

        return {
            "status": "failed",
            "attempts": attempts,
            "final_gateway": second_gateway,
            "recovery": recovery
        }