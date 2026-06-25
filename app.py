import streamlit as st
import os
import time
from moviepy import VideoFileClip
from google import genai
from dotenv import load_dotenv

# 1. Load your hidden API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure the Layout of your Web Dashboard
st.set_page_config(page_title="Algorithmic Pre-Flight Simulator", layout="wide")
st.title("🎬 Algorithmic Pre-Flight Short-Form Simulator")
st.write("Upload your completed Short, Reel, or TikTok under 2 minutes to scan its hook metrics and virality potential.")

# Create the visual drag-and-drop box
uploaded_file = st.file_uploader("Drop your video file here (.mp4 or .mov)", type=["mp4", "mov"])

if uploaded_file is not None:
    # Save the file temporarily to your drive so moviepy can check its runtime
    temp_filename = "user_upload_temp.mp4"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.read())
    
    # 3. Read Video Length Metadata
    video_analysis = VideoFileClip(temp_filename)
    duration_seconds = video_analysis.duration
    video_analysis.close() 
    
    if duration_seconds > 120:
        st.error(f"🚨 Video Length Restriction: Your video is {int(duration_seconds)} seconds long. Please keep it under 2 minutes (120 seconds).")
        os.remove(temp_filename) 
    else:
        st.success(f"✅ Video duration verified ({int(duration_seconds)}s). Ready to simulate audience engagement.")
        
        # When user clicks the analyze button
        if st.button("🚀 Run Virality Simulation"):
            with st.spinner("Uploading assets and running frame-by-frame algorithmic check..."):
                try:
                    # Connect to the official Google SDK client
                    client = genai.Client(api_key=api_key)
                    
                    # Upload the file to Google's temporary processing pool
                    uploaded_ai_file = client.files.upload(file=temp_filename)
                    
                    # Give the file a moment to process on Google's servers
                    while not uploaded_ai_file.state or uploaded_ai_file.state.name != "ACTIVE":
                        time.sleep(2)
                        uploaded_ai_file = client.files.get(name=uploaded_ai_file.name)
                    
                    # 4. The Social Media Retention Auditor Persona Prompt
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
                    
                    # Trigger the analysis request via the ultra-fast gemini-2.5-flash model
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[uploaded_ai_file, system_prompt]
                    )
                   # Extract the raw text response
                    full_report = response.text
                    
                    # Smart logic to find the score and display it in a premium widget
                    score_value = "Analyze Video"
                    for line in full_report.split("\n"):
                        if "Score:" in line or "90/100" in line or "88/100" in line:
                            score_value = line.replace("Score:", "").replace("**", "").strip()
                            break

                    # Main Dashboard Container
                    with st.container(border=True):
                        st.markdown("## ⚡ Algorithmic Virality Dashboard")
                        st.caption("Real-time behavioral, pacing, and retention diagnostics.")
                        st.divider()
                        
                        # Top KPI Analytics Row
                        kpi1, kpi2, kpi3 = st.columns(3)
                        with kpi1:
                            st.metric(label="🎯 Predicted Retention Grade", value=score_value)
                        with kpi2:
                            st.metric(label="⏱️ Video Processing", value="Verified Live")
                        with kpi3:
                            st.metric(label="🧠 Audit Engine", value="Gemini Pro AI")
                            
                        st.divider()
                        
                        # Interactive UI Navigation Tabs
                        tab_analysis, tab_export = st.tabs(["📋 Detailed Retention Audit", "💾 Export & Next Steps"])
                        
                        with tab_analysis:
                            # Render the main AI report beautifully inside this tab
                            st.markdown(full_report)
                            
                        with tab_export:
                            st.info("💡 **Agency Best Practice:** Apply these high-impact edits directly to your video editing timeline, re-export the file, and run it back through the simulator to verify your retention score increase.")
                            
                            # Give the user a premium product utility feature: A download button
                            st.download_button(
                                label="📥 Download PDF-Ready Audit Report (.txt)",
                                data=full_report,
                                file_name="virality_retention_report.txt",
                                mime="text/plain"
                            )
                    
                except Exception as error:
                    st.error(f"An processing error occurred: {error}")
                finally:
                    # Clean up the file out of your local desktop folder
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
