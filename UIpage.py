import time
import streamlit as st
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# Page Configuration
st.set_page_config(
    page_title="Nexus Research | Multi-Agent Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sleek Glassmorphic Modern Dark Theme CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #090d16;
        color: #e2e8f0;
    }
    
    /* Header Card */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    
    .title-gradient {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.4rem;
    }

    .subtitle-text {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1322;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .sidebar-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Inputs & Buttons */
    .stTextInput input {
        background-color: #131b2e !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease;
    }

    .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 20px -3px rgba(79, 70, 229, 0.45) !important;
    }

    /* Custom Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre;
        border-radius: 10px;
        color: #94a3b8;
        background-color: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        font-weight: 500;
        padding: 0 16px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        color: #c084fc !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
    }

    /* Data Containers */
    .output-card {
        background: #0f172a;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* Streamlit Container Adjustments */
    div[data-testid="stStatusWidget"] {
        background-color: #131b2e;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


def safe_invoke(agent_or_chain, inputs):
    """Local execution safe wrapper"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return agent_or_chain.invoke(inputs)
        except Exception as e:
            err_msg = str(e)
            st.warning(f"⚠️ Retry attempt {attempt+1}/{max_retries}: {err_msg}")
            time.sleep(2)
    raise Exception("Execution failed locally.")


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # Step 1: Search Agent
    search_agent = build_search_agent()
    search_result = safe_invoke(search_agent, {
        "input": f"Find recent, reliable and detailed information about: {topic}"
    })
    state["search_results"] = search_result['output']

    # Step 2: Reader Agent
    reader_agent = build_reader_agent()
    reader_result = safe_invoke(reader_agent, {
        "input": state['search_results'][:800]
    })
    state["scraped_content"] = reader_result['output']

    # Step 3: Writer Chain
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
    )
    writer_res = safe_invoke(writer_chain, {
        "topic": topic,
        "research": research_combined
    })
    report = writer_res.content if hasattr(writer_res, 'content') else str(writer_res)
    state["report"] = report

    # Step 4: Critic Chain
    critic_res = safe_invoke(critic_chain, {
        "report": report
    })
    critic_report = critic_res.content if hasattr(critic_res, 'content') else str(critic_res)
    state["critic_report"] = critic_report

    return state


def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚡ Engine Specs")
        st.markdown("""
        <div class="sidebar-card">
            <div class="status-badge">🟢 Local Ollama (qwen2.5)</div>
            <p style="color: #64748b; font-size: 0.8rem; margin-top: 10px; margin-bottom: 0;">
                Zero API keys, 100% private execution running on local host.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧩 Pipeline Agents")
        st.markdown("""
        * **1. Search Agent** — *Scouts web index*
        * **2. Reader Agent** — *Deep content extraction*
        * **3. Writer Chain** — *Synthesis & Drafting*
        * **4. Critic Chain** — *Quality benchmark*
        """)
        
        st.markdown("---")
        st.caption("Build v2.4 • Fully Local Architecture")

    # Main Hero Banner
    st.markdown("""
    <div class="main-header">
        <div class="title-gradient">Nexus Research</div>
        <p class="subtitle-text">Autonomous Multi-Agent Research Assistant Powered by Local Qwen2.5</p>
    </div>
    """, unsafe_allow_html=True)

    # Input Form Layout
    col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    
    with col_input:
        topic = st.text_input(
            "Research Query Target", 
            placeholder="e.g., Next-Gen Solid State Battery Architectures 2026",
            label_visibility="visible"
        )
        
    with col_btn:
        run_button = st.button("Launch Agents 🚀")

    if run_button:
        if not topic.strip():
            st.error("Please enter a research topic to proceed.")
            return

        # Status Tracker
        with st.status("🧠 Executing Autonomous Agent Mesh...", expanded=True) as status:
            st.write("🔍 **Search Agent** querying local knowledge & tools...")
            time.sleep(0.3)
            
            st.write("📖 **Reader Agent** extracting deep metadata & content...")
            time.sleep(0.3)
            
            st.write("✍️ **Writer Chain** compiling structured thesis report...")
            time.sleep(0.3)
            
            st.write("🧐 **Critic Chain** scoring analysis and verifying output quality...")
            
            # Execute Pipeline
            state = run_research_pipeline(topic)
            
            status.update(label="✨ Intelligence Compilation Completed!", state="complete", expanded=False)

        st.markdown("---")

        # Results Dashboard
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Final Synthesis Report", 
            "🎯 Peer Review & Score", 
            "🌐 Search Intelligence", 
            "📄 Raw Scraped Context"
        ])
        
        with tab1:
            st.markdown("### Executive Synthesis")
            st.markdown(state["report"])
            
        with tab2:
            st.markdown("### Quality Audit")
            st.markdown(state["critic_report"])
            
        with tab3:
            st.markdown("### Information Discovery Stream")
            st.text_area("Search Logs", state["search_results"], height=320)
            
        with tab4:
            st.markdown("### Scraped Document Stream")
            st.text_area("Content Dump", state["scraped_content"], height=320)

if __name__ == "__main__":
    main()