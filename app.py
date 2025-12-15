import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json
import os

# --- Configuration ---
CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"

AVAILABLE_MODELS = [
    "unsloth/gemma-3-27b-it",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen3-VL-235B-A22B-Instruct",
    "Qwen/Qwen2.5-VL-32B-Instruct",
    "unsloth/gemma-3-4b-it",
    "unsloth/gemma-3-12b-it",
]

DEFAULT_SYSTEM_INSTRUCTION = """Give description of an object you see on uploaded night sky image
You either see:
    meteor

    fireball

    bright moon

    something else

    uploaded image does not contain night sky
    If you get something outside listed categories, tell about it in one short sentence, 10 words max.
    If you see bright rainbow - it's likely a spectrum from diffraction grating that appears from meteor/fireball"""

# --- Helper Functions ---
def encode_image(image_file):
    """Encodes a file-like image object to base64 string."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def get_image_media_type(filename):
    """Returns the media type based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        return "image/jpeg"
    elif ext == '.png':
        return "image/png"
    elif ext == '.webp':
        return "image/webp"
    elif ext == '.gif':
        return "image/gif"
    else:
        return "image/jpeg" # Default fallback

# --- UI Layout ---
st.set_page_config(page_title="Chutes Vision Interface", page_icon="🌠", layout="wide")

st.title("🌠 Chutes.ai Vision Interface")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    
    api_key_input = st.text_input("CHUTES_API_KEY", type="password", help="Enter your Chutes.ai API Key")
    
    selected_model = st.selectbox(
        "Select Model",
        AVAILABLE_MODELS,
        index=0  # Default to unsloth/gemma-3-27b-it (first in list)
    )
    
    st.subheader("Model Parameters")
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    max_tokens = st.number_input("Max Output Tokens", min_value=1, max_value=8192, value=1024, step=128)

# Main Content Area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input")
    
    system_instruction = st.text_area(
        "System Instructions",
        value=DEFAULT_SYSTEM_INSTRUCTION,
        height=200
    )
    
    user_prompt = st.text_area("User Prompt", value="What is in this image?", height=100)
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

with col2:
    st.subheader("Output")
    
    if st.button("Analyze Image", type="primary"):
        if not api_key_input:
            st.error("Please enter your CHUTES_API_KEY in the sidebar.")
        elif not uploaded_file:
            st.error("Please upload an image.")
        else:
            with st.spinner("Sending request to Chutes API..."):
                try:
                    # Prepare Data
                    base64_image = encode_image(uploaded_file)
                    media_type = get_image_media_type(uploaded_file.name)
                    image_url = f"data:{media_type};base64,{base64_image}"
                    
                    # Construct Payload
                    payload = {
                        "model": selected_model,
                        "messages": [
                            {
                                "role": "system", 
                                "content": system_instruction
                            },
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_url
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False # Simpler for now, can add streaming later if needed
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {api_key_input}",
                        "Content-Type": "application/json"
                    }
                    
                    # Make Request
                    response = requests.post(CHUTES_API_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract Content
                        content = result['choices'][0]['message']['content']
                        st.markdown("### Response")
                        st.write(content)
                        
                        # Extract Token Usage
                        usage = result.get('usage', {})
                        prompt_tokens = usage.get('prompt_tokens', 'N/A')
                        completion_tokens = usage.get('completion_tokens', 'N/A')
                        total_tokens = usage.get('total_tokens', 'N/A')
                        
                        st.divider()
                        st.markdown("### Token Usage")
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        metric_col1.metric("Input Tokens", prompt_tokens)
                        metric_col2.metric("Output Tokens", completion_tokens)
                        metric_col3.metric("Total Tokens", total_tokens)
                        
                        with st.expander("Raw JSON Response"):
                            st.json(result)
                            
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

