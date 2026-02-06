import streamlit as st
import os
import io
import json
from google import genai
from google.genai import types
from gtts import gTTS 
from services.vision_services import analyze_outfit_vision
from agent_logic import run_fashion_agent

# 1. UI Setup
st.set_page_config(page_title="AI Fashion Stylist", page_icon="👗", layout="centered")
st.title("👗 AI Personal Fashion Stylist")
st.write("Upload a photo or use your camera to let the AI stylist check your outfit, weather, and schedule.")

# 2. Sidebar – API Key
with st.sidebar:
    st.header("🔑 Settings")
    # Tip: For a hackathon, leave the default blank or use st.secrets
    api_key = st.text_input("Enter Gemini API Key", type="password", value="YOUR_API_KEY_HERE")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

# 3. Inputs (Webcam + Upload)
st.write("### 📸 Step 1: Provide your outfit")
tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Use Webcam"])

with tab1:
    uploaded_file = st.file_uploader("Upload your outfit photo", type=["jpg", "jpeg", "png"])

with tab2:
    camera_file = st.camera_input("Take a photo of your outfit")

input_image = camera_file if camera_file else uploaded_file

user_query = st.text_input(
    "Any specific occasion?",
    placeholder="e.g., Is this okay for my 2 PM meeting?"
)

# 4. Main Action
if input_image:
    if not api_key:
        st.sidebar.error("⚠️ API Key required!")
        st.stop()

    st.image(input_image, caption="Current Outfit Selection", use_container_width=True)

    if st.button("✨ Get Expert Advice", use_container_width=True):
        try:
            client = genai.Client(api_key=api_key)
            image_bytes = input_image.getvalue()
            mime_type = input_image.type

            # STEP 1 & 2: Processing
            with st.status("🧠 Agent at work...", expanded=True) as status:
                st.write("👁️ Analyzing clothing details...")
                vision_results = analyze_outfit_vision(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    client=client
                )
                
                st.write("📅 Checking context (Weather/Calendar)...")
                response_text = run_fashion_agent(
                    user_prompt=user_query or "Give me general styling advice",
                    image_data=vision_results,
                    client=client
                )
                status.update(label="✅ Advice Ready!", state="complete", expanded=False)

            #  PARSE STRUCTURED JSON RESULTS 
            st.divider()
            try:
                data = json.loads(response_text)
                
                # Winner Badge
                st.balloons()
                st.success(f"🏆 **Winner: {data['winner']}**")
                
                # Why it wins
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write("### Why this wins:")
                    for r in data['reason']:
                        st.write(f"✅ {r}")
                
                with col2:
                    st.write("### ⚖️ Tradeoffs")
                    st.json(data['tradeoffs'])

                # Final Written Recommendation
                st.info(data['final_recommendation'])

                # Voice summary (reads the final recommendation)
                tts_text = data['final_recommendation']

            except json.JSONDecodeError:
                # Fallback if AI skips JSON format
                st.subheader("🧥 Stylist Recommendation")
                st.markdown(response_text)
                tts_text = response_text

            # VOICE OUTPUT 
            try:
                with st.spinner("🔊 Generating voice summary..."):
                    tts = gTTS(text=tts_text, lang='en')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)
            except Exception:
                st.info("Note: Audio summary unavailable.")

            # Details expander for technical transparency
            with st.expander("🔍 View AI Reasoning Details"):
                st.write("**Visual Observations:**")
                if 'data' in locals():
                    st.write(", ".join(data['visual_observations']))
                st.json(vision_results)

        except Exception as e:
            st.error(f"Execution Error: {e}")

elif not api_key:
    st.info("💡 Pro-tip: Enter your API key in the sidebar to unlock the Stylist.")