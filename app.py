import streamlit as st
from PIL import Image
import pytesseract
from vision_models import perform_ocr_with_model
from groq import Groq  # Import Groq for Llama model integration
import os
import json
import base64
import io

# App Configuration
st.set_page_config(
    page_title="OCR Vision App",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Colors, Fonts, and Animations
st.markdown(
    """
    <style>
    /* Background and Text Colors */
    .main {
        background-color: #f4f4f9;
        color: #2e2e2e;
    }

    h1, h2, h3, h4 {
        color: #3b82f6;
        font-family: 'Roboto', sans-serif;
    }

    /* Sidebar Customization */
    .sidebar .sidebar-content {
        background-color: #1e3a8a;
        color: #ffffff;
    }

    /* Button Animations */
    button {
        transition: transform 0.2s ease-in-out;
    }
    button:hover {
        transform: scale(1.1);
        background-color: #3b82f6;
        color: white;
    }

    /* Custom Footer Styling */
    .footer {
        text-align: center;
        color: #6b7280;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Content
st.title("🦙 OCR Vision App")
# st.markdown(
#     '<p style="margin-top: -20px; color: #2e2e2e;">Extract structured text from images using Llama 3.2 Vision!</p>',
#     unsafe_allow_html=True
# )
# st.markdown("---")

# Main Content
# st.title("🦙 OCR Vision App")

# Initialize session state
if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None

# Add clear button to top right
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear 🗑️"):
        if 'ocr_result' in st.session_state:
            del st.session_state['ocr_result']
        st.experimental_rerun()

st.markdown('<p style="margin-top: -20px;">Extract structured text from images using Llama 3.2 Vision!</p>', unsafe_allow_html=True)
st.markdown("---")

# Output Formats
OUTPUT_FORMATS = ["plain text", "markdown", "json"]

# Sidebar Controls
with st.sidebar:
    st.sidebar.title("🔧 Controls")
    
    # Select Vision Model
    vision_model = st.sidebar.selectbox(
        "Select Vision Model",
        options=["easyocr", "llama3.2.vision:latest", "groq-llama-3.2-90b-vision-preview", "custom-vision"],
        index=0
    )
    
    # Select Output Format
    output_format = st.sidebar.selectbox(
        "Output Format",
        options=OUTPUT_FORMATS,
        index=0
    )
    
    st.header("📄 Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # Resize and compress the image to reduce size
        max_size = (1024, 1024)  # Define maximum size
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        st.image(image, caption="Uploaded Image")
        
        # Perform OCR Button
        if st.button("Extract Text 🔍", type="primary"):
            with st.spinner("Performing OCR..."):
                extracted_text = None  # Initialize
                
                if vision_model == "groq-llama-3.2-90b-vision-preview":
                    try:
                        # Initialize Groq client with API key from secrets
                        api_key = st.secrets["GROQ_API_KEY"]
                        client = Groq(api_key=api_key)

                        # Convert image to bytes
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        img_bytes = buffered.getvalue()

                        # Encode image bytes to base64
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

                        # Prepare messages with base64 image
                        messages = [
                            {"role": "system", "content": "Extract text from the following image."},
                            {"role": "user", "content": f"data:image/png;base64,{img_base64}"}
                        ]

                        # Create completion
                        completion = client.chat.completions.create(
                            model="llama-3.2-90b-vision-preview",
                            messages=messages,
                            temperature=1,
                            max_tokens=1024,
                            top_p=1,
                            stream=False,
                            stop=None,
                        )

                        # Extract OCR result from response
                        extracted_text = completion.choices[0].message['content']
                    except Exception as e:
                        st.error(f"Error with Groq Llama model: {e}")
                        extracted_text = None
                else:
                    # Use the existing OCR function for other models
                    extracted_text = perform_ocr_with_model(image, vision_model, uploaded_file)
                
                # Update session state with OCR result
                if extracted_text:
                    st.session_state.ocr_result = extracted_text
                else:
                    st.session_state.ocr_result = "No text extracted."
    else:
        st.info("Please upload an image to start OCR.")

# Display OCR result in main content area
if st.session_state.ocr_result:
    st.markdown("---")
    st.write("### OCR Result")
    
    if output_format == "plain text":
        st.text_area("Plain Text Output", st.session_state.ocr_result, height=300)
    elif output_format == "markdown":
        st.markdown(f"```markdown\n{st.session_state.ocr_result}\n```")
    elif output_format == "json":
        json_output = {"extracted_text": st.session_state.ocr_result, "model_used": vision_model}
        st.json(json_output)

    # Download Extracted Text
    with st.container():
        if output_format == "plain text":
            download_data = st.session_state.ocr_result
            file_name = "extracted_text.txt"
            mime_type = "text/plain"
        elif output_format == "markdown":
            download_data = f"```markdown\n{st.session_state.ocr_result}\n```"
            file_name = "extracted_text.md"
            mime_type = "text/markdown"
        elif output_format == "json":
            download_data = json.dumps({"extracted_text": st.session_state.ocr_result, "model_used": vision_model}, indent=4)
            file_name = "extracted_text.json"
            mime_type = "application/json"

        st.download_button(
            label="📥 Download Extracted Text",
            data=download_data,
            file_name=file_name,
            mime=mime_type
        )

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
