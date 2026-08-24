import random
import time


class PaymentProcessor:

    def process_payment(self, gateway: str) -> dict:
        """
        Simulates a payment attempt through a gateway.
        """

        # Simulate gateway response time
        response_time = round(random.uniform(0.5, 5.5), 2)

        # Simulate gateway success probability
        gateway_success_rates = {
            "Gateway_A": 0.65,
            "Gateway_B": 0.80,
            "Gateway_C": 0.85
        }

        success_probability = gateway_success_rates.get(
            gateway,
            0.70
        )

        success = random.random() < success_probability

        if success:
            return {
                "status": "success",
                "gateway": gateway,
                "response_time": response_time,
                "failure_reason": None
            }

        # Simulated failure reasons
        failure_reasons = [
            "BANK_TIMEOUT",
            "NETWORK_ERROR",
            "GATEWAY_ERROR"
        ]

        return {
            "status": "failed",
            "gateway": gateway,
            "response_time": response_time,
            "failure_reason": random.choice(failure_reasons)
        }