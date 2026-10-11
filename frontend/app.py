import streamlit as st
import os
import sys
import time

# -----------------------------
# Project Path
# -----------------------------
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if project_root not in sys.path:
    sys.path.append(project_root)

from run_pipeline import process_video

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Advanced Real-Time Abandoned Object Detection",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Advanced Real-Time Abandoned Object Detection")
st.markdown("---")

results = {
    "video": "",
    "persons": 0,
    "bags": 0,
    "abandoned": 0,
    "alerts": 0,
    "fps": 0,
    "latest_alert": "No abandoned object detected."
}

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([2, 1])

# ==========================================================
# LEFT COLUMN
# ==========================================================
with left:

    st.subheader("📤 Input Video")

    uploaded_video = st.file_uploader(
        "Upload CCTV Video",
        type=["mp4", "avi", "mov"]
    )

    if uploaded_video is not None:

        st.video(uploaded_video)

        if st.button("▶ Process Video"):

            # Create input folder
            os.makedirs("input", exist_ok=True)

            input_path = os.path.join(
                "input",
                uploaded_video.name
            )

            # Save uploaded video
            with open(input_path, "wb") as f:
                f.write(uploaded_video.getbuffer())

            # Process
            start_time = time.time()

            with st.spinner("Processing Video... Please wait..."):
                results = process_video(input_path)

                output_video = results["video"]

            end_time = time.time()

            st.success("✅ Processing Completed!")

            st.subheader("🎥 Processed Video")

            # Display processed video
            st.write("Returned path:", output_video)
            st.write("File exists:", os.path.exists(output_video))

            st.video(output_video)

            # Download buttons
            col1, col2 = st.columns(2)

            with col1:
                with open(output_video, "rb") as f:
                    st.download_button(
                        label="⬇ Download Processed Video",
                        data=f,
                        file_name="processed_video.mp4",
                        mime="video/mp4"
                    )

            with col2:
                with open("logs/tracking_log.txt", "rb") as f:
                    st.download_button(
                        label="⬇ Download Log",
                        data=f,
                        file_name="tracking_log.txt",
                        mime="text/plain"
                    )

            st.info(f"⏱ Processing Time: {end_time-start_time:.2f} seconds")

# ==========================================================
# RIGHT COLUMN
# ==========================================================
with right:

    st.subheader("📊 Statistics")

    st.metric("Maximum Persons", results["persons"])
    st.metric("Maximum Bags", results["bags"])
    st.metric("Total Abandoned Events", results["abandoned"])
    st.metric("Total Risk Alerts", results["alerts"])
    st.metric("FPS", results["fps"])

    st.markdown("---")

    st.subheader("🚨 Latest Alert")

    st.info(results["latest_alert"])