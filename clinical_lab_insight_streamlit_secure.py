import streamlit as st
import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from openai import OpenAI
import json

# Setup OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI
st.set_page_config(page_title="Clinical Lab Insight", layout="wide")
st.title("🧠 Clinical Lab Insight Tool")
st.markdown("Upload a PDF lab report. The AI will extract key values and generate clinical recommendations.")

# File uploader
uploaded_file = st.file_uploader("📤 Upload Lab PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_pdf_path = tmp_file.name

        # Convert PDF to images
        images = convert_from_path(tmp_pdf_path, dpi=300)

        # Run OCR on each page
        ocr_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            ocr_text += f"\n\n--- Page {i+1} ---\n{text}"

        # Display raw OCR text (optional)
        with st.expander("📄 View OCR Text"):
            st.text_area("Extracted Text", ocr_text, height=300)

    # Step 2: Run Clinical Interpretation via GPT
    if st.button("🧠 Generate Clinical Recommendations"):
        with st.spinner("Thinking..."):
            prompt = f"""
You are a medical assistant trained by Dr. Eric at Modern Sports Medicine. 

Given the OCR text from a scanned lab report below, extract and return a JSON containing:
- Hormones or lab tests detected
- Value
- Units
- Reference range (if available)
- Dosage (if available)
- Clinical recommendation (if any)

OCR TEXT:
{ocr_text}

Return ONLY a JSON array of objects like:
[
  {{
    "test": "TSH",
    "value": "0.998",
    "units": "uIU/mL",
    "range": "0.450-4.500",
    "recommendation": "Maintain current thyroid support"
  }},
  ...
]
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                ai_text = response.choices[0].message.content.strip()

                try:
                    parsed = json.loads(ai_text)
                    st.success("✅ Clinical recommendations generated.")
                    st.json(parsed)
                except json.JSONDecodeError:
                    st.warning("⚠️ GPT response was not valid JSON. Here’s the raw output:")
                    st.text(ai_text)

            except Exception as e:
                st.error(f"❌ Error generating clinical interpretation: {e}")
