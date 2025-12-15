# Chutes.ai Vision Interface

This is a Streamlit application to interact with Chutes.ai vision models.

## Setup

1.  **Install Dependencies:**
    Ensure you have Python 3 installed.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` is not provided, but you need `streamlit`, `requests`, `python-dotenv`, `Pillow`)*
    
    Alternatively, if you followed the CLI setup:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install streamlit requests python-dotenv Pillow
    ```

## Usage

1.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

2.  **Interface:**
    *   **Sidebar:** Enter your `CHUTES_API_KEY`. Select the desired model (Default: `unsloth/gemma-3-27b-it`). Adjust temperature and max tokens.
    *   **Main Area:**
        *   **System Instructions:** Edit the default instructions if needed.
        *   **User Prompt:** Enter your specific question or prompt about the image.
        *   **Upload Image:** Upload a JPG, PNG, or WEBP image.
        *   **Analyze Image:** Click the button to send the request.

3.  **Output:**
    *   The model's description or answer will appear.
    *   Token usage (Input, Output, Total) will be displayed below the response.
