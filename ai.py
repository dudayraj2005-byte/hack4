from transformers import pipeline

# Load AI models
classifier = pipeline("zero-shot-classification")
sentiment = pipeline("sentiment-analysis")

# Categories (you can change to hospital if needed)
CATEGORIES = ["Billing", "Technical", "Account", "General"]

# AI severity labels
SEVERITY_LEVELS = ["Low", "Medium", "High"]

# Optional keyword boost
HIGH_PRIORITY_WORDS = [
    "urgent", "immediately", "asap",
    "not working at all", "payment failed",
    "refund not received", "error again and again"
]


def process_message(message: str):
    message_lower = message.lower()

    # 🧠 Category (AI)
    category_result = classifier(message, CATEGORIES)
    category = category_result["labels"][0]

    # 🧠 Severity (AI)
    severity_result = classifier(message, SEVERITY_LEVELS)
    severity = severity_result["labels"][0]

    # 🧠 Sentiment (AI)
    sentiment_result = sentiment(message)[0]

    # ⚡ Hybrid improvements
    if any(word in message_lower for word in HIGH_PRIORITY_WORDS):
        severity = "High"

    elif sentiment_result["label"] == "NEGATIVE" and severity == "Low":
        severity = "Medium"

    # 🎫 Escalation
    escalate = severity == "High"

    # 💬 Response
    if severity == "Low":
        response = "I can help you with that. Let me guide you."
    elif severity == "Medium":
        response = "I understand your issue. I'll assist you and escalate if needed."
    else:
        response = "This seems critical. I'm escalating this to our support team immediately."

    return {
        "response": response,
        "category": category,
        "severity": severity,
        "escalate": escalate
    }
