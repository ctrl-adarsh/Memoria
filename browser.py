import streamlit as st
import sqlite3
import pandas as pd

# Page Config
st.set_page_config(page_title="Memoria Explorer", page_icon="🧠", layout="wide")

def get_memories(search_query=""):
    conn = sqlite3.connect("memoria_vault.db")
    if search_query:
        # FTS5 search for the UI
        query = "SELECT rowid, content FROM memories WHERE memories MATCH ? ORDER BY rowid DESC"
        df = pd.read_sql_query(query, conn, params=(search_query,))
    else:
        query = "SELECT rowid, content FROM memories ORDER BY rowid DESC"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- UI LAYOUT ---
st.title("🧠 Memoria: Visual Context Browser")
st.markdown("Explore what your agent has extracted and archived in Warm Storage.")

# Sidebar Stats
memories_df = get_memories()
st.sidebar.metric("Total Facts Archived", len(memories_df))
if st.sidebar.button("♻️ Refresh View"):
    st.rerun()

# Search Bar
search = st.text_input("🔍 Search Memories (e.g., 'Bali', 'Phone', 'Wedding')", "")

# Display Data
if not memories_df.empty:
    filtered_df = get_memories(search) if search else memories_df
    
    # Clean display
    for index, row in filtered_df.iterrows():
        with st.container():
            st.info(f"**Fact #{row['rowid']}**\n\n{row['content']}")
else:
    st.warning("No memories found. Chat with your bot first to trigger a 'Flush'!")

st.sidebar.markdown("---")
st.sidebar.caption("Memoria Context Engineering Framework v0.1")