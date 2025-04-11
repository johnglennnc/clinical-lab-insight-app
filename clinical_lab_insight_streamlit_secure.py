import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import tempfile
import os
from openai import OpenAI

# Initialize OpenAI with fine-tuned model
client = OpenAI()
fine_tuned_model = "ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2"

st.title("🧠 Clinical Lab Insight Engine")
st.markdown("Upload a lab report file (PDF, TXT, or Image), and receive clinical insights in Eric's interpretation style.")

uploaded_file = st.file_uploader("📄 Upload your file", type=["pdf", "txt", "png", "jpg", "jpeg"])

lab_text = ""

def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        st.error(f"❌ PDF extraction error: {e}")
        return ""

def extract_text_from_image(img_path):
    try:
        image = Image.open(img_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        st.error(f"❌ OCR error: {e}")
        return ""

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    file_type = uploaded_file.type

    if uploaded_file.name.endswith(".pdf"):
        st.info("📄 Extracting text from PDF...")
        lab_text = extract_text_from_pdf(tmp_path)

    elif uploaded_file.name.endswith(".txt"):
        st.info("📄 Reading text file...")
        with open(tmp_path, "r", encoding="utf-8") as f:
            lab_text = f.read()

    elif uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
        st.info("🖼️ Extracting text from image...")
        lab_text = extract_text_from_image(tmp_path)

    else:
        st.error("Unsupported file type.")

    os.unlink(tmp_path)

    if lab_text.strip():
        st.success("✅ Text extracted! Ready to analyze.")
        st.text_area("🧬 Extracted Lab Report", lab_text, height=250)

        if st.button("🧠 Generate Clinical Insight", key="insight_button"):
            with st.spinner("Thinking..."):
                prompt = (
                    f"Here is a lab report:\n\n{lab_text.strip()}\n\n"
                    "Please extract the lab values, goals, hormones, dosages, and give clinical recommendations based on this in the same style as Eric."
                    " Respond in JSON with these keys: `values`, `goals`, `hormones`, `dosages`, `recommendations`."
                )

                try:
                    response = client.chat.completions.create(
                        model=fine_tuned_model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    reply = response.choices[0].message.content
                    st.success("✅ Clinical insight generated!")
                    st.markdown(f"```json\n{reply}\n```")
                except Exception as e:
                    st.error(f"❌ Error from OpenAI: {e}")
    else:
        st.warning("⚠️ No text was extracted. Please upload a valid file.")
