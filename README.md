# AutoStream AI Agent 

An AI-powered customer support agent built using Django and LangGraph.  
It can answer product queries, maintain multi-turn conversation context, and capture leads intelligently.

---

## Features

- Conversational chatbot with natural responses  
-  Multi-turn memory (retains context across 5–6 messages)  
-  RAG-based query handling (pricing, plans)  
-  Lead capture flow (name, email, platform)  
-  Interrupt handling (user can switch topics anytime)  
-  Simple, clean frontend UI  
-  Fallback handling (works even if LLM fails)  

---

##  Tech Stack

- Python  
- Django  
- LangGraph  
- Google Gemini API (optional, with fallback)  
- HTML, CSS, JavaScript  

---

## How to Run the Project Locally

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Add environment variables
5. Run migrations
6. Start server
7. Open in browser


**Architecture Explanation**
I used LangGraph to build a structured conversational agent instead of a simple request-response system. It allows me to define different steps (like intent detection, retrieval, and lead capture) as nodes and control how the conversation flows between them.
State is managed using a shared dictionary that is passed across these nodes. It stores information like the user’s message, intent, and conversation stage. This helps the system remember context across multiple turns and handle flows like lead capture step-by-step.
For answering product-related questions, I used a simple RAG approach where data (like pricing and plans) is fetched from a knowledge base. I also added a fallback so that even if the LLM fails, the system still returns a valid response, making it more reliable.



**WhatsApp Deployment (Using Webhooks)**
To integrate this agent with WhatsApp, I would use the WhatsApp Business API via providers like Meta or Twilio.

Create a webhook endpoint in Django (e.g., /webhook/)
Configure WhatsApp API to send incoming messages to this webhook
When a user sends a message:
WhatsApp forwards it to the webhook
Backend extracts the message
Pass the message into the LangGraph agent
Agent processes it (intent → RAG → lead flow)
Generate response
Send response back using WhatsApp API

To maintain conversation state, the user’s phone number can be used as a unique identifier, allowing session tracking across multiple messages.
