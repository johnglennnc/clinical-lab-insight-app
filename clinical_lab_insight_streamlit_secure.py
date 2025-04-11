import streamlit as st
import os
import tempfile
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_ID = "ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2"

st.set_page_config(page_title="Clinical Lab Insight")
st.title("🧬 Clinical Lab Insight Generator")

uploaded_file = st.file_uploader("Upload your lab report (PDF, image, .txt, or .docx)", type=["pdf", "png", "jpg", "jpeg", "txt", "docx"])

def extract_text_from_file(file_path, file_type):
    try:
        if file_type == "pdf":
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text.strip()
        elif file_type in ["png", "jpg", "jpeg"]:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image).strip()
        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif file_type == "docx":
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs]).strip()
        else:
            return ""
    except Exception as e:
        st.error(f"❌ Error extracting text from file: {e}")
        return ""

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    file_extension = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    extracted_text = extract_text_from_file(tmp_path, file_extension)

    if not extracted_text:
        st.warning("⚠️ No text was extracted. Please upload a valid file.")
    else:
        st.success("✅ Text extraction complete!")

        if st.button("🧠 Generate Clinical Recommendations"):
            with st.spinner("Consulting the fine-tuned model..."):
                try:
                    response = openai.ChatCompletion.create(
                        model=MODEL_ID,
                        messages=[
                            {"role": "system", "content": "You are a medical assistant generating clinical recommendations."},
                            {
                                "role": "user",
                                "content": f"Here is a lab report:\n{extracted_text}\n\nReturn only a valid JSON with this structure:\n{{\n  \"Hormones\": [],\n  \"Ranges\": [],\n  \"Goals\": [],\n  \"Dosages\": [],\n  \"Recommendations\": []\n}}"
                            }
                        ]
                    )

                    output = response.choices[0].message.content

                    try:
                        parsed = json.loads(output)
                        st.subheader("📋 Clinical Recommendations (Structured):")
                        st.json(parsed)
                    except json.JSONDecodeError:
                        st.warning("⚠️ GPT response was not valid JSON. Here’s the raw output:")
                        st.text(output)

                except Exception as e:
                    st.error(f"❌ Error during GPT call: {e}")
