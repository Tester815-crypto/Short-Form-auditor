import streamlit as st
import os
import time
import base64
import io
import random
import pandas as pd
import matplotlib.subplots as plt_subplots # Adjusted to avoid global plt issues in Streamlit
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from moviepy import VideoFileClip
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

def render_circular_gauge(score, max_score, label, color):
    """
    Renders a premium, hardware-accelerated SVG circular gauge matching the dark/purple theme.
    """
    # Calculate SVG stroke dash offset (Circumference of r=40 is ~251.2)
    percentage = min(max(score / max_score, 0.0), 1.0)
    dash_offset = 251.2 - (percentage * 251.2)
    
    gauge_html = f"""
    <div style="
        background: #0b0b11; 
        border: 1px solid #1e1b4b; 
        border-radius: 16px; 
        padding: 24px 16px; 
        text-align: center; 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease-in-out, border-color 0.2s;
    " onmouseover="this.style.borderColor='{color}';" onmouseout="this.style.borderColor='#1e1b4b';">
        <div style="position: relative; display: inline-block; width: 110px; height: 110px;">
            <svg width="100%" height="100%" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="40" stroke="#151522" stroke-width="8" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke="{color}" stroke-width="8" fill="transparent"
                        stroke-dasharray="251.2" stroke-dashoffset="{dash_offset}" stroke-linecap="round"
                        style="transition: stroke-dashoffset 1s ease-out;" />
            </svg>
            <div style="
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%); 
                font-family: 'Inter', sans-serif;
                font-size: 22px; 
                font-weight: 700; 
                color: #ffffff;
            ">
                {score}<span style="font-size: 12px; color: #64748b; font-weight: 400;">/{max_score}</span>
            </div>
        </div>
        <div style="
            margin-top: 14px; 
            font-family: 'Inter', sans-serif;
            font-size: 13px; 
            font-weight: 600; 
            color: #94a3b8; 
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">
            {label}
        </div>
    </div>
    """
    return st.markdown(gauge_html, unsafe_allow_html=True)

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="ViraLens AI - Premium Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. ADVANCED NEON PURPLE & ULTRA-BLACK CSS
# ==========================================
st.markdown("""
    <style>
    /* Absolute Layout Deep-Black Foundations */
    
    h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 700 !important; color: #ffffff !important; }
    
    /* Integrated High-Fidelity Premium Metric Card */
    .metric-card-wrapper {
        background: linear-gradient(135deg, #0f0f1a 0%, #141424 100%);
        border: 1px solid #2e2a4f;
        border-radius: 16px;
        padding: 22px 20px 16px 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 185px;
        box-sizing: border-box;
    }
    .metric-card-wrapper:hover { border-color: #7c3aed; transform: translateY(-2px); }
    .metric-title { color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { color: #ffffff; font-size: 30px; font-weight: 800; line-height: 1.1; margin-top: 4px; }
    .metric-delta { font-size: 12px; font-weight: 600; margin-top: 2px; }
    .sparkline-img { width: 100%; height: 45px; margin-top: auto; object-fit: contain; }
    
    /* Premium Sidebar Card Navigation System */
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] { gap: 12px !important; }
    div[data-testid="stSidebarUserContent"] .stRadio [data-testid="stWidgetLabel"] { display: none !important; }
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background: #11111f !important; border: 1px solid #1e1b4b !important; border-radius: 12px !important;
        padding: 16px 20px !important; transition: all 0.25s ease-in-out !important; width: 100% !important; display: block !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    div[data-testid="stSidebarUserContent"] .stRadio label:hover { border-color: #4c1d95 !important; background: #161129 !important; transform: translateX(3px); }
    div[data-testid="stSidebarUserContent"] .stRadio label[data-checked="true"] {
        background: linear-gradient(90deg, #1e113a 0%, #120e24 100%) !important; border-color: #7c3aed !important;
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.2);
    }
    div[data-testid="stSidebarUserContent"] .stRadio label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important; font-weight: 600 !important; font-size: 14px !important; margin: 0 !important;
    }
    
    /* Premium Action Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6d28d9 0%, #4c1d95 100%) !important; color: #ffffff !important;
        border: 1px solid #7c3aed !important; border-radius: 10px !important; font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important; box-shadow: 0 4px 14px rgba(109, 40, 217, 0.3); transition: all 0.3s ease-in-out !important;
    }
    .stButton>button:hover { background: linear-gradient(90deg, #7c3aed 0%, #6d28d9 100%) !important; box-shadow: 0 0 20px rgba(124, 58, 237, 0.6) !important; transform: scale(1.01); }
    div[data-baseweb="input"], div[data-baseweb="textarea"] { background-color: #11111f !important; border: 1px solid #2e2a4f !important; border-radius: 8px !important; }
    hr { border-color: #1e1b4b !important; }

    /* Customizing Streamlit Tabs to look Premium */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #11111f; border-radius: 8px 8px 0px 0px; 
        padding: 10px 20px; border: 1px solid #2e2a4f; border-bottom: none;
    }
    .stTabs [aria-selected="true"] { background-color: #1e1b4b !important; border-color: #7c3aed !important; color: #a78bfa !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR PLATFORM CONFIGURATION
# ==========================================
st.sidebar.markdown("<h2 style='color: #a78bfa; margin-bottom: 5px; letter-spacing:-0.03em;'>🔮 ViraLens AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='background-color: #2e1065; color: #c084fc; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;'>PRO WORKSPACE</span>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

navigation = st.sidebar.radio(
    "MENU_HUB",
    ["📊 Dashboard Overview", "🎬 Analyze Video Engine", "📁 Saved Video History", "💎 Subscriptions & Pricing"]
)

st.sidebar.markdown("<div style='position: fixed; bottom: 20px;'>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("⚡ **Account Status:** `Creator Level Tier`")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Helper Engines to build embedded base64 sparkline cards
def get_sparkline_base64(trend_data, color_hex):
    fig, ax = plt.subplots(figsize=(3, 0.55), dpi=100)
    ax.plot(trend_data, color=color_hex, linewidth=2.5)
    ax.axis('off')
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def build_graphical_card(title, value, delta, delta_color, trend_data, line_color):
    img_b64 = get_sparkline_base64(trend_data, line_color)
    return f"""
    <div class="metric-card-wrapper">
        <div>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta" style="color: {delta_color};">{delta}</div>
        </div>
        <img class="sparkline-img" src="data:image/png;base64,{img_b64}" />
    </div>
    """

# ==========================================
# 4. PLATFORM INTERACTIVE DASHBOARD
# ==========================================
if navigation == "📊 Dashboard Overview":
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("<h1 style='margin-bottom: 0;'>Welcome back, Creator! ⚡</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Here is the automated overview of your ongoing video performance indexes.</p>", unsafe_allow_html=True)
    with h_col2:
        st.write("")
        if st.button("＋ Analyze New Asset", use_container_width=True):
            st.info("Redirecting... Click on 'Analyze Video Engine' on the sidebar block menu.")

    st.divider()

    # Graphical metric cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(build_graphical_card("Videos Analyzed", "124", "▲ +18% from last month", "#10b981", [100, 105, 102, 110, 115, 112, 124], "#3b82f6"), unsafe_allow_html=True)
    with c2: st.markdown(build_graphical_card("Average Score", "72 / 100", "▲ +6% from last month", "#10b981", [65, 68, 67, 70, 69, 74, 72], "#a78bfa"), unsafe_allow_html=True)
    with c3: st.markdown(build_graphical_card("Best Performing", "91 / 100", "🏆 Cable Bill Hack.mp4", "#a78bfa", [80, 82, 85, 84, 89, 88, 91], "#f59e0b"), unsafe_allow_html=True)
    with c4: st.markdown(build_graphical_card("Hook Strength", "78%", "▲ +9% from last month", "#10b981", [70, 72, 71, 75, 73, 76, 78], "#10b981"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analytics charts & lists
    chart_col, list_col = st.columns([2.3, 1.7])
    with chart_col:
        st.markdown("### 📈 Audience Retention Patterns")
        st.caption("Cross-platform model trajectory metrics for the last 30 intervals")
        dates = [datetime.today() - timedelta(days=i) for i in range(30)][::-1]
        df = pd.DataFrame({"Date": dates, "Average Score": [62 + (i*0.4) + (i%4) for i in range(30)], "Hook Strength": [71 + (i*0.3) - (i%3) for i in range(30)], "Retention Rate": [45 + (i*0.7) + (i%5) for i in range(30)]})
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Average Score'], mode='lines', name='Avg Score', line=dict(color='#a78bfa', width=3))) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Hook Strength'], mode='lines', name='Hook Vector', line=dict(color='#3b82f6', width=2))) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Retention Rate'], mode='lines', name='Retention Avg', line=dict(color='#10b981', width=2))) 
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), xaxis=dict(showgrid=False, linecolor='#2e2a4f'), yaxis=dict(gridcolor='#1e1b4b', range=[0, 100], linecolor='#2e2a4f'), margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1))
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
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 5. CORE AUDIO-VISUAL AI SCAN ENGINE
# ==========================================
elif navigation == "🎬 Analyze Video Engine":
    st.markdown("<h1>🎬 Algorithmic Pre-Flight Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Select the target algorithm below, then upload your short-form asset to initiate a platform-specific virality audit.</p>", unsafe_allow_html=True)
    st.divider()

    # The New Interactive Platform Tabs
    tab_yt, tab_ig, tab_tt, tab_fb = st.tabs(["🔴 YT Shorts", "🟣 Insta Reels", "⚫ TikTok", "🔵 FB Reels"])
    platforms = [
        ("YouTube Shorts", tab_yt),
        ("Instagram Reels", tab_ig),
        ("TikTok", tab_tt),
        ("Facebook Reels", tab_fb)
    ]

    for i, (platform_name, tab) in enumerate(platforms):
        with tab:
            st.markdown(f"<h3 style='margin-top: 15px; color: #e2e8f0;'>Optimize for {platform_name}</h3>", unsafe_allow_html=True)
            
            # Using unique keys for each uploader so they don't conflict
            uploaded_file = st.file_uploader(f"Drop your {platform_name} draft here (.mp4 or .mov)", type=["mp4", "mov"], key=f"uploader_{i}")

            if uploaded_file is not None:
                file_key = f"{uploaded_file.name}_{uploaded_file.size}_{platform_name}"
                temp_filename = f"temp_upload_{i}.mp4"
                
                # Check video constraints
                if f"file_verified_{i}" not in st.session_state or st.session_state[f"file_verified_{i}"] != file_key:
                    with open(temp_filename, "wb") as f: 
                        f.write(uploaded_file.getbuffer())
                    
                    video_analysis = VideoFileClip(temp_filename)
                    st.session_state[f"duration_{i}"] = video_analysis.duration
                    video_analysis.close() 
                    if os.path.exists(temp_filename): os.remove(temp_filename) 
                    st.session_state[f"file_verified_{i}"] = file_key

                duration_seconds = st.session_state[f"duration_{i}"]
                
                if duration_seconds > 120:
                    st.error(f"🚨 Operational Error: The target clip clocks at {int(duration_seconds)}s. Ensure limits remain below 2 minutes.")
                else:
                    st.success(f"✅ Infrastructure Verified: Validated {int(duration_seconds)}s for the {platform_name} algorithm. Framework primed.")
                    
                    if st.button(f"🚀 Execute {platform_name} Simulation", key=f"run_btn_{i}"):
                        progress_text = "Initiating Neural Connection..."
                        bar = st.progress(0, text=progress_text)
                        
                        def update_progress(val, text):
                            bar.progress(val, text=text)

                        max_retries = 3
                        retry_delay = 4
                        
                        for attempt in range(max_retries):
                            try:
                                update_progress(20, "Uploading Asset to Node...")
                                with open(temp_filename, "wb") as f: 
                                    f.write(uploaded_file.getbuffer())
                                
                                client = genai.Client(api_key=api_key)
                                uploaded_ai_file = client.files.upload(file=temp_filename)
                                
                                update_progress(50, "Calibrating Neural Matrices...")
                                while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                                    time.sleep(2)
                                    uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                                
                                update_progress(80, "Running Virality Audit...")
                                
                                # Highly specific dynamic prompt injection based on the active tab
                                system_prompt = f"""
                                You are an elite virality engineer and retention analyst for short-form video content.
                                Your objective is to audit this video specifically for the **{platform_name}** algorithm.
                                
                                Keep in mind {platform_name}'s unique audience behavior. For example, TikTok demands aggressive 1-second hooks, FB Reels skews slightly older and relatable, YT Shorts rewards continuous loops, and Insta Reels focuses heavily on aesthetic and trending audio.
                                
                                Break down the video into sections: 
                                1. {platform_name} Performance Grade (Out of 100)
                                2. 3-Second Hook Audit
                                3. Retention Drop-offs (Identify exact timestamp risks)
                                4. High-Impact Fixes to optimize specifically for {platform_name}
                                
                                Make recommendations direct, punchy, and highly technical.
                                """
                                
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash", 
                                    contents=[uploaded_ai_file, system_prompt]
                                )
                                
                                update_progress(100, "Audit Complete.")
                                st.session_state[f"dash_report_{i}"] = response.text
                                
                                # Generate simulation telemetry scores dynamically for the gauges
                                st.session_state[f"hook_score_{i}"] = round(random.uniform(7.5, 9.8), 1)
                                st.session_state[f"ret_score_{i}"] = round(random.uniform(6.5, 9.5), 1)
                                st.session_state[f"emo_score_{i}"] = round(random.uniform(7.0, 9.9), 1)
                                st.session_state[f"conv_score_{i}"] = round(random.uniform(6.0, 9.0), 1)
                                
                                try: 
                                    client.files.delete(name=uploaded_ai_file.name)
                                except: 
                                    pass
                                break
                            except APIError as e:
                                if "503" in str(e) or "UNAVAILABLE" in str(e):
                                    if attempt < max_retries - 1:
                                        st.warning(f"⚠️ Neural Node busy (503). Retrying in {retry_delay}s...")
                                        time.sleep(retry_delay); retry_delay *= 2
                                    else: 
                                        st.error("🚨 Cloud Architecture Overloaded. Please try re-running the simulation shortly.")
                                else: 
                                    st.error(f"API Error: {e}"); break
                            except Exception as error:
                                st.error(f"System Exception Encountered: {error}"); break
                            finally:
                                if os.path.exists(temp_filename): 
                                    os.remove(temp_filename)
                        
                        bar.empty() # Clear the bar when finished

            # =================================================================
            # 🚀 POST-SIMULATION LAYOUT BLOCK
            # =================================================================
            if f"dash_report_{i}" in st.session_state:
                st.divider()
                st.markdown(f"<h3 style='color: #a78bfa;'>🧠 {platform_name} Diagnostic Matrix</h3>", unsafe_allow_html=True)
                
                # Render the 4 animated metric gauges horizontally
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    render_circular_gauge(score=st.session_state[f"hook_score_{i}"], max_score=10, label="⚡ Hook", color="#00f2fe")
                with col2:
                    render_circular_gauge(score=st.session_state[f"ret_score_{i}"], max_score=10, label="⏱️ Retention", color="#d946ef")
                with col3:
                    render_circular_gauge(score=st.session_state[f"emo_score_{i}"], max_score=10, label="🔥 Emotional", color="#ff5e62")
                with col4:
                    render_circular_gauge(score=st.session_state[f"conv_score_{i}"], max_score=10, label="🎯 Conversion", color="#10b981")

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Render the deep AI textual breakdown below the gauges
                with st.container(border=True): 
                    st.markdown(st.session_state[f"dash_report_{i}"])

# ==========================================
# 6. INTERACTIVE HISTORICAL DATA REPOSITORY
# ==========================================
elif navigation == "📁 Saved Video History":
    st.markdown("<h1>📁 Secure Asset Retention Logs</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Search, review, filter, and extract analytical reports from previously processed short-form content models.</p>", unsafe_allow_html=True)
    st.divider()

    search_q = st.text_input("🔍 Search Historical Filenames", placeholder="Type a file keyword to filter data...")
    history_data = {
        "Project Filename": ["Cable Bill Hack.mp4", "Stop Wasting Money.mp4", "Easy Phone Trick.mp4"],
        "Execution Date": ["2026-06-18", "2026-06-17", "2026-06-16"],
        "Duration": ["56s", "48s", "35s"], "Retention Index": [91, 67, 84], "Platform Optimized": ["TikTok Pro", "YT Shorts", "Instagram Reels"]
    }
    df_history = pd.DataFrame(history_data)
    if search_q: df_history = df_history[df_history["Project Filename"].str.contains(search_q, case=False)]

    st.dataframe(df_history, use_container_width=True, hide_index=True, column_config={
        "Retention Index": st.column_config.ProgressColumn("Retention Index", min_value=0, max_value=100, format="%d pts"),
        "Project Filename": st.column_config.TextColumn("Target File Name"),
    })

# ==========================================
# 7. SUBSCRIPTION PLAN MODES
# ==========================================
elif navigation == "💎 Subscriptions & Pricing":
    st.markdown("<h1>💎 Premium Architecture Tiers</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Upgrade or scale infrastructure boundaries to suit agency rendering throughput requests.</p>", unsafe_allow_html=True)
    st.divider()

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        st.markdown("""<div style='background:#0f0f1a; border: 1px solid #1e1b4b; border-radius:16px; padding:24px; text-align:center;'><h3 style='color:#94a3b8;'>Starter Sandbox</h3><h2 style='font-size:36px; margin: 15px 0;'>$0 <span style='font-size:14px; color:gray;'>/ month</span></h2><hr style='border-color:#1e1b4b;'><p style='text-align:left;'>• 5 Basic Scans Monthly<br>• Max file duration 60s<br>• Core Processing Units</p><div style='margin-top:30px; padding:10px; background:#1e1b4b; border-radius:8px; color:gray; font-size:12px; font-weight:bold;'>INACTIVE IN WORKSPACE</div></div>""", unsafe_allow_html=True)
    with pc2:
        st.markdown("""<div style='background: linear-gradient(145deg, #180f2b 0%, #0f0f1a 100%); border: 2px solid #7c3aed; border-radius:16px; padding:24px; text-align:center; box-shadow: 0 0 25px rgba(124,58,237,0.25);'><h3 style='color:#a78bfa;'>Creator Studio Pro</h3><h2 style='font-size:36px; margin: 15px 0; color:#ffffff;'>$49 <span style='font-size:14px; color:#a78bfa;'>/ month</span></h2><hr style='border-color:#2e2a4f;'><p style='text-align:left; color:#e2e8f0;'>• Unlimited Video Engine Processing<br>• Max file duration 120s<br>• Priority Neural Grid Queue<br>• Custom Analytics Exports</p></div>""", unsafe_allow_html=True)
        st.write(""); st.button("✨ CURRENT WORKSPACE ACCOUNT TIER", disabled=True, use_container_width=True)
    with pc3:
        st.markdown("""<div style='background:#0f0f1a; border: 1px solid #1e1b4b; border-radius:16px; padding:24px; text-align:center;'><h3 style='color:#94a3b8;'>Production Scale</h3><h2 style='font-size:36px; margin: 15px 0;'>$199 <span style='font-size:14px; color:gray;'>/ month</span></h2><hr style='border-color:#1e1b4b;'><p style='text-align:left;'>• Unlimited Scans + Automation APIs<br>• Uncapped File Durations<br>• Dedicated AI Node Cluster access</p><div style='margin-top:30px;'></div></div>""", unsafe_allow_html=True)

