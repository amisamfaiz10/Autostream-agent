from typing import TypedDict, Optional

class AgentState(TypedDict):
    message: str
    intent: str
    response: str
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    step: Optional[str]



from .gemini import detect_intent, generate_rag_response
from .rag import retrieve_context
from .tools import mock_lead_capture


def greeting_node(state):
    return {**state, "response": "Hey! How can I help you with AutoStream?"}



#  Intent Node
def intent_node(state):
    message = (state.get("message") or "").lower()

    intent = detect_intent(message)

    # reset on new queries
    if any(word in message for word in ["price", "plan", "cost", "tell", "what"]):
        return {**state, "intent": "product_inquiry", "step": None}

    if any(word in message for word in ["hi", "hello", "hey"]):
        return {**state, "intent": "greeting", "step": None}

    return {**state, "intent": intent}



#  RAG Node
def rag_node(state):
    try:
        message = state.get("message", "")
        context = retrieve_context(message)

        if not context:
            return {**state, "response": "I couldn't find info on that."}

        try:
            response = generate_rag_response(message, context)
        except Exception as e:
            print("Gemini failed:", e)
            response = context  # fallback

        return {**state, "response": response}

    except Exception as e:
        print("RAG NODE ERROR:", e)
        return {**state, "response": "Something went wrong."}




#  Lead Node
def lead_node(state):
    step = state.get("step")

    # Step 1: Ask name
    if step == "asking_name":
        return {**state, "response": "What's your name?", "step": "get_name"}

    if step == "get_name":
        state["name"] = state["message"]
        return {**state, "response": "Enter your email", "step": "get_email"}

    if step == "get_email":
        state["email"] = state["message"]
        return {**state, "response": "Which platform?", "step": "get_platform"}

    if step == "get_platform":
        state["platform"] = state["message"]

        mock_lead_capture(
            state["name"],
            state["email"],
            state["platform"]
        )

        return {
            **state,
            "response": "Awesome! Our team will reach out to you shortly.",
            "step": "done"
        }

    # Start flow
    return {**state, "response": "Let's get started. What's your name?", "step": "get_name"}





def route(state):

    # Continue lead ONLY if explicitly in flow
    if state.get("step") and state["step"] != "done":
        return "lead"

    if state["intent"] == "greeting":
        return "greeting"

    if state["intent"] == "high_intent":
        return "lead"

    if state["intent"] == "product_inquiry":
        return "rag"

    return "greeting"





from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("greeting", greeting_node)
workflow.add_node("intent", intent_node)
workflow.add_node("rag", rag_node)
workflow.add_node("lead", lead_node)

# Flow
workflow.set_entry_point("intent")


workflow.add_conditional_edges("intent", route)
workflow.add_edge("greeting", "__end__")
workflow.add_edge("rag", "__end__")
workflow.add_edge("lead", "__end__")

app = workflow.compile()

