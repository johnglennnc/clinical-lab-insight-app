import streamlit as st
import openai
import tempfile
import fitz  # PyMuPDF
import json
import os

# Load OpenAI API Key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧪 Clinical Lab Insight Generator")

uploaded_file = st.file_uploader("Upload a lab report PDF", type=["pdf"])

extracted_text = ""
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_pdf_path = tmp_file.name

    try:
        with fitz.open(tmp_pdf_path) as doc:
            for page in doc:
                extracted_text += page.get_text()
        st.success("✅ PDF text extraction complete!")
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {e}")

if extracted_text:
    st.subheader("📝 Extracted Text")
    st.text_area("Raw OCR/Text Output", extracted_text, height=200)

    if st.button("⚡ Generate Clinical Insights", key="generate_insights") and extracted_text.strip():
        with st.spinner("Asking Eric’s AI twin..."):
            try:
                response = openai.ChatCompletion.create(
                    model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                    messages=[
                        {"role": "system", "content": "You are a clinical analyst AI trained to interpret lab reports in Eric's exact style."},
                        {"role": "user", "content": f"Here is a lab report:\n{extracted_text}\n\nPlease extract and summarize any hormones, ranges, goals, dosages, and clinical recommendations in Eric’s exact language and return it as JSON."}
                    ],
                    temperature=0.4
                )
                message = response.choices[0].message.content

                try:
                    parsed = json.loads(message)
                    st.subheader("📊 Clinical Insights (Structured)")
                    st.json(parsed)
                except json.JSONDecodeError:
                    st.warning("⚠️ GPT response was not valid JSON. Here’s the raw output:")
                    st.text(message)

            except Exception as e:
                st.error(f"🚨 API Error: {e}")

