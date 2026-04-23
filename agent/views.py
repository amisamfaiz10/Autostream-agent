import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .graph import app

# ─────────────────────────────────────────────
# Default session state template
# ─────────────────────────────────────────────

def default_state():
    return {
        "message": "",
        "intent": "",
        "response": "",
        "name": None,
        "email": None,
        "platform": None,
        "step": None
    }


@csrf_exempt
def chat_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"response": "Please type a message."})

        # Load session state (persists across turns)
        state = request.session.get("agent_state", default_state())

        # Inject the new user message
        state["message"] = message

        # Run the LangGraph agent
        try:
            result = app.invoke(state)
            response = result.get("response", "Sorry, I didn't understand that.")
        except Exception as e:
            print("[GRAPH ERROR]", e)
            result = state
            response = "Something went wrong. Please try again."

        # Persist updated state back to session
        request.session["agent_state"] = result
        request.session.modified = True

        return JsonResponse({"response": response})

    except Exception as e:
        print("[VIEW ERROR]", e)
        return JsonResponse({"response": "Server error occurred."}, status=500)


@csrf_exempt
def reset_chat(request):
    if request.method == "POST":
        request.session.flush()
        return JsonResponse({
            "response": (
                "Hey! I'm your AutoStream assistant. 👋\n\n"
                "Ask me about pricing, plans, or getting started 🚀"
            )
        })
    return JsonResponse({"error": "Invalid request"}, status=400)


def chat_page(request):
    return render(request, "chat.html")
