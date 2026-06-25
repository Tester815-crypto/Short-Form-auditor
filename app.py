import streamlit as st
import os
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from moviepy import VideoFileClip
from google import genai
from dotenv import load_dotenv

# 1. Initialize environments and configurations
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="ViralScan AI - Premium Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ADVANCED NEON PURPLE & ULTRA-BLACK CSS
# ==========================================
st.markdown("""
    <style>
    /* Absolute Layout Deep-Black Foundations */
    .stApp {
        background-color: #06060a !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0b0b11 !important;
        border-right: 1px solid #1e1b4b !important;
    }
    
    /* Typography & Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    /* Custom High-Fidelity Premium Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, #0f0f1a 0%, #141424 100%);
        border: 1px solid #2e2a4f;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .metric-container:hover {
        border-color: #7c3aed;
        transform: translateY(-2px);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 36px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 6px;
    }
    .metric-delta {
        color: #10b981;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    
    /* Custom Premium Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6d28d9 0%, #4c1d95 100%) !important;
        color: #ffffff !important;
        border: 1px solid #7c3aed !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(109, 40, 217, 0.3);
        transition: all 0.3s ease-in-out !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #7c3aed 0%, #6d28d9 100%) !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.6) !important;
        transform: scale(1.02);
    }
    
    /* Input Field Styling */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: #11111f !important;
        border: 1px solid #2e2a4f !important;
        border-radius: 8px !important;
    }
    
    /* Clean Divider borders */
    hr {
        border-color: #1e1b4b !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR SYSTEM INTERFACE
# ==========================================
st.sidebar.markdown("<h2 style='color: #a78bfa; margin-bottom: 5px;'>🔮 ViralScan AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='background-color: #2e1065; color: #c084fc; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;'>PRO WORKSPACE</span>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

navigation = st.sidebar.radio(
    "NAVIGATION HUB",
    ["📊 Dashboard Overview", "🎬 Analyze Video Engine", "📁 Saved Video History", "💎 Subscriptions & Pricing", "⚙️ Account Settings"]
)

st.sidebar.markdown("<div style='position: fixed; bottom: 20px;'>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("⚡ **Account Status:** `Creator Level Tier`")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Helper function to render a premium dashboard card
def render_metric_card(title, value, delta):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">{delta}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 1. LIVE PERFORMANCE DASHBOARD
# ==========================================
if navigation == "📊 Dashboard Overview":
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("<h1 style='margin-bottom: 0;'>Welcome back, Creator! 👋</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Here is the automated overview of your ongoing video performance indexes.</p>", unsafe_allow_html=True)
    with h_col2:
        st.write("")
        if st.button("＋ Analyze New Asset", use_container_width=True):
            st.info("Switching engine lanes... Click on 'Analyze Video Engine' in the left menu bar!")

    st.divider()

    # Highly Requested Dashboard Card row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Videos Analyzed", "124", "▲ +18% from last month")
    with c2:
        render_metric_card("Average Score", "72 / 100", "▲ +6% from last month")
    with c3:
        render_metric_card("Best Performing", "91 / 100", "🏆 Cable Bill Hack.mp4")
    with c4:
        render_metric_card("Hook Strength", "78%", "▲ +9% from last month")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Row split into Interactive Analytics & Recent Video Logs
    chart_col, list_col = st.columns([2.3, 1.7])
    
    with chart_col:
        st.markdown("### 📈 Audience Retention Patterns")
        st.caption("Cross-platform model trajectory metrics for the last 30 intervals")
        
        # Build out true mock data lines
        dates = [datetime.today() - timedelta(days=i) for i in range(30)][::-1]
        df = pd.DataFrame({
            "Date": dates,
            "Average Score": [62 + (i*0.4) + (i%4) for i in range(30)],
            "Hook Strength": [71 + (i*0.3) - (i%3) for i in range(30)],
            "Retention Rate": [45 + (i*0.7) + (i%5) for i in range(30)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Average Score'], mode='lines', name='Avg Score', line=dict(color='#a78bfa', width=3))) # Purple Accent
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Hook Strength'], mode='lines', name='Hook Vector', line=dict(color='#3b82f6', width=2))) # Royal Blue
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Retention Rate'], mode='lines', name='Retention Avg', line=dict(color='#10b981', width=2))) # Emerald
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            xaxis=dict(showgrid=False, linecolor='#2e2a4f'),
            yaxis=dict(gridcolor='#1e1b4b', range=[0, 100], linecolor='#2e2a4f'),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with list_col:
        st.markdown("### 🕒 Real-Time Audit Feed")
        st.caption("Latest short-form items run through the core processor")
        
        # High fidelity list elements matching the exact reference layout images
        st.markdown("""
        <div style='background: #0f0f1a; border: 1px solid #2e2a4f; border-radius: 12px; padding: 16px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e1b4b; padding-bottom: 12px; margin-bottom: 12px;'>
                <div><span style='font-weight:bold; color:#ffffff;'>Cable Bill Hack.mp4</span><br><span style='color:#64748b; font-size:12px;'>May 18 • 0:56 mins</span></div>
                <div style='background: #065f46; color: #34d399; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px;'>91</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e1b4b; padding-bottom: 12px; margin-bottom: 12px;'>
                <div><span style='font-weight:bold; color:#ffffff;'>Stop Wasting Money.mp4</span><br><span style='color:#64748b; font-size:12px;'>May 17 • 0:48 mins</span></div>
                <div style='background: #854d0e; color: #fef08a; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px;'>67</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e1b4b; padding-bottom: 12px; margin-bottom: 12px;'>
                <div><span style='font-weight:bold; color:#ffffff;'>Easy Phone Trick.mp4</span><br><span style='color:#64748b; font-size:12px;'>May 16 • 0:35 mins</span></div>
                <div style='background: #065f46; color: #34d399; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px;'>84</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e1b4b; padding-bottom: 12px; margin-bottom: 12px;'>
                <div><span style='font-weight:bold; color:#ffffff;'>Hidden Features.mp4</span><br><span style='color:#64748b; font-size:12px;'>May 15 • 0:42 mins</span></div>
                <div style='background: #991b1b; color: #fca5a5; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px;'>45</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div><span style='font-weight:bold; color:#ffffff;'>WiFi Booster Setup.mp4</span><br><span style='color:#64748b; font-size:12px;'>May 14 • 0:51 mins</span></div>
                <div style='background: #854d0e; color: #fef08a; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px;'>61</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 2. CORE AUDIO-VISUAL AI SCAN ENGINE
# ==========================================
elif navigation == "🎬 Analyze Video Engine":
    st.markdown("<h1>🎬 Algorithmic Pre-Flight Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Drop files into the container module below to initiate programmatic virality auditing metrics.</p>", unsafe_allow_html=True)
    st.divider()

    uploaded_file = st.file_uploader("Drop short-form creative assets here (.mp4 or .mov formats supported)", type=["mp4", "mov"])

    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        temp_filename = "user_upload_temp.mp4"
        
        if "file_verified_key" not in st.session_state or st.session_state.file_verified_key != file_key:
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            video_analysis = VideoFileClip(temp_filename)
            st.session_state.duration_seconds = video_analysis.duration
            video_analysis.close() 
            if os.path.exists(temp_filename):
                os.remove(temp_filename) 
            st.session_state.file_verified_key = file_key

        duration_seconds = st.session_state.duration_seconds
        
        if duration_seconds > 120:
            st.error(f"🚨 Operational Error: The target clip clocks at {int(duration_seconds)}s. Ensure limits remain below 2 minutes.")
        else:
            st.success(f"✅ Infrastructure Verified: Length metadata constraints validated ({int(duration_seconds)}s). Framework primed.")
            
            if st.button("🚀 Execute Neural Simulation Runtime"):
                with st.spinner("Processing visual timelines and synchronizing audio tracking matrix..."):
                    try:
                        with open(temp_filename, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        client = genai.Client(api_key=api_key)
                        uploaded_ai_file = client.files.upload(file=temp_filename)
                        
                        while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                            time.sleep(2)
                            uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                        
                        system_prompt = """
                        You are an expert retention analyst for short form video content. 
                        Break down the video into sections: Performance Grade, 3-Second Hook Audit, Retention Drop-offs, and High-Impact Fixes. Make recommendations direct, punchy, and highly technical.
                        """
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[uploaded_ai_file, system_prompt]
                        )
                        st.session_state.dash_report = response.text
                        try:
                            client.files.delete(name=uploaded_ai_file.name)
                        except:
                            pass
                    except Exception as error:
                        st.error(f"System Exception Encountered: {error}")
                    finally:
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)

            if "dash_report" in st.session_state:
                st.divider()
                st.markdown("<h3 style='color: #a78bfa;'>🧠 Diagnostic Output Matrix</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown(st.session_state.dash_report)

# ==========================================
# 3. INTERACTIVE HISTORICAL STORAGE REPOSITORY
# ==========================================
elif navigation == "📁 Saved Video History":
    st.markdown("<h1>📁 Secure Asset Retention Logs</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Search, review, filter, and extract analytical reports from previously processed short-form content models.</p>", unsafe_allow_html=True)
    st.divider()

    # Search Bar layout filter
    search_q = st.text_input("🔍 Search Historical Filenames", placeholder="Type a file keyword to filter data...")
    
    # Historic Data Table Dataframe Construction
    history_data = {
        "Project Filename": ["Cable Bill Hack.mp4", "Stop Wasting Money.mp4", "Easy Phone Trick.mp4", "Hidden Features.mp4", "WiFi Booster Setup.mp4"],
        "Execution Date": ["2026-06-18", "2026-06-17", "2026-06-16", "2026-06-15", "2026-06-14"],
        "Duration": ["56s", "48s", "35s", "42s", "51s"],
        "Retention Index": [91, 67, 84, 45, 61],
        "Platform Optimized": ["TikTok Pro", "YT Shorts", "Instagram Reels", "TikTok Pro", "YT Shorts"]
    }
    df_history = pd.DataFrame(history_data)
    
    if search_q:
        df_history = df_history[df_history["Project Filename"].str.contains(search_q, case=False)]

    st.dataframe(
        df_history,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Retention Index": st.column_config.ProgressColumn("Retention Index", min_value=0, max_value=100, format="%d pts"),
            "Project Filename": st.column_config.TextColumn("Target File Name", help="File uploaded to system core"),
        }
    )

# ==========================================
# 4. SUBSCRIPTION PLAN MODES
# ==========================================
elif navigation == "💎 Subscriptions & Pricing":
    st.markdown("<h1>💎 Premium Architecture Tiers</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Upgrade or scale infrastructure boundaries to suit agency rendering throughput requests.</p>", unsafe_allow_html=True)
    st.divider()

    pc1, pc2, pc3 = st.columns(3)
    
    with pc1:
        st.markdown("""
        <div style='background:#0f0f1a; border: 1px solid #1e1b4b; border-radius:16px; padding:24px; text-align:center;'>
            <h3 style='color:#94a3b8;'>Starter Sandbox</h3>
            <h2 style='font-size:36px; margin: 15px 0;'>$0 <span style='font-size:14px; color:gray;'>/ month</span></h2>
            <hr style='border-color:#1e1b4b;'>
            <p style='text-align:left;'>• 5 Basic Scans Monthly<br>• Max file duration 60s<br>• Core Processing Units</p>
            <div style='margin-top:30px; padding:10px; background:#1e1b4b; border-radius:8px; color:gray; font-size:12px; font-weight:bold;'>INACTIVE IN WORKSPACE</div>
        </div>
        """, unsafe_allow_html=True)
        
    with pc2:
        st.markdown("""
        <div style='background: linear-gradient(145deg, #180f2b 0%, #0f0f1a 100%); border: 2px solid #7c3aed; border-radius:16px; padding:24px; text-align:center; box-shadow: 0 0 25px rgba(124,58,237,0.25);'>
            <h3 style='color:#a78bfa;'>Creator Studio Pro</h3>
            <h2 style='font-size:36px; margin: 15px 0; color:#ffffff;'>$49 <span style='font-size:14px; color:#a78bfa;'>/ month</span></h2>
            <hr style='border-color:#2e2a4f;'>
            <p style='text-align:left; color:#e2e8f0;'>• Unlimited Video Engine Processing<br>• Max file duration 120s<br>• Priority Neural Grid Queue<br>• Custom Analytics Exports</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.button("✨ CURRENT WORKSPACE ACCOUNT TIER", disabled=True, use_container_width=True)
        
    with pc3:
        st.markdown("""
        <div style='background:#0f0f1a; border: 1px solid #1e1b4b; border-radius:16px; padding:24px; text-align:center;'>
            <h3 style='color:#94a3b8;'>Production Scale</h3>
            <h2 style='font-size:36px; margin: 15px 0;'>$199 <span style='font-size:14px; color:gray;'>/ month</span></h2>
            <hr style='border-color:#1e1b4b;'>
            <p style='text-align:left;'>• Unlimited Scans + Automation APIs<br>• Uncapped File Durations<br>• Dedicated AI Node Cluster access</p>
            <div style='margin-top:30px;'></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade Workspace", key="scale_btn", use_container_width=True):
            st.success("Redirecting gateway parameters to secure checkout node...")

# ==========================================
# 5. ACCOUNT WORKSPACE CONFIGURATIONS
# ==========================================
elif navigation == "⚙️ Account Settings":
    st.markdown("<h1>⚙️ Enterprise Environment Controls</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Modify system behavioral prompt architectures and update developer pipeline credentials.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🔌 Core Neural Credentials")
    user_api_input = st.text_input("Gemini API Secure Passkey Override", type="password", value="••••••••••••••••••••••••••••••••••••", help="Overrides the default repository deployment secure key variables.")
    
    st.divider()
    
    st.markdown("### 🧠 Prompt Engineering Weights")
    st.caption("Customize what metrics the retention auditor aggressively looks for during simulation pipelines.")
    custom_framework = st.text_area(
        "Custom Directives Prompt Modifier",
        value="You are a professional, ruthless short-form video retention auditor trained on high-retention frameworks (like MrBeast and Ryan Trahan pacing rules). Analyze frame tracking parameters...",
        rows=5
    )
    
    if st.button("Save Workspace Modifications"):
        st.success("Environment configuration matrix updated successfully!")
