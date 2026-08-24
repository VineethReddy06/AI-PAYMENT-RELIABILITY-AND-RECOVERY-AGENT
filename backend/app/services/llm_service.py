import requests


class PaymentLLM:

    def __init__(self):

        self.url = "http://localhost:1234/v1/chat/completions"

        self.model = "meta-llama_-_llama-3.2-3b-instruct"

    def explain_recovery(
        self,
        transaction,
        recovery,
        retrieved_policies
    ):

        policy_text = "\n\n".join(
            policy["document"]
            for policy in retrieved_policies
        )

        prompt = f"""
Explain the payment failure and the recovery decision accurately.

IMPORTANT:
- The Recovery Agent's actual decision is authoritative.
- Do NOT change, reinterpret, or invent the recovery action.
- Do NOT mention STOP_RETRY unless the actual recovery action is STOP_RETRY.
- Do NOT recommend a different gateway from the one provided.
- If the recommended gateway is None, do not invent a gateway.
- Explain the retrieved policy only as supporting context.
- Keep the explanation concise.

Payment failure:
{transaction.get("failure_reason")}

Current gateway:
{transaction.get("gateway")}

Previous failures:
{transaction.get("previous_failures")}

Risk score:
{transaction.get("risk_score")}

ACTUAL RECOVERY ACTION:
{recovery.get("action")}

ACTUAL RECOVERY DECISION:
{recovery.get("decision")}

ACTUAL RECOMMENDED GATEWAY:
{recovery.get("recommended_gateway")}

ACTUAL RECOVERY REASON:
{recovery.get("reason")}

Retrieved payment recovery policies:
{policy_text}

Explain only:
1. Why the payment failed.
2. What the Recovery Agent actually decided.
3. Why that decision was made.
4. What happened during recovery.

Use ONLY the information provided above.
"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You explain payment failures and recovery decisions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 220
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]