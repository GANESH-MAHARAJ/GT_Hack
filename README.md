Retail customers today expect instant answers. ”Is this store open?” ”Do you have size 10 in
stock?” ”Where is my order?” Standard chatbots are dumb—they give generic answers.


# GroundTruth Concierge — Hyper-Personalized Customer Experience Agent  
### Dual-Agent AI · Privacy-Safe · Location-Aware · RAG-Powered

### H-002 Customer Experience Automation

### Track: Customer Experience & Conversational AI


GroundTruth Concierge is a next-generation customer experience assistant designed for retail use-cases where *real-world context* matters. Built for the GroundTruth Mini AI Hackathon, this system bridges digital data with physical-world intelligence using a **dual-LLM pipeline**, **location-aware store intelligence**, **policy RAG over internal documents**, and **strict privacy masking** for all user data.

---

## 🚀 Key Features

### **1. Dual-Agent LLM Architecture (Llama 3.1 – Local, Private)**
- **Agent-1 (Intent Engine):**  
  Extracts up to **5 high-confidence intents** from the user’s masked message.
- **Agent-2 (Response Engine):**  
  Combines user intent + nearest store + offers + RAG snippets to generate a personalized and actionable response.

This removes hallucinations and ensures deterministic reasoning.

---

### **2. Hard Privacy Layer – No Raw PII to LLMs**
Before any text reaches an LLM:
- Phone numbers → masked  
- Email IDs → masked  
- Addresses → masked  
- Order IDs → masked  

A clean “privacy-first” pipeline for enterprise-safe deployments.

---

### **3. Location-Aware Store Discovery**
Given user latitude/longitude:
- Finds nearby stores (mock dataset or external API)
- Computes distance
- Checks open/closed status
- Surfaces ratings and review counts
- Generates context-aware suggestions (e.g., “You are 30m from Starbucks MG Road—open now.”)

---

### **4. RAG Over Policy Documents (Static Vector Store)**
The system includes 5 internal knowledge documents:

- Return & Refund Policy  
- Shipping Policy  
- Wi-Fi Terms  
- Loyalty Program Benefits  
- Allergen Guide  

These are embedded into ChromaDB at startup (no PDF ingestion needed).  
This allows grounded responses to:
- “What is your return policy?”  
- “How long does express delivery take?”  
- “What benefits does Gold tier get?”  
- “Is your Wi-Fi safe?”  
- “Does Caramel Latte contain gluten?”

---

### **5. Modern Chat UI**
A clean, minimal Web UI:
- Chat bubbles  
- Store info cards  
- Intent debugging  
- Dual agent reasoning workflow  

Designed for a smooth hackathon demo.

---

## 🧠 High-Level Architecture
User → Privacy Masking → Agent-1 (Intent LLM)
→ Store Locator + Offers + RAG
→ Agent-2 (Response LLM)
→ Final Personalized Reply → UI


### Components
- **FastAPI Backend**
- **Dual Llama 3.1 Agents (Ollama)**
- **ChromaDB Vector Store**
- **Local RAG for internal policies**
- **Frontend Chat UI (HTML + JS)**

---

## 📁 Project Structure
GT_hack/
│
├── backend/
│ ├── app.py # Main FastAPI server
│ ├── llm/
│ │ ├── agent_intent.py # Agent-1 (Intent Extraction)
│ │ └── agent_response.py # Agent-2 (Final Response)
│ ├── services/
│ │ ├── privacy.py # PII masking logic
│ │ ├── store_locator.py # Nearest-store logic
│ │ ├── offer_engine.py # Store coupon generator
│ │ └── rag_service.py # Static-doc RAG + Chroma
│ └── models/ # Request/response schemas
│
├── frontend/
│ └── index.html # Chat UI
│
├── rag/
│ └── vector_store/ # Auto-populated Chroma storage
│
├── running.txt # Instructions to run project
├── requirements.txt
└── README.md


---

## 📦 Installation

you can find the installation and setup instructions in the  file "running.txt"

## Sample Query Flow

I am cold and want coffee

System Response:

Agent-1 intents: FIND_NEARBY_COFFEE_SHOP, SUGGEST_WARM_DRINK, etc.

Store locator finds nearest open store.

Offers engine applies “10% off Hot Cocoa”.

Result:
You’re just 24m from Starbucks MG Road. It is open right now. 
You also have a 10% discount on hot beverages — would you like a hot cocoa?


## 🧪 FAQ / RAG Query Example

User: What is your return policy?

LLM Output: Returns can be initiated within 30 days for unopened items. 
Food items must be reported within 24 hours.
Refunds go back to the original payment method.

LLM pulls this from the Return Policy document stored in Chroma.

## 🔐 Privacy Guarantee

No raw user PII is ever sent to LLMs.

All messages are masked before model calls.

Works with internal, self-hosted LLMs (Ollama) → no external data leakage.