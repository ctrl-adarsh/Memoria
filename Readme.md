### **Capacity: Warm Storage Limits**

The "Warm Storage" in **Memoria** is poBecause it stores distilled, atomic facts rather than rawwered by **SQLite with FTS5**. , repetitive conversation transcripts, it is incredibly efficient.

* **Theoretical Limit:** SQLite can handle databases up to **140 Terabytes**.
* **Practical Limit:** For a personal AI framework, you can easily store **millions of atomic facts** (e.g., *"User's favorite color is neon green"*) before noticing any performance lag in search.
* **Token Efficiency:** A single "flush" typically condenses 2,000 tokens of chat into roughly 100-200 tokens of "atomic facts." This effectively increases your "perceived" context window by **10x to 20x** compared to a standard chatbot.

---

### **GitHub README.md**

Here is a professional, high-energy `README.md` to accompany your code. Copy this into a file named `README.md` in your project root.

```markdown
# 🧠 Memoria: A Context Engineering Framework

**Memoria** is a hybrid, multi-layered memory system designed to give LLMs "infinite" long-term recall. It solves the "Goldfish Memory" problem by monitoring token usage in real-time and automatically distilling chat history into a searchable, atomic fact database.

## 🚀 The Architecture

Memoria uses a tiered storage approach to balance speed and intelligence:

1.  **Hot Storage (In-Memory):** The current conversation buffer. High resolution, limited capacity.
2.  **Warm Storage (SQLite + FTS5):** A searchable database of distilled facts. Blazing fast keyword retrieval using Full-Text Search.
3.  **Intelligence Layer (Hybrid LLM):** A robust fallback system that cycles through **Gemini 2.0 Flash**, **OpenAI GPT-4o-mini**, and **Local Llama 3.1 (via Ollama)**.



## ✨ Key Features

- **Adaptive Flushing:** Automatically detects when the context window is near capacity and triggers a "Ghost Turn" to summarize and archive facts.
- **Conflict Resolver:** Identifies contradictions (e.g., if the user changes their favorite phone) and flags them in the UI.
- **Unstoppable Fallback:** If cloud APIs hit rate limits or budget caps, the system seamlessly switches to your local hardware (Ollama).
- **Visual Browser:** A built-in Streamlit dashboard to inspect, search, and manage the agent's archived memories.
- **Explainability:** The agent cites its sources when it pulls a fact from Warm Storage.

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (for local backup)
- Google AI Studio API Key

### 2. Install Dependencies
```bash
pip install google-genai openai ollama tiktoken python-dotenv streamlit pandas

```

### 3. Configure Environment

Create a `.env` file in the root directory:

```text
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key_optional

```

### 4. Run the Framework

Open two terminals:

**Terminal 1 (The AI Agent):**

```bash
python3 memoria.py

```

**Terminal 2 (The Memory Browser):**

```bash
streamlit run browser.py

```