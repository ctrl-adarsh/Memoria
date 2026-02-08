import os
import sqlite3
import re
import tiktoken
import ollama  # New local backup
from google import genai
from google.genai import types
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Memoria:
    def __init__(self, threshold=1500):
        # Cloud Clients
        self.gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Settings
        self.local_model = "qwen2.5-coder:latest" # Your local powerhouse
        self.threshold = threshold
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.db_path = "memoria_vault.db"
        self._init_db()
        self.history = []

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories USING fts5(content)")

    def _get_tokens(self, text):
        return len(self.encoder.encode(text))

    def _conflict_resolver(self, new_fact):
        """Phase 1b: Detect contradictions before archiving."""
        # Extract keywords (e.g., 'cat', 'wedding', 'phone')
        keywords = [word for word in new_fact.split() if len(word) > 4]
        if not keywords: return False
        
        search_term = " OR ".join(keywords[:3]) # Check first 3 major words
        
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT content FROM memories WHERE memories MATCH ? LIMIT 1", 
                (search_term,)
            ).fetchone()
            
        if existing:
            # Simple check: if the old fact and new fact are different but share keywords
            if existing[0].lower() != new_fact.lower():
                print(f"⚠️ CONFLICT DETECTED: New fact '{new_fact}' might contradict '{existing[0]}'")
                return True
        return False

    def _call_llm(self, system_instruction, user_input):
        """Tiered Fallback: Gemini -> OpenAI -> Ollama (Local)"""
        
        # 1. TIER 1: GEMINI
        try:
            print("[Memoria] ☁️ Trying Gemini...")
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(system_instruction=system_instruction),
                contents=user_input
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini Limit Reached: {str(e)[:50]}")

        # 2. TIER 2: OPENAI
        try:
            print("[Memoria] ☁️ Trying OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ OpenAI Limit Reached: {str(e)[:50]}")

        # 3. TIER 3: OLLAMA (Llama 3.1 Local)
        try:
            print(f"[Memoria] 🏠 Local Engine: {self.local_model}...")
            # We use ollama.chat to handle the message templating automatically
            response = ollama.chat(
                model=self.local_model,
                messages=[
                    {'role': 'system', 'content': system_instruction},
                    {'role': 'user', 'content': user_input},
                ],
                options={
                    'temperature': 0.1,  # Lower temperature for factual extraction
                    'num_predict': 256,   # Limit response length for speed
                    'stop': ["USER:", "ASSISTANT:"]
                }
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"❌ All Engines Failed: {str(e)}")
            return "I am currently processing in offline mode and will archive this locally."

    def _flush_orchestrator(self):
        print("\n[Memoria] 🚨 Orchestrating flush & conflict check...")
        full_history = "\n".join([f"{h['role']}: {h['content']}" for h in self.history])
        instruction = "Extract critical atomic facts (dates, names, preferences) from this chat. List only."
        
        extracted_text = self._call_llm(instruction, full_history)
        facts = [f.strip("- ") for f in extracted_text.strip().split('\n') if len(f) > 5]
        
        with sqlite3.connect(self.db_path) as conn:
            for fact in facts:
                # RUN CONFLICT RESOLVER
                if not self._conflict_resolver(fact):
                    conn.execute("INSERT INTO memories (content) VALUES (?)", (fact,))
                else:
                    # Logic: If conflict, we append it but tag it for manual review
                    conn.execute("INSERT INTO memories (content) VALUES (?)", (f"[CONFLICT] {fact}",))
        
        self.history = self.history[-2:]
        print(f"[Memoria] ✅ Archived {len(facts)} facts.\n")

    def _retrieval_engine(self, user_query):
        clean_query = re.sub(r'[^\w\s]', ' ', user_query)
        search_terms = " OR ".join(clean_query.split())
        if not search_terms: return ""
        try:
            with sqlite3.connect(self.db_path) as conn:
                results = conn.execute(
                    "SELECT content FROM memories WHERE memories MATCH ? LIMIT 3", 
                    (search_terms,)
                ).fetchall()
            return "\n".join([f"- {r[0]}" for r in results])
        except: return ""

    def chat(self, user_input):
        # 1. Retrieve Context
        past_context = self._retrieval_engine(user_input)
        
        # 2. Build Instruction
        system_instruction = f"""You are a personal AI with long-term memory. 
        RELEVANT PAST MEMORIES:
        {past_context if past_context else "No relevant past memories found."}
        
        If you use a memory from the list above, mention it briefly at the end of your response."""
        
        self.history.append({"role": "user", "content": user_input})
        
        # 3. Get Response (Using your tiered fallback logic)
        response_text = self._call_llm(system_instruction, user_input)
        
        # 4. Handle "Explainability" UI
        source_note = ""
        if past_context:
            source_note = "\n\n*(Source: Retrieved from Warm Storage)*"
        
        full_response = response_text + source_note
        self.history.append({"role": "model", "content": full_response})
        
        # 5. Token Check & Auto-Flush
        if self._get_tokens(str(self.history)) > self.threshold:
            self._flush_orchestrator()
            
        return full_response

if __name__ == "__main__":
    bot = Memoria()
    print("--- MEMORIA SYSTEM (HYBRID/LOCAL) ONLINE ---")
    while True:
        msg = input("User: ")
        if msg.lower() in ['exit', 'quit']: break
        print(f"AI: {bot.chat(msg)}")