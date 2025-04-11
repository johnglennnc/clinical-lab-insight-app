import streamlit as st
import tempfile
import os
import fitz  # PyMuPDF
import docx
import openai

# Set your fine-tuned model ID here
MODEL_ID = "ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2"

st.set_page_config(page_title="Clinical Lab Insight", layout="wide")
st.title("🧪 Clinical Lab Insight")
st.write("Upload a lab report (PDF, DOCX, or TXT), and get GPT-powered clinical recommendations.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
extracted_text = ""

def extract_text_from_pdf(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        with fitz.open(tmp_path) as doc:
            return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        st.error(f"❌ PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        doc = docx.Document(tmp_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"❌ DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"❌ TXT extraction error: {e}")
        return ""

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        extracted_text = extract_text_from_docx(uploaded_file)
    elif file_type == "txt":
        extracted_text = extract_text_from_txt(uploaded_file)
    else:
        st.warning("⚠️ Unsupported file type.")

    if extracted_text.strip():
        st.success("✅ Text extraction complete!")

        if st.button("🧠 Generate Clinical Insights"):
            with st.spinner("Analyzing with GPT..."):
                try:
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model=MODEL_ID,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a medical assistant generating clinical recommendations."
                            },
                            {
                                "role": "user",
                                "content": f"""Here is a lab report:

{extracted_text}

Return only a valid JSON with this structure:
{{
  "Hormones": [],
  "Ranges": [],
  "Goals": [],
  "Dosages": [],
  "Recommendations": []
}}"""
                            }
                        ]
                    )
                    output = response.choices[0].message.content
                    st.subheader("🧬 GPT Clinical Recommendations")
                    st.code(output, language="json")
                except Exception as e:
                    st.error(f"❌ Error during GPT call:\n\n{e}")
    else:
        st.warning("⚠️ No text was extracted. Please upload a valid file.")
