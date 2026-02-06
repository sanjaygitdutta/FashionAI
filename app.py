import streamlit as st
import os
import io
from google import genai
from gtts import gTTS  # ✅ Added for Voice
from services.vision_services import analyze_outfit_vision
from agent_logic import run_fashion_agent

# 1. Ui Setup
st.set_page_config(page_title="AI Fashion Stylist", page_icon="👗")
st.title("👗 AI Personal Fashion Stylist")
st.write("Upload a photo or use your camera to let the AI stylist check your outfit, weather, and schedule.")


# 2. Sidebar – API Key
with st.sidebar:
    st.header("🔑 Settings")
    # Note: For security, you might want to remove the default value before sharing!
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

# Logic to pick which image to use
input_image = camera_file if camera_file else uploaded_file

user_query = st.text_input(
    "Any specific occasion?",
    placeholder="e.g., Is this okay for my 2 PM meeting?"
)


# 4. Main Action
if input_image:

    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
        st.stop()

    # Preview image
    st.image(input_image, caption="Selected Outfit", use_container_width=True)

    if st.button("✨ Get Expert Advice"):
        try:
            client = genai.Client(api_key=api_key)

            image_bytes = input_image.getvalue()
            mime_type = input_image.type

            # STEP 1 & 2: Vision & Agentic Reasoning
            with st.status("🧠 Processing your request...", expanded=True) as status:
                st.write("👀 Analyzing outfit...")
                vision_results = analyze_outfit_vision(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    client=client
                )
                
                st.write("✅ Vision analysis completed")
                status.update(label="🧠 Checking weather & calendar...", state="running")

                final_recommendation = run_fashion_agent(
                    user_prompt=user_query or "Give me general styling advice",
                    image_data=vision_results,
                    client=client
                )

                status.update(label="✨ Styling complete!", state="complete")

            # STEP 3: Output (Text)
            st.subheader("🧥 Stylist Recommendation")
            st.markdown(final_recommendation)

            # STEP 4: Output (Voice)
            try:
                with st.spinner("🔊 Generating voice summary..."):
                    # Use gTTS to create the audio from the recommendation
                    tts = gTTS(text=final_recommendation, lang='en')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    
                    # This will display the audio player and autoplay the advice
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)
            except Exception as v_e:
                st.warning("Could not generate voice audio, but your text is ready above!")

            # Details expander
            with st.expander("🔍 Vision Analysis Details"):
                st.json(vision_results)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif not api_key:
    st.warning("Please enter your API key in the sidebar to begin.")