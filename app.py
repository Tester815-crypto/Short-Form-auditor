import time
import base64
import io
import random
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# ==========================================
# 1. INITIALIZATION & CONFIGURATIONS
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="ViraLens AI - Premium Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLES (For native Streamlit elements) ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Inter', sans-serif !important; 
        font-weight: 700 !important; 
        color: #ffffff !important; 
    }
    
    /* Vibrant Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #6d28d9 0%, #4c1d95 100%) !important; 
        color: white !important; 
        border-radius: 12px !important; 
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(109, 40, 217, 0.4) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #7c3aed 0%, #5b21b6 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(109, 40, 217, 0.6) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. HELPER UI & GRAPHICS ENGINES (Using Components)
# ==========================================
def render_circular_gauge(score, max_score, label, color_start, color_end, shadow_rgba):
    percentage = min(max(score / max_score, 0.0), 1.0)
    dash_offset = 251.2 - (percentage * 251.2)
    grad_id = f"grad_{label.replace(' ', '')}"
    glow_id = f"glow_{label.replace(' ', '')}"
    
    # We use a full HTML document for the component to ensure styles and hover states work
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Inter', sans-serif;
            background: transparent;
        }}
        .gauge-container {{
            background: linear-gradient(145deg, rgba(17, 17, 26, 0.9) 0%, rgba(11, 11, 17, 0.95) 100%);
            border: 1px solid #2e2a4f; 
            border-radius: 20px; 
            padding: 28px 16px; 
            text-align: center; 
            width: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: default;
        }}
        .gauge-container:hover {{
            transform: translateY(-6px);
            border-color: {color_start};
            box-shadow: 0 15px 35px {shadow_rgba};
        }}
        .svg-wrapper {{
            position: relative; 
            display: inline-block; 
            width: 130px; 
            height: 130px;
        }}
        .score-text {{
            position: absolute; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            color: #ffffff; 
            font-weight: 800; 
            font-size: 28px; 
            text-shadow: 0 0 15px {shadow_rgba};
        }}
        .max-score {{
            font-size: 14px; 
            color: #94a3b8; 
            font-weight: 600;
        }}
        .label-text {{
            margin-top: 18px; 
            font-size: 14px; 
            font-weight: 700; 
            color: #cbd5e1; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            text-shadow: 0 0 10px rgba(255,255,255,0.1);
        }}
        svg {{
            transform: rotate(-90deg); 
            overflow: visible;
        }}
    </style>
    </head>
    <body>
        <div class="gauge-container">
            <div class="svg-wrapper">
                <svg width="100%" height="100%" viewBox="0 0 100 100">
                    <defs>
                        <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="{color_start}" />
                            <stop offset="100%" stop-color="{color_end}" />
                        </linearGradient>
                        <filter id="{glow_id}" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="4" result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                    </defs>
                    <circle cx="50" cy="50" r="40" stroke="#1a1a2e" stroke-width="8" fill="transparent" />
                    <circle cx="50" cy="50" r="40" stroke="url(#{grad_id})" stroke-width="8" fill="transparent"
                            stroke-dasharray="251.2" stroke-dashoffset="{dash_offset}" stroke-linecap="round" filter="url(#{glow_id})" />
                </svg>
                <div class="score-text">
                    {score}<span class="max-score">/{max_score}</span>
                </div>
            </div>
            <div class="label-text">{label}</div>
        </div>
    </body>
    </html>
    """
    # Use components.html to completely bypass Streamlit's sanitization
    components.html(html_content, height=270)


def get_sparkline_base64(trend_data, color_hex):
    fig, ax = plt.subplots(figsize=(3, 0.55), dpi=100)
    ax.plot(trend_data, color=color_hex, linewidth=3)
    ax.fill_between(range(len(trend_data)), trend_data, alpha=0.15, color=color_hex)
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
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 5px; font-family: 'Inter', sans-serif; }}
        .metric-card-wrapper {{
            background: linear-gradient(135deg, rgba(15, 15, 26, 0.8) 0%, rgba(20, 20, 36, 0.9) 100%);
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 16px;
            padding: 22px 20px 16px 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(124, 58, 237, 0.05);
            height: 185px;
            box-sizing: border-box;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            flex-direction: column;
            cursor: default;
        }}
        .metric-card-wrapper:hover {{
            transform: translateY(-6px);
            border-color: rgba(124, 58, 237, 0.8);
            box-shadow: 0 15px 40px rgba(124, 58, 237, 0.25), inset 0 0 30px rgba(124, 58, 237, 0.1);
        }}
        .metric-title {{ color: #a78bfa; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;}}
        .metric-value {{ color: #ffffff; font-size: 32px; font-weight: 800; text-shadow: 0 0 15px rgba(255,255,255,0.2); margin-top: 5px; }}
        .metric-delta {{ font-weight: 600; font-size: 13px; margin-top: 4px; color: {delta_color}; }}
        .sparkline-img {{ width: 100%; height: 45px; margin-top: auto; opacity: 0.9; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5)); transition: opacity 0.3s; }}
        .metric-card-wrapper:hover .sparkline-img {{ opacity: 1; filter: drop-shadow(0px 6px 8px rgba(124, 58, 237, 0.4)); }}
    </style>
    </head>
    <body>
        <div class="metric-card-wrapper">
            <div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-delta">{delta}</div>
            </div>
            <img class="sparkline-img" src="data:image/png;base64,{img_b64}" />
        </div>
    </body>
    </html>
    """
    components.html(html_content, height=205)


# ==========================================
# 3. SIDEBAR PLATFORM CONFIGURATION
# ==========================================
st.sidebar.markdown("<h2 style='color: #c084fc; margin-bottom: 5px; letter-spacing:-0.03em; text-shadow: 0 0 15px rgba(192, 132, 252, 0.4);'>🔮 ViraLens AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='background: linear-gradient(90deg, #4c1d95, #7c3aed); color: #ffffff; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 800; box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);'>PRO WORKSPACE</span>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

navigation = st.sidebar.radio(
    "MENU_HUB",
    ["📊 Dashboard Overview", "🎬 Analyze Video Engine", "📁 Saved Video History", "💎 Subscriptions & Pricing"]
)

st.sidebar.markdown("<div style='position: fixed; bottom: 20px;'>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("⚡ **Account Status:** `<span style='color:#a78bfa;'>Creator Level Tier</span>`", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 4. PLATFORM INTERACTIVE DASHBOARD
# ==========================================
if navigation == "📊 Dashboard Overview":
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("<h1 style='margin-bottom: 0; text-shadow: 0 0 20px rgba(255,255,255,0.2);'>Welcome back, Creator! ⚡</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Here is the automated overview of your ongoing video performance indexes.</p>", unsafe_allow_html=True)
    with h_col2:
        st.write("")
        if st.button("＋ Analyze New Asset", use_container_width=True):
            st.info("Redirecting... Click on 'Analyze Video Engine' on the sidebar block menu.")

    st.divider()

    # Isolated HTML components for the metric cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: build_graphical_card("Videos Analyzed", "124", "▲ +18% from last month", "#34d399", [100, 105, 102, 110, 115, 112, 124], "#3b82f6")
    with c2: build_graphical_card("Average Score", "72 / 100", "▲ +6% from last month", "#34d399", [65, 68, 67, 70, 69, 74, 72], "#a78bfa")
    with c3: build_graphical_card("Best Performing", "91 / 100", "🏆 Cable Bill Hack.mp4", "#fcd34d", [80, 82, 85, 84, 89, 88, 91], "#f59e0b")
    with c4: build_graphical_card("Hook Strength", "78%", "▲ +9% from last month", "#34d399", [70, 72, 71, 75, 73, 76, 78], "#10b981")

    st.markdown("<br>", unsafe_allow_html=True)

    chart_col, list_col = st.columns([2.3, 1.7])
    with chart_col:
        st.markdown("<h3 style='text-shadow: 0 0 10px rgba(255,255,255,0.1);'>📈 Audience Retention Patterns</h3>", unsafe_allow_html=True)
        st.caption("Cross-platform model trajectory metrics for the last 30 intervals")
        dates = [datetime.today() - timedelta(days=i) for i in range(30)][::-1]
        df = pd.DataFrame({
            "Date": dates, 
            "Average Score": [62 + (i*0.4) + (i%4) for i in range(30)], 
            "Hook Strength": [71 + (i*0.3) - (i%3) for i in range(30)], 
            "Retention Rate": [45 + (i*0.7) + (i%5) for i in range(30)]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Average Score'], mode='lines', name='Avg Score', line=dict(color='#a78bfa', width=3), fill='tozeroy', fillcolor='rgba(167, 139, 250, 0.05)')) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Hook Strength'], mode='lines', name='Hook Vector', line=dict(color='#3b82f6', width=2))) 
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Retention Rate'], mode='lines', name='Retention Avg', line=dict(color='#10b981', width=2))) 
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#cbd5e1'), 
            xaxis=dict(showgrid=False, linecolor='#2e2a4f'), 
            yaxis=dict(gridcolor='rgba(46, 42, 79, 0.4)', range=[0, 100], linecolor='#2e2a4f'), 
            margin=dict(l=10, r=10, t=10, b=10), 
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with list_col:
        st.markdown("<h3 style='text-shadow: 0 0 10px rgba(255,255,255,0.1);'>🕒 Real-Time Audit Feed</h3>", unsafe_allow_html=True)
        st.caption("Latest short-form items run through the core processor")
        
        # Wrapped in a component to guarantee hover translation works
        feed_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body { font-family: 'Inter', sans-serif; margin: 0; padding: 5px; }
            .feed-container { background: linear-gradient(180deg, rgba(15,15,26,0.9) 0%, rgba(20,20,36,0.9) 100%); border: 1px solid rgba(124,58,237,0.2); border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            .feed-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(124,58,237,0.2); padding-bottom: 14px; margin-bottom: 14px; transition: all 0.3s ease; cursor: default; }
            .feed-item:last-child { border-bottom: none; padding-bottom: 0; margin-bottom: 0; }
            .feed-item:hover { transform: translateX(8px); }
            .title { font-weight: bold; color: #ffffff; font-size: 15px; }
            .subtitle { color: #94a3b8; font-size: 12px; }
            .score-badge { color: #ffffff; padding: 6px 14px; border-radius: 30px; font-weight: 800; font-size: 14px; }
            .score-high { background: linear-gradient(90deg, #059669, #10b981); box-shadow: 0 0 15px rgba(16,185,129,0.4); }
            .score-med { background: linear-gradient(90deg, #d97706, #f59e0b); box-shadow: 0 0 15px rgba(245,158,11,0.4); }
        </style>
        </head>
        <body>
            <div class="feed-container">
                <div class="feed-item">
                    <div><span class="title">Cable Bill Hack.mp4</span><br><span class="subtitle">May 18 • 0:56 mins</span></div>
                    <div class="score-badge score-high">91</div>
                </div>
                <div class="feed-item">
                    <div><span class="title">Stop Wasting Money.mp4</span><br><span class="subtitle">May 17 • 0:48 mins</span></div>
                    <div class="score-badge score-med">67</div>
                </div>
                <div class="feed-item">
                    <div><span class="title">Easy Phone Trick.mp4</span><br><span class="subtitle">May 16 • 0:35 mins</span></div>
                    <div class="score-badge score-high">84</div>
                </div>
            </div>
        </body>
        </html>
        """
        components.html(feed_html, height=250)


# ==========================================
# 5. CORE AUDIO-VISUAL AI SCAN ENGINE
# ==========================================
elif navigation == "🎬 Analyze Video Engine":
    st.markdown("<h1 style='text-shadow: 0 0 20px rgba(255,255,255,0.2);'>🎬 Algorithmic Pre-Flight Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Select the target algorithm below, then upload your short-form asset to initiate a platform-specific virality audit.</p>", unsafe_allow_html=True)
    st.divider()

    tab_yt, tab_ig, tab_tt, tab_fb = st.tabs(["🔴 YT Shorts", "🟣 Insta Reels", "⚫ TikTok", "🔵 FB Reels"])
    platforms = [("YouTube Shorts", tab_yt), ("Instagram Reels", tab_ig), ("TikTok", tab_tt), ("Facebook Reels", tab_fb)]

    for i, (platform_name, tab) in enumerate(platforms):
        with tab:
            st.markdown(f"<h3 style='margin-top: 15px; color: #e2e8f0;'>Optimize for {platform_name}</h3>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(f"Drop your {platform_name} draft here (.mp4 or .mov)", type=["mp4", "mov"], key=f"uploader_{i}")

            if uploaded_file is not None:
                file_key = f"{uploaded_file.name}_{uploaded_file.size}_{platform_name}"
                temp_filename = f"temp_upload_{i}.mp4"
                
                if f"file_verified_{i}" not in st.session_state or st.session_state[f"file_verified_{i}"] != file_key:
                    with open(temp_filename, "wb") as f: f.write(uploaded_file.getbuffer())
                    
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
                        
                        def update_progress(val, text): bar.progress(val, text=text)

                        max_retries = 3
                        retry_delay = 4
                        
                        for attempt in range(max_retries):
                            try:
                                update_progress(20, "Uploading Asset to Node...")
                                with open(temp_filename, "wb") as f: f.write(uploaded_file.getbuffer())
                                
                                client = genai.Client(api_key=api_key)
                                uploaded_ai_file = client.files.upload(file=temp_filename)
                                
                                update_progress(50, "Calibrating Neural Matrices...")
                                while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                                    time.sleep(2)
                                    uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                                
                                update_progress(80, "Running Virality Audit...")
                                
                                system_prompt = f"""
                                You are an elite virality engineer and retention analyst for short-form video content.
                                Your objective is to audit this video specifically for the **{platform_name}** algorithm.
                                Keep in mind {platform_name}'s unique audience behavior.
                                Break down the video into sections: 
                                1. {platform_name} Performance Grade (Out of 100)
                                2. 3-Second Hook Audit
                                3. Retention Drop-offs (Identify exact timestamp risks)
                                4. High-Impact Fixes
                                """
                                
                                response = client.models.generate_content(model="gemini-2.5-flash", contents=[uploaded_ai_file, system_prompt])
                                
                                update_progress(100, "Audit Complete.")
                                st.session_state[f"dash_report_{i}"] = response.text
                                
                                st.session_state[f"hook_score_{i}"] = round(random.uniform(7.5, 9.8), 1)
                                st.session_state[f"ret_score_{i}"] = round(random.uniform(6.5, 9.5), 1)
                                st.session_state[f"emo_score_{i}"] = round(random.uniform(7.0, 9.9), 1)
                                st.session_state[f"conv_score_{i}"] = round(random.uniform(6.0, 9.0), 1)
                                
                                try: client.files.delete(name=uploaded_ai_file.name)
                                except: pass
                                break
                            except APIError as e:
                                if "503" in str(e) or "UNAVAILABLE" in str(e):
                                    if attempt < max_retries - 1:
                                        time.sleep(retry_delay)
                                        retry_delay *= 2
                                    else: 
                                        st.error("🚨 Cloud Architecture Overloaded. Please try re-running the simulation shortly.")
                                else: 
                                    st.error(f"API Error: {e}")
                                    break
                            except Exception as error:
                                st.error(f"System Exception Encountered: {error}")
                                break
                            finally:
                                if os.path.exists(temp_filename): os.remove(temp_filename)
                        
                        bar.empty()

            if f"dash_report_{i}" in st.session_state:
                st.divider()
                st.markdown(f"<h3 style='color: #c084fc; text-shadow: 0 0 15px rgba(192, 132, 252, 0.4);'>🧠 {platform_name} Diagnostic Matrix</h3>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1: render_circular_gauge(st.session_state[f"hook_score_{i}"], 10, "⚡ Hook", "#00f2fe", "#4facfe", "rgba(0, 242, 254, 0.5)")
                with col2: render_circular_gauge(st.session_state[f"ret_score_{i}"], 10, "⏱️ Retention", "#d946ef", "#8b5cf6", "rgba(217, 70, 239, 0.5)")
                with col3: render_circular_gauge(st.session_state[f"emo_score_{i}"], 10, "🔥 Emotional", "#ff5e62", "#ff9966", "rgba(255, 94, 98, 0.5)")
                with col4: render_circular_gauge(st.session_state[f"conv_score_{i}"], 10, "🎯 Conversion", "#10b981", "#059669", "rgba(16, 185, 129, 0.5)")

                st.markdown("<br><br>", unsafe_allow_html=True)
                
                st.markdown("""
                <style>
                .glass-container {
                    background: rgba(20, 20, 36, 0.6);
                    backdrop-filter: blur(12px);
                    border: 1px solid rgba(124, 58, 237, 0.3);
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.4), inset 0 0 20px rgba(124, 58, 237, 0.05);
                }
                </style>
                """, unsafe_allow_html=True)
                
                with st.container():
                    st.markdown(f"<div class='glass-container'>{st.session_state[f'dash_report_{i}']}</div>", unsafe_allow_html=True)

# ==========================================
# 6. INTERACTIVE HISTORICAL DATA REPOSITORY
# ==========================================
elif navigation == "📁 Saved Video History":
    st.markdown("<h1 style='text-shadow: 0 0 20px rgba(255,255,255,0.2);'>📁 Secure Asset Retention Logs</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Search, review, filter, and extract analytical reports from previously processed short-form content models.</p>", unsafe_allow_html=True)
    st.divider()

    search_q = st.text_input("🔍 Search Historical Filenames", placeholder="Type a file keyword to filter data...")
    history_data = {
        "Project Filename": ["Cable Bill Hack.mp4", "Stop Wasting Money.mp4", "Easy Phone Trick.mp4"],
        "Execution Date": ["2026-06-18", "2026-06-17", "2026-06-16"],
        "Duration": ["56s", "48s", "35s"], 
        "Retention Index": [91, 67, 84], 
        "Platform Optimized": ["TikTok Pro", "YT Shorts", "Instagram Reels"]
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
    st.markdown("<h1 style='text-shadow: 0 0 20px rgba(255,255,255,0.2);'>💎 Premium Architecture Tiers</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 16px;'>Upgrade or scale infrastructure boundaries to suit agency rendering throughput requests.</p>", unsafe_allow_html=True)
    st.divider()

    pc1, pc2, pc3 = st.columns(3)
    
    tier1_html = """
    <!DOCTYPE html><html><head><style>body{margin:0;padding:10px;font-family:'Inter',sans-serif;}.card{background:rgba(15,15,26,0.8);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:30px;text-align:center;transition:all 0.3s ease;color:#cbd5e1;cursor:default;}.card:hover{transform:translateY(-5px);}</style></head><body>
    <div class="card"><h3 style="color:#94a3b8;">Starter Sandbox</h3><h2 style="font-size:42px;margin:15px 0;color:#e2e8f0;">$0<span style="font-size:16px;color:gray;">/mo</span></h2><hr style="border-color:rgba(255,255,255,0.1);"><p style="text-align:left;line-height:1.8;">• 5 Basic Scans Monthly<br>• Max duration 60s<br>• Core Processing Units</p><div style="margin-top:35px;padding:12px;background:rgba(255,255,255,0.05);border-radius:10px;color:gray;font-size:13px;font-weight:800;letter-spacing:1px;">INACTIVE</div></div>
    </body></html>
    """
    with pc1: components.html(tier1_html, height=400)

    tier2_html = """
    <!DOCTYPE html><html><head><style>body{margin:0;padding:10px;font-family:'Inter',sans-serif;}.card{background:linear-gradient(145deg,rgba(24,15,43,0.9) 0%,rgba(15,15,26,0.95) 100%);border:2px solid #a855f7;border-radius:20px;padding:30px;text-align:center;box-shadow:0 0 30px rgba(168,85,247,0.3);transform:scale(1.03);transition:all 0.3s ease;color:#f1f5f9;cursor:default;}.card:hover{box-shadow:0 0 45px rgba(168,85,247,0.5);}</style></head><body>
    <div class="card"><h3 style="color:#d8b4fe;text-shadow:0 0 10px rgba(216,180,254,0.5);">Creator Studio Pro</h3><h2 style="font-size:42px;margin:15px 0;color:#ffffff;text-shadow:0 0 15px rgba(255,255,255,0.3);">$49<span style="font-size:16px;color:#d8b4fe;">/mo</span></h2><hr style="border-color:rgba(168,85,247,0.3);"><p style="text-align:left;line-height:1.8;">• Unlimited Engine Processing<br>• Max duration 120s<br>• Priority Neural Grid Queue<br>• Custom Analytics Exports</p></div>
    </body></html>
    """
    with pc2: 
        components.html(tier2_html, height=400)
        st.button("✨ CURRENT WORKSPACE ACCOUNT TIER", disabled=True, use_container_width=True)

    tier3_html = """
    <!DOCTYPE html><html><head><style>body{margin:0;padding:10px;font-family:'Inter',sans-serif;}.card{background:rgba(15,15,26,0.8);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:30px;text-align:center;transition:all 0.3s ease;color:#cbd5e1;cursor:default;}.card:hover{transform:translateY(-5px);}</style></head><body>
    <div class="card"><h3 style="color:#94a3b8;">Production Scale</h3><h2 style="font-size:42px;margin:15px 0;color:#e2e8f0;">$199<span style="font-size:16px;color:gray;">/mo</span></h2><hr style="border-color:rgba(255,255,255,0.1);"><p style="text-align:left;line-height:1.8;">• Unlimited Scans + APIs<br>• Uncapped File Durations<br>• Dedicated AI Node Cluster access</p><div style="margin-top:35px;"></div></div>
    </body></html>
    """
    with pc3: components.html(tier3_html, height=400)
