import streamlit as st
import os
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from moviepy import VideoFileClip
from google import genai
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure Layout (MUST BE FIRST)
st.set_page_config(page_title="ViralScan AI", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# CUSTOM CSS: THE DEEP BLACK & PURPLE THEME
# ==========================================
st.markdown("""
    <style>
    /* Main Backgrounds */
    .stApp {
        background-color: #0b0b10;
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] {
        background-color: #12121a;
        border-right: 1px solid #1f1f2e;
    }
    /* Headers and Text */
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    p { color: #a0a0b0; }
    
    /* Style the Metric Cards */
    [data-testid="stMetric"] {
        background-color: #161622;
        border: 1px solid #2a2a3d;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 32px !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] svg { fill: #00ffcc; } /* Neon green for positive trends */
    
    /* Primary Buttons (The Purple Accent) */
    .stButton>button {
        background-color: #7b2cbf !important; /* Deep Purple */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #9d4edd !important; /* Lighter Purple on hover */
        box-shadow: 0 0 15px rgba(123, 44, 191, 0.5);
    }
    
    /* Containers / Divs */
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent;
    }
    .css-1r6slb0 { border-color: #2a2a3d; } /* Dividers */
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("<h2 style='color: #9d4edd;'>▶️ ViralScan AI</h2>", unsafe_allow_html=True)
st.sidebar.caption("Workspace: Professional Plan")
st.sidebar.divider()

navigation = st.sidebar.radio(
    "",
    ["🏠 Dashboard", "☁️ Analyze Video", "▶️ Video History", "💎 Pricing", "⚙️ Settings", "👤 Profile"]
)

st.sidebar.divider()
st.sidebar.markdown("👤 **Robert Fox**")

# ==========================================
# PAGE 1: PREMIUM DASHBOARD
# ==========================================
if navigation == "🏠 Dashboard":
    # Top Header Row
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.markdown("<h1 style='font-size: 2.2rem;'>Welcome back, Robert! 👋</h1>", unsafe_allow_html=True)
        st.write("Here's an overview of your video performance.")
    with header_col2:
        st.write("") # Spacing
        if st.button("＋ Analyze New Video", use_container_width=True):
            st.info("Navigate to 'Analyze Video' on the left to start a new scan!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="📹 Videos Analyzed", value="124", delta="↑ 18% from last month")
    with m2:
        st.metric(label="⭐ Average Score", value="72 / 100", delta="↑ 6% from last month")
    with m3:
        st.metric(label="🏆 Best Performing", value="91 / 100", delta="Cable Bill Hack.mp4", delta_color="off")
    with m4:
        st.metric(label="🪝 Hook Strength", value="78 / 100", delta="↑ 9% from last month")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart & Recent Videos Row
    chart_col, list_col = st.columns([2.5, 1.5])
    
    with chart_col:
        st.markdown("### 📈 Performance Overview")
        st.caption("Average metrics over the last 30 days")
        
        # Generate Dummy Data for the Chart to make it look alive
        dates = [datetime.today() - timedelta(days=i) for i in range(30)][::-1]
        df = pd.DataFrame({
            "Date": dates,
            "Average Score": [60 + (i*0.5) + (i%5) for i in range(30)],
            "Hook Strength": [70 + (i*0.6) - (i%3) for i in range(30)],
            "Retention": [40 + (i*0.8) + (i%4) for i in range(30)]
        })
        
        # Build the Plotly Dark Theme Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Average Score'], mode='lines', name='Avg Score', line=dict(color='#3b82f6', width=3))) # Blue
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Hook Strength'], mode='lines', name='Hook Strength', line=dict(color='#ef4444', width=3))) # Red/Pink
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Retention'], mode='lines', name='Retention', line=dict(color='#10b981', width=3))) # Green
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a0a0b0'),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#2a2a3d', range=[0, 100]),
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with list_col:
        st.markdown("### 🕒 Recent Analyzed")
        st.caption("Your latest content scans")
        
        # Mock List of recent videos
        with st.container(border=True):
            st.markdown("""
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2a3d; padding-bottom: 10px; margin-bottom: 10px;'>
                <div><strong>Cable Bill Hack.mp4</strong><br><span style='color:gray; font-size:12px;'>May 18 • 0:56</span></div>
                <div style='background-color:#059669; color:white; padding: 5px 10px; border-radius: 20px; font-weight: bold;'>91</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2a3d; padding-bottom: 10px; margin-bottom: 10px;'>
                <div><strong>Stop Wasting Money.mp4</strong><br><span style='color:gray; font-size:12px;'>May 17 • 0:48</span></div>
                <div style='background-color:#ca8a04; color:white; padding: 5px 10px; border-radius: 20px; font-weight: bold;'>67</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2a3d; padding-bottom: 10px; margin-bottom: 10px;'>
                <div><strong>Easy Phone Trick.mp4</strong><br><span style='color:gray; font-size:12px;'>May 16 • 0:35</span></div>
                <div style='background-color:#059669; color:white; padding: 5px 10px; border-radius: 20px; font-weight: bold;'>84</div>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div><strong>Hidden Features.mp4</strong><br><span style='color:gray; font-size:12px;'>May 15 • 0:42</span></div>
                <div style='background-color:#dc2626; color:white; padding: 5px 10px; border-radius: 20px; font-weight: bold;'>45</div>
            </div>
            """, unsafe_allow_html=True)

    # Bottom CTA Box
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        cta_c1, cta_c2, cta_c3 = st.columns([1.5, 1, 1])
        with cta_c1:
            st.markdown("### 🚀 Ready to analyze a new video?")
            st.write("Upload your video (MP4 or MOV, under 2 minutes) to get started.")
        with cta_c2:
            st.write("") # spacing
            if st.button("📤 Upload Video Now", use_container_width=True):
                 st.info("Navigate to 'Analyze Video' on the left to start!")
        with cta_c3:
            st.markdown("✨ **AI-Powered Analysis**<br>⚡ **Actionable Insights**", unsafe_allow_html=True)

# ==========================================
# PAGE 2: ANALYZE VIDEO (Your AI Engine)
# ==========================================
elif navigation == "☁️ Analyze Video":
    st.title("☁️ Neural Engine Scanner")
    st.write("Upload your Short, Reel, or TikTok to scan its hook metrics and virality potential.")

    uploaded_file = st.file_uploader("Drop your video file here (.mp4 or .mov)", type=["mp4", "mov"])

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
            st.error(f"🚨 Video is {int(duration_seconds)} seconds. Please keep it under 2 minutes.")
        else:
            st.success(f"✅ Duration verified ({int(duration_seconds)}s). Ready to simulate.")
            
            if st.button("⚡ Run Deep-Scan Analysis"):
                with st.spinner("Initializing neural models and analyzing frames..."):
                    try:
                        with open(temp_filename, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        client = genai.Client(api_key=api_key)
                        uploaded_ai_file = client.files.upload(file=temp_filename)
                        
                        while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                            time.sleep(2)
                            uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                        
                        system_prompt = """
                        You are a professional, ruthless short-form video retention auditor. 
                        Analyze the uploaded video's audio and visual tracks frame-by-frame. Format your response into these clean sections using markdown headers:
                        
                        ## 📊 Algorithmic Performance Grade
                        Give a final evaluation score out of 100 based strictly on whether this content can break the '200-view jail'. Explain the rating.
                        
                        ## 🪝 The 3-Second Hook Audit
                        Analyze the first 3 seconds visually and audibly. Did the creator introduce an immediate curiosity gap or conflict?
                        
                        ## 📉 Predicted Retention Drop-offs
                        Pinpoint specific timestamps where viewers are highly likely to swipe away.
                        
                        ## 🛠️ High-Impact Fixes
                        Provide 3 concrete, actionable changes to increase retention.
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
                        st.error(f"Error: {error}")
                    finally:
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)

            if "dash_report" in st.session_state:
                st.markdown("---")
                st.markdown("<h2 style='color: #9d4edd;'>🧠 Diagnostic Report Output</h2>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown(st.session_state.dash_report)

# ==========================================
# PLACEHOLDERS
# ==========================================
else:
    st.title(navigation)
    st.write("This section is under construction for the Professional Plan.")
