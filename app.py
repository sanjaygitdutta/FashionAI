import streamlit as st
import os
from google import genai
from services.vision_services import analyze_outfit_vision
from agent_logic import run_fashion_agent


# 1. Ui Setup
st.set_page_config(page_title="AI Fashion Stylist", page_icon="👗")
st.title("👗 AI Personal Fashion Stylist")
st.write("Upload a photo and let the AI stylist check your outfit, weather, and schedule.")


# 2. Sidebar – API Key
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password", value="AIzaSyBKTv1PJSOTk7kLaE3R4pjmar-uOqbZGfg")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key


# 3. Inputs
uploaded_file = st.file_uploader(
    "Upload your outfit photo",
    type=["jpg", "jpeg", "png"]
)

user_query = st.text_input(
    "Any specific occasion?",
    placeholder="e.g., Is this okay for my 2 PM meeting?"
)


# 4. Main Action
if uploaded_file:

    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
        st.stop()

    # Preview image
    st.image(uploaded_file, caption="Your Outfit", use_container_width=True)

    if st.button("✨ Get Expert Advice"):
        try:
            client = genai.Client(api_key=api_key)

            image_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type  # ✅ REQUIRED

            # STEP 1: Vision
            with st.status("👀 Analyzing outfit...", expanded=True) as status:
                vision_results = analyze_outfit_vision(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    client=client
                )
                st.write("✅ Vision analysis completed")

                # STEP 2: Agent 
                status.update(
                    label="🧠 Checking weather & calendar...",
                    state="running"
                )

                final_recommendation = run_fashion_agent(
                    user_prompt=user_query or "Give me general styling advice",
                    image_data=vision_results,
                    client=client
                )

                status.update(
                    label="✨ Styling complete!",
                    state="complete"
                )

            # STEP 3: Output 
            st.subheader("🧥 Stylist Recommendation")
            st.markdown(final_recommendation)

            with st.expander("🔍 Vision Analysis Details"):
                st.json(vision_results)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif not api_key:
    st.warning("Please enter your API key in the sidebar to begin.")