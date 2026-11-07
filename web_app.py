import streamlit as st
import requests
import base64
from io import BytesIO
from urllib.parse import urljoin

# API Endpoint
API_URL = "http://localhost:8000/separate"
BASE_URL = "http://localhost:8000/"  # Used to resolve relative URLs

def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/png;base64,{encoded});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.15);
            z-index: 0;
        }}
        .block-container {{
            position: relative;
            z-index: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Change "background.jpg" to your image file path
add_bg_from_local('pexels-garrettmorrow-1649771.jpg')

# Streamlit UI
st.markdown(
    """
    <p style="text-align: center; color:#FFFFFF; font-size: 55px; font-weight: bold;">
        🎵 Music Source Separator 🎵
    </p>
    <p style="text-align: center; color: #FFFFFF; font-size: 18px;">
        Upload your audio file and split it into vocals, drums, bass, and more!
    </p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "",
    type=["mp3", "wav", "flac"],
    help="Supported formats: MP3, WAV, FLAC"
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    # Send file to the API
    with st.spinner("🎧 Processing your track... This might take a moment..."):
        response = requests.post(API_URL, files={"file": uploaded_file})

    st.text(f"Response Status Code: {response.status_code}")

    try:
        response_json = response.json()
        st.text(f"Response JSON: {response_json}")  # Debugging

        if response.status_code == 200 and "files" in response_json:
            separated_files = response_json["files"]
            st.success("✅ Separation successful!")

            for label, file_url in separated_files.items():
                st.markdown(
                        f"""
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px; background-color: rgba(0, 0, 0, 0.85);">
                            <h4 style="margin: 0;">🎶 {label.capitalize()}</h4>
                            <audio controls style="width: 100%;">
                                <source src="{file_url}" type="audio/wav">
                            </audio>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Ensure the URL is absolute
                full_url = urljoin(BASE_URL, file_url)

                # Download audio from URL
                file_response = requests.get(full_url)
                if file_response.status_code == 200:
                    audio_bytes = BytesIO(file_response.content)

                    # Download button
                    st.download_button(
                        label=f"Download {label} track",
                        data=audio_bytes,
                        file_name=f"{label}.wav",
                        mime="audio/wav"
                    )
                else:
                    st.error(f"❌ Failed to download {label} track (HTTP {file_response.status_code})")

        else:
            st.error("❌ API response does not contain 'files'.")
    
    except Exception as e:
        st.error(f"❌ Error parsing response: {str(e)}")
