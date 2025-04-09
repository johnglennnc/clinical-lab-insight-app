import streamlit as st
import openai
import tempfile
import os
import json
import fitz  # PyMuPDF

# Secure API key loading
openai.api_key = os.getenv("OPENAI_API_KEY")

# Title
st.title("🧠 Clinical Lab Insight Generator (Fine-tuned Model)")
st.markdown("Upload a PDF lab report or paste text below to generate clinical recommendations.")

# File upload
uploaded_file = st.file_uploader("📄 Upload PDF Lab Report", type="pdf")
lab_text = st.text_area("✏️ Or paste lab report text here (optional)", height=300)

# PDF text extraction with PyMuPDF
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.read())
        tmp_pdf_path = tmp_pdf.name

    with fitz.open(tmp_pdf_path) as doc:
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()

    os.remove(tmp_pdf_path)
    lab_text = extracted_text.strip()

# Submit button
if st.button("🔍 Generate Clinical Insights") and lab_text:
    with st.spinner("Generating insights..."):
        try:
            response = openai.chat.completions.create(
                model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                messages=[
                    {"role": "system", "content": "You are a clinical assistant trained on functional medicine lab interpretation. Respond only with structured JSON using Eric’s style."},
                    {"role": "user", "content": f"""Here is a lab report:
{lab_text}"""}
                ],
                temperature=0.3
            )

            message_content = response.choices[0].message.content

            try:
                parsed = json.loads(message_content)
                st.success("✅ Clinical recommendations generated:")
                st.json(parsed)
            except json.JSONDecodeError:
                st.warning("⚠️ GPT response was not valid JSON. Here’s the raw output:")
                st.text(message_content)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif st.button("🔁 Reset"):
    st.experimental_rerun()

