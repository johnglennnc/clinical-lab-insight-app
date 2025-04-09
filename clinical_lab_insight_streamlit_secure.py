import streamlit as st
import tempfile
import fitz  # PyMuPDF
import openai
import os

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Clinical Lab Insight AI", layout="centered")
st.title("🧠 Clinical Lab Insight Generator")

uploaded_file = st.file_uploader("📄 Upload a lab report PDF", type=["pdf"])
extracted_text = ""

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_pdf_path = tmp_file.name

    try:
        with fitz.open(tmp_pdf_path) as doc:
            for page in doc:
                extracted_text += page.get_text()
        st.success("✅ PDF text extraction complete!")
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {e}")

if extracted_text:
    st.subheader("📜 Extracted Lab Report Text")
    st.text_area("Extracted Text", extracted_text, height=200)

    if st.button("🤖 Generate Clinical Insight"):
        with st.spinner("💬 Analyzing with fine-tuned GPT..."):
            try:
                response = openai.ChatCompletion.create(
                    model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an experienced functional medicine clinician named Eric. Based only on the provided lab report text, return a JSON with recommendations, hormones, ranges, and dosages in your own voice."
                        },
                        {
                            "role": "user",
                            "content": f"Here is a lab report:\n{extracted_text}"
                        }
                    ],
                    temperature=0.7
                )

                output = response.choices[0].message.content
                st.subheader("🧠 AI Clinical Insight")
                st.code(output, language="json")

            except Exception as e:
                st.error(f"⚠️ Error generating insights: {e}")
