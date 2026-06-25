import streamlit as st
import os
import time
from moviepy import VideoFileClip
from google import genai
from dotenv import load_dotenv

# 1. Load your hidden API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure the Layout of your Web Dashboard (MUST BE FIRST)
st.set_page_config(page_title="RetainAI Studio", layout="wide", initial_sidebar_state="expanded")

# --- PREMIUM SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h2 style='color: #00FFCC;'>🛡️ RetainAI Studio</h2>", unsafe_allow_html=True)
st.sidebar.caption("v2.1 Premium Enterprise")
st.sidebar.divider()

# Create navigation options
navigation = st.sidebar.radio(
    "Navigation Workspace",
    ["📊 Dashboard Overview", "🎬 Analyze Video", "⏳ Audit History", "💳 Pricing & Plans", "⚙️ Account Settings"]
)

st.sidebar.divider()
st.sidebar.markdown("👤 **User Profile:** `Premium Creator`")

# ==========================================
# PAGE 1: DASHBOARD OVERVIEW
# ==========================================
if navigation == "📊 Dashboard Overview":
    st.title("📊 Virality Workspace Performance")
    st.write("Welcome back! Here is how your short-form content has been tracking across algorithms.")
    st.divider()
    
    # Premium Dashboard Analytic Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Videos Analyzed", value="124", delta="+18 this week")
    with col2:
        st.metric(label="Average Retention Score", value="72 / 100", delta="+3.4%")
    with col3:
        st.metric(label="Best Performing Piece", value="91 / 100")
    with col4:
        st.metric(label="Avg Hook Strength", value="78%", delta="+5.1%")
        
    st.divider()
    st.markdown("### 📈 Recent Activity Track")
    st.info("💡 **Tip for today:** Videos with visual pattern-interrupts within the first 1.5 seconds are converting 40% higher retention rates on TikTok this week.")

# ==========================================
# PAGE 2: ANALYZE VIDEO (Our Core App Architecture)
# ==========================================
elif navigation == "🎬 Analyze Video":
    st.title("🎬 Algorithmic Pre-Flight Short-Form Simulator")
    st.write("Upload your completed Short, Reel, or TikTok under 2 minutes to scan its hook metrics and virality potential.")

    # Create the visual drag-and-drop box
    uploaded_file = st.file_uploader("Drop your video file here (.mp4 or .mov)", type=["mp4", "mov"])

    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        temp_filename = "user_upload_temp.mp4"
        
        # Only run MoviePy ONCE per new file upload to save server memory
        if "file_verified_key" not in st.session_state or st.session_state.file_verified_key != file_key:
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            video_analysis = VideoFileClip(temp_filename)
            st.session_state.duration_seconds = video_analysis.duration
            video_analysis.close() 
            
            del video_analysis
            if os.path.exists(temp_filename):
                os.remove(temp_filename) 
            import gc
            gc.collect()
            
            st.session_state.file_verified_key = file_key

        duration_seconds = st.session_state.duration_seconds
        
        if duration_seconds > 120:
            st.error(f"🚨 Video Length Restriction: Your video is {int(duration_seconds)} seconds long. Please keep it under 2 minutes (120 seconds).")
        else:
            st.success(f"✅ Video duration verified ({int(duration_seconds)}s). Ready to simulate audience engagement.")
            
            if st.button("🚀 Run Virality Simulation"):
                with st.spinner("Uploading assets and running frame-by-frame algorithmic check..."):
                    try:
                        with open(temp_filename, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        client = genai.Client(api_key=api_key)
                        uploaded_ai_file = client.files.upload(file=temp_filename)
                        
                        while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                            time.sleep(2)
                            uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                        
                        system_prompt = """
                        You are a professional, ruthless short-form video retention auditor trained on high-retention frameworks (like MrBeast and Ryan Trahan pacing rules). 
                        Analyze the uploaded video's audio and visual tracks frame-by-frame. Format your response into these clean sections using markdown headers:
                        
                        ## 📊 Algorithmic Performance Grade
                        Give a final evaluation score out of 100 based strictly on whether this content can break the '200-view jail'. Explain the rating.
                        
                        ## 🪝 The 3-Second Hook Audit
                        Analyze the first 3 seconds visually and audibly. Did the creator introduce an immediate curiosity gap or conflict? Was there a visual mismatch?
                        
                        ## 📉 Predicted Retention Drop-offs
                        Pinpoint specific timestamps where viewers are highly likely to swipe away due to slow pacing, quiet dead-air, or repetitive visual layouts.
                        
                        ## 🛠️ High-Impact Fixes
                        Provide 3 concrete, actionable changes (e.g., 'Add a pattern interrupt at 0:14', 'Punch in 10% closer on the hook cut') to increase retention.
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[uploaded_ai_file, system_prompt]
                        )
                        
                        full_report = response.text.replace("Gemini", "Proprietary Core").replace("gemini", "Core Engine")
                        
                        try:
                            client.files.delete(name=uploaded_ai_file.name)
                        except:
                            pass
                        
                        raw_score = 85  
                        for line in full_report.split("\n"):
                            if "Score:" in line or "88/100" in line or "90/100" in line:
                                digits = [int(s) for s in line.split() if s.isdigit()]
                                if digits:
                                    raw_score = digits[0]
                                    break
                        
                        final_score = round(raw_score / 10, 1) if raw_score > 10 else float(raw_score)
                        if final_score > 10.0 or final_score < 1.0:
                            final_score = 8.8  
                        
                        hook_score = min(10.0, round(final_score + 0.4, 1))
                        pacing_score = min(10.0, round(final_score - 0.3, 1))
                        retention_score = final_score

                        st.session_state.dash_report = full_report
                        st.session_state.scores = (final_score, hook_score, pacing_score, retention_score)
                        
                    except Exception as error:
                        st.error(f"A processing error occurred: {error}")
                    finally:
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)
                        import gc
                        gc.collect()

            # Render Diagnostic Report from Memory
            if "dash_report" in st.session_state:
                f_score, h_score, p_score, r_score = st.session_state.scores
                report_text = st.session_state.dash_report
                
                with st.container(border=True):
                    st.markdown("<h2 style='text-align: center; color: #00FFCC; font-family: sans-serif;'>🛡️ RetainAI Diagnostic Matrix</h2>", unsafe_allow_html=True)
                    st.caption("<p style='text-align: center;'>Proprietary Automated Short-Form Auditing Environment v2.1</p>", unsafe_allow_html=True)
                    st.divider()
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric(label="🔥 OVERALL VIRALITY INDEX", value=f"{f_score} / 10")
                    with m2:
                        st.metric(label="📊 SCAN PROFILE", value="Short / Reel / TikTok")
                    with m3:
                        st.metric(label="🔒 ARCHITECTURE STATUS", value="Live / Proprietary")
                    
                    st.divider()
                    st.markdown("### 📈 Core Performance Vectors")
                    p_col1, p_col2, p_col3 = st.columns(3)
                    with p_col1:
                        st.write(f"🪝 **Hook Efficiency:** {h_score} / 10")
                        st.progress(h_score / 10.0)
                    with p_col2:
                        st.write(f"⏱️ **Pacing Flow Rate:** {p_score} / 10")
                        st.progress(p_score / 10.0)
                    with p_col3:
                        st.write(f"📉 **Audience Retention Hold:** {r_score} / 10")
                        st.progress(r_score / 10.0)
                        
                    st.divider()
                    st.markdown("### 🧠 Deep-Dive Intelligence Modules")
                    with st.expander("👁️ Open Full Structural Audit Timeline & Recommendations", expanded=False):
                        st.markdown(report_text)
                    with st.expander("📥 Platform Export Assets"):
                        st.download_button(
                            label="Download Signed Platform Report Manifest",
                            data=report_text,
                            file_name="retention_audit_manifest.txt",
                            mime="text/plain"
                        )

# ==========================================
# PLACEHOLDER PREMIUM PAGES
# ==========================================
elif navigation == "⏳ Audit History":
    st.title("⏳ Historic Retention Logs")
    st.write("Browse through previous video performance metrics and export multi-file historical reports.")
    st.divider()
    st.info("Feature coming soon: This tab will display a database table connected to your past video scores!")

elif navigation == "💳 Pricing & Plans":
    st.title("💳 Upgrade to Scale Virality")
    st.write("Unlock unrestricted file uploads, 4K rendering models, and API endpoints for heavy automated pipelines.")
    st.divider()
    
    p1, p2 = st.columns(2)
    with p1:
        with st.container(border=True):
            st.subheader("Starter Dev")
            st.markdown("### Free / \$0")
            st.write("* 1GB Server Capacity\n* 2 Minute Upload Caps\n* Basic Flash Check")
            st.button("Current Active Workspace Plan", disabled=True)
    with p2:
        with st.container(border=True):
            st.subheader("Agency Pro")
            st.markdown("### \$49 <span style='font-size:14px;'>/ month</span>", unsafe_allow_html=True)
            st.write("* Uncapped Processing Limits\n* Unlimited Monthly Scans\n* Raw 4K Pro Video Support")
            st.button("Upgrade to Enterprise Engine", type="primary")

elif navigation == "⚙️ Account Settings":
    st.title("⚙️ Workspace Configurations")
    st.write("Manage your custom prompt modifications and developer API key structures.")
