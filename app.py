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
                    
                    st.divider()
                    st.markdown(response.text)
                    
                    # Clean up file out of Google Cloud Storage
                    client.files.delete(name=uploaded_ai_file.name)
                    
                except Exception as error:
                    st.error(f"An processing error occurred: {error}")
                finally:
                    # Clean up the file out of your local desktop folder
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)