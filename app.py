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
    
    /* Custom High-Fidelity Premium Metric Cards with Sparklines */
    .metric-container {
        background: linear-gradient(135deg, #0f0f1a 0%, #141424 100%);
        border: 1px solid #2e2a4f;
        border-radius: 16px;
        padding: 20px 20px 10px 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
        margin-bottom: -10px;
    }
    .metric-container:hover {
        border-color: #7c3aed;
        transform: translateY(-2px);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-delta-pos {
        color: #10b981;
        font-size: 12px;
        font-weight: 600;
    }
    .metric-delta-neutral {
        color: #a78bfa;
        font-size: 12px;
        font-weight: 600;
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

# Account configurations completely dropped from navigation
navigation = st.sidebar.radio(
    "NAVIGATION HUB",
    ["📊 Dashboard Overview", "🎬 Analyze Video Engine", "📁 Saved Video History", "💎 Subscriptions & Pricing"]
)

st.sidebar.markdown("<div style='position: fixed; bottom: 20px;'>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("⚡ **Account Status:** `Creator Level Tier`")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PREMIUM CARD SPARKLINE GRAPH ENGINE
# ==========================================
def render_graphical_card(title, value, delta, spark_trend, color_hex, is_neutral=False):
    # Render text layout
    delta_class = "metric-delta-neutral" if is_neutral else "metric-delta-pos"
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="{delta_class}">{delta}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate integrated miniature sparkline graph directly under metrics
    fig = go.Figure(go.Scatter(y=spark_trend, mode='lines', line=dict(color=color_hex, width=2.5)))
    fig.update_layout(
        hovermode=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=5, t=2, b=2),
        height=45,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 1. LIVE PERFORMANCE DASHBOARD
# ==========================================
if navigation == "📊 Dashboard Overview":
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("<h1 style='margin-bottom: 0;'>Welcome back, Creator! ⚡</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Here is the automated overview of your ongoing video performance indexes.</p>", unsafe_allow_html=True)
    with h_col2:
        st.write("")
        if st.button("＋ Analyze New Asset", use_container_width=True):
            st.info("Switching engine lanes... Click on 'Analyze Video Engine' in the left menu bar!")

    st.divider()

    # Premium Graphical Cards Row with unique trends matching your exact layout styles
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_graphical_card("Videos Analyzed", "124", "▲ +18% from last month", [100, 105, 102, 110, 115, 112, 124], "#3b82f6")
    with c2:
        render_graphical_card("Average Score", "72 / 100", "▲ +6% from last month", [65, 68, 67, 70, 69, 74, 72], "#a78bfa")
    with c3:
        render_graphical_card("Best Performing", "91 / 100", "🏆 Cable Bill Hack.mp4", [80, 82, 85, 84, 89, 88, 91], "#f59e0b", is_neutral=True)
    with c4:
        render_graphical_card("Hook Strength", "78%", "▲ +9% from last month", [70, 72, 71, 75, 73, 76, 78], "#10b981")

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
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Average Score'], mode='lines', name='Avg Score', line=dict(color='#a78bfa', width=3))) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Hook Strength'], mode='lines', name='Hook Vector', line=dict(color='#3b82f6', width=2))) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Retention Rate'], mode='lines', name='Retention Avg', line=dict(color='#10b981', width=2))) 
        
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

    search_q = st.text_input("🔍 Search Historical Filenames", placeholder="Type a file keyword to filter data...")
    
    history_data = {
        "Project Filename": ["Cable Bill Hack.mp4", "Stop Wasting Money.mp4", "Easy Phone Trick.mp4", "Hidden Features.mp4", "WiFi Booster Setup.mp4"],
        "Execution Date": ["2026-06-18", "2026-06-17", "2026-06-16", "2026-06-15", "2026-06-14"],
        "Duration": ["56s", "48s", "35s", "42s", "51s"],
        "Retention Index": [91, 67, 84, 45, 61],
        "Platform Optimized": ["TikTok Pro", "YT Shorts", "Instagram Reels", "TikTok Pro", "YT Shorts"]
    }
    df_history = pd.DataFrame(history_data)
