import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def detect_intent(message: str) -> str:
    """
    Keyword-based intent classification.
    Returns: 'high_intent' | 'product_inquiry' | 'greeting'
    """
    text = (message or "").lower()

    # High intent — ready to convert
    if any(word in text for word in [
        "buy", "purchase", "subscribe", "get started",
        "sign up", "register", "interested", "want to try",
        "i want", "i'd like", "let's go"
    ]):
        return "high_intent"

    # Product/pricing questions
    if any(word in text for word in [
        "price", "pricing", "cost", "plan", "pro", "basic",
        "feature", "refund", "support", "how much", "what does"
    ]):
        return "product_inquiry"

    # Greeting
    if any(word in text for word in ["hi", "hello", "hey", "good morning", "good evening"]):
        return "greeting"

    # Default: treat as a product inquiry
    return "product_inquiry"


def generate_rag_response(query: str, context: str) -> str:
    """Generate a natural response using Gemini, grounded in the retrieved context."""
    try:
        prompt = f"""You are a friendly and helpful sales assistant for AutoStream, 
a SaaS platform for automated video editing.

Use ONLY the information below to answer the user's question. 
Be concise, helpful, and natural. Don't mention that you're using a knowledge base.

Knowledge Base:
{context}

User question: {query}

Answer:"""

        response = model.generate_content(prompt)

        if not response or not response.text:
            return "Sorry, I couldn't generate a response right now."

        return response.text.strip()

    except Exception as e:
        print("[Gemini Error]", e)
        return context  # Fallback: return raw context
