from django.shortcuts import render
from django.http import JsonResponse
import json


from django.http import JsonResponse
import json
from .gemini import detect_intent


from .rag import retrieve_context
from .gemini import detect_intent, generate_rag_response
from .tools import mock_lead_capture
from .graph import app
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chat_view(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "")

        # Load session memory
        state = request.session.get("agent_state", {
            "message": "",
            "intent": "",
            "response": "",
            "name": None,
            "email": None,
            "platform": None,
            "step": None
        })

        # Update message
        state["message"] = message

        #  Run LangGraph
        try:
            result = app.invoke(state)
            response = result.get("response", "No response")

            #  Save state back
            request.session["agent_state"] = result
            request.session.modified = True

        except Exception as e:
            print("GRAPH ERROR:", e)
            response = "Something went wrong."

        return JsonResponse({"response": response})

    except Exception as e:
        print("VIEW ERROR:", e)
        return JsonResponse({"response": "Server error occurred."})



from django.shortcuts import render
def chat_page(request):
    return render(request, "chat.html")

