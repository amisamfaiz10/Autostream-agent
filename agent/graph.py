from typing import TypedDict, Optional
from langgraph.graph import StateGraph

from .gemini import detect_intent, generate_rag_response
from .rag import retrieve_context
from .tools import mock_lead_capture


class AgentState(TypedDict):
    message: str
    intent: str
    response: str
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    step: Optional[str]


# ─────────────────────────────────────────────
# NODES
# ─────────────────────────────────────────────

def greeting_node(state: AgentState) -> AgentState:
    return {**state, "response": "Hey! 👋 How can I help you with AutoStream today?"}


def intent_node(state: AgentState) -> AgentState:
    """Detect intent only when we're NOT mid lead-capture flow."""
    # If a lead flow is already in progress, preserve intent so router keeps us in lead
    if state.get("step") and state["step"] not in (None, "done"):
        return state

    intent = detect_intent(state.get("message", ""))
    return {**state, "intent": intent}


def rag_node(state: AgentState) -> AgentState:
    message = state.get("message", "")
    context = retrieve_context(message)

    if not context:
        return {**state, "response": "I don't have specific info on that. Feel free to ask about our pricing or plans!"}

    try:
        response = generate_rag_response(message, context)
    except Exception as e:
        print("Gemini failed:", e)
        response = context  # fallback to raw context

    return {**state, "response": response}


def lead_node(state: AgentState) -> AgentState:
    """
    Step machine for lead capture.

    step=None      → start flow, ask for name
    step='name'    → user just sent their name, save it, ask for email
    step='email'   → user just sent their email, save it, ask for platform
    step='platform'→ user just sent their platform, save it, call API
    """
    step = state.get("step")
    message = state.get("message", "").strip()

    # ── Step 0: Kick off the flow ──────────────────────────
    if not step or step == "done":
        return {
            **state,
            "step": "name",
            "response": "Awesome! Let's get you set up 🚀\n\nWhat's your **name**?"
        }

    # ── Step 1: Name just received → ask email ─────────────
    if step == "name":
        return {
            **state,
            "name": message,
            "step": "email",
            "response": f"Nice to meet you, {message}! What's your **email address**?"
        }

    # ── Step 2: Email just received → ask platform ─────────
    if step == "email":
        return {
            **state,
            "email": message,
            "step": "platform",
            "response": "Almost there! Which creator platform are you on? (e.g. YouTube, Instagram, TikTok)"
        }

    # ── Step 3: Platform just received → fire API ──────────
    if step == "platform":
        name = state.get("name", "Unknown")
        email = state.get("email", "Unknown")
        platform = message

        result = mock_lead_capture(name, email, platform)
        print("Lead capture result:", result)

        return {
            **state,
            "platform": platform,
            "step": "done",
            "response": (
                f"You're all set, {name}! 🎉\n\n"
                f"Our team will reach out to **{email}** shortly to get you started on AutoStream.\n\n"
                f"In the meantime, feel free to ask anything else!"
            )
        }

    # Fallback (shouldn't be reached)
    return {**state, "response": "Something went wrong with the lead flow. Let's start over — what's your name?", "step": "name"}


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────

def route(state: AgentState) -> str:
    step = state.get("step")

    # Mid lead-capture flow → keep going
    if step and step not in (None, "done"):
        return "lead"

    intent = state.get("intent", "")

    if intent == "greeting":
        return "greeting"
    if intent == "high_intent":
        return "lead"
    if intent == "product_inquiry":
        return "rag"

    # Default fallback
    return "greeting"


# ─────────────────────────────────────────────
# GRAPH
# ─────────────────────────────────────────────

workflow = StateGraph(AgentState)

workflow.add_node("greeting", greeting_node)
workflow.add_node("intent", intent_node)
workflow.add_node("rag", rag_node)
workflow.add_node("lead", lead_node)

workflow.set_entry_point("intent")

workflow.add_conditional_edges("intent", route)
workflow.add_edge("greeting", "__end__")
workflow.add_edge("rag", "__end__")
workflow.add_edge("lead", "__end__")

app = workflow.compile()
