import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "service_hive_meta.json")


def retrieve_context(query: str) -> str:
    """
    Keyword-based RAG retrieval from local knowledge base.
    Returns a context string to pass to the LLM.
    """
    try:
        if not os.path.exists(FILE_PATH):
            print("[RAG] Knowledge base file not found:", FILE_PATH)
            return ""

        with open(FILE_PATH, "r") as f:
            data = json.load(f)

        pricing = data.get("pricing", {})
        basic = pricing.get("basic", {})
        pro = pricing.get("pro", {})
        policies = data.get("policies", {})

        q = (query or "").lower()

        # ── Policy queries ─────────────────────────────────────
        if any(word in q for word in ["refund", "cancel", "money back"]):
            return f"Refund policy: {policies.get('refund', 'Not available')}"

        if any(word in q for word in ["support", "help", "customer service"]):
            return f"Support policy: {policies.get('support', 'Not available')}"

        # ── Plan-specific queries ───────────────────────────────
        if "pro" in q:
            return (
                f"Pro Plan: {pro.get('price')} — "
                f"{', '.join(pro.get('features', []))}\n"
                f"Support: {policies.get('support')}"
            )

        if "basic" in q:
            return (
                f"Basic Plan: {basic.get('price')} — "
                f"{', '.join(basic.get('features', []))}"
            )

        # ── General pricing query ───────────────────────────────
        if any(word in q for word in ["price", "pricing", "cost", "plan", "how much"]):
            return (
                f"Basic Plan: {basic.get('price')} — {', '.join(basic.get('features', []))}\n"
                f"Pro Plan: {pro.get('price')} — {', '.join(pro.get('features', []))}\n"
                f"Policy: {policies.get('refund')}"
            )

        # ── General product questions ───────────────────────────
        if any(word in q for word in ["feature", "what", "tell me", "autostream", "video"]):
            return (
                f"AutoStream is a SaaS platform for automated video editing.\n"
                f"Basic Plan: {basic.get('price')} — {', '.join(basic.get('features', []))}\n"
                f"Pro Plan: {pro.get('price')} — {', '.join(pro.get('features', []))}\n"
                f"Refund policy: {policies.get('refund')}\n"
                f"Support: {policies.get('support')}"
            )

        return ""

    except Exception as e:
        print("[RAG] Error:", e)
        return ""
