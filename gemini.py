import google.generativeai as genai
from django.conf import settings

# API
genai.configure(api_key=settings.GEMINI_API_KEY)

# MODEL
model = genai.GenerativeModel("gemini-flash-latest")

#  INTENT DETECTION
def detect_intent(message):
    text = message.lower()

    #  HIGH INTENT FIRST
    if any(word in text for word in ["buy", "subscribe", "i want", "sign up"]):
        return "high_intent"

    #  PRODUCT
    if any(word in text for word in ["price", "pricing", "cost", "plan", "pro", "basic"]):
        return "product_inquiry"

    # GREETING
    if any(word in text for word in ["hi", "hello", "hey"]):
        return "greeting"

    return "product_inquiry"


#  RAG RESPONSE
def generate_rag_response(query, context):
    try:
        prompt = f"""
        You are a helpful assistant for AutoStream.

        Use the information below to answer the question clearly.

        Context:
        {context}

        Question:
        {query}

        Give a helpful and clear answer.
        """

        response = model.generate_content(prompt)

        #  SAFE HANDLING
        if not response or not response.text:
            return "Sorry, I couldn't generate a response."

        return response.text.strip()

    except Exception as e:
        print("Gemini Error:", e)
        return "Error generating response."