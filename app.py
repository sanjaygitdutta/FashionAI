import streamlit as st
import os
import io
from google import genai
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
    # Tip: In a real demo, leave this blank so the judges see you enter a key!
    api_key = st.text_input("Enter Gemini API Key", type="password", value="AIzaSyBKTv1PJSOTk7kLaE3R4pjmar-uOqbZGfg")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

# 3. Inputs (Webcam + Upload Merged)
st.write("### 📸 Step 1: Provide your outfit")
tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Use Webcam"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload your outfit photo",
        type=["jpg", "jpeg", "png"]
    )

with tab2:
    camera_file = st.camera_input("Take a photo of your outfit")

# Prioritize webcam photo if taken, else use upload
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

    # Center the preview
    st.image(input_image, caption="Current Outfit Selection", use_container_width=True)

    if st.button("✨ Get Expert Advice", use_container_width=True):
        try:
            client = genai.Client(api_key=api_key)
            image_bytes = input_image.getvalue()
            mime_type = input_image.type

            # STEP 1 & 2: Processing via Status Container
            with st.status("🧠 Agent at work...", expanded=True) as status:
                st.write("👁️ Analyzing clothing details...")
                vision_results = analyze_outfit_vision(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    client=client
                )
                
                st.write("📅 Checking context (Weather/Calendar)...")
                final_recommendation = run_fashion_agent(
                    user_prompt=user_query or "Give me general styling advice",
                    image_data=vision_results,
                    client=client
                )
                status.update(label="✅ Advice Ready!", state="complete", expanded=False)

            # --- RESULTS UI ---
            st.divider()
            st.subheader("🧥 Stylist Recommendation")
            st.markdown(final_recommendation)

            # STEP 4: Voice Output
            try:
                with st.spinner("🔊 Generating voice summary..."):
                    tts = gTTS(text=final_recommendation, lang='en')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    # Use container width for a cleaner player look
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)
            except Exception:
                st.info("Note: Audio summary unavailable, but recommendation is ready above.")

            # Details expander for transparency
            with st.expander("🔍 View AI Reasoning Details"):
                st.json(vision_results)

        except Exception as e:
            st.error(f"Execution Error: {e}")

elif not api_key:
    st.info("💡 Pro-tip: Enter your API key in the sidebar to unlock the Stylist.")