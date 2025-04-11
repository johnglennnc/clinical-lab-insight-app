import streamlit as st
import os
import tempfile
import fitz  # pymupdf
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
import openai

# Use environment variable for security
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_ID = "ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2"

st.set_page_config(page_title="Clinical Lab Insight", layout="wide")
st.title("🧠 Clinical Lab Insight Generator")
st.markdown("Upload a **lab report** as a PDF, image, or TXT file to receive structured clinical insights.")

uploaded_file = st.file_uploader("📤 Upload a lab report", type=["pdf", "png", "jpg", "jpeg", "txt"])

extracted_text = ""

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text().strip()
                if not page_text:
                    # Fallback to OCR if page is image-based
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
    except Exception as e:
        st.error(f"❌ PDF extraction error: {str(e)}")
    return text.strip()

def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        st.error(f"❌ Image extraction error: {str(e)}")
        return ""

def read_txt_file(txt_file):
    try:
        return txt_file.read().decode("utf-8").strip()
    except Exception as e:
        st.error(f"❌ Text file read error: {str(e)}")
        return ""

if uploaded_file:
    file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    st.success("✅ File uploaded successfully!")

    if file_ext == ".pdf":
        extracted_text = extract_text_from_pdf(tmp_file_path)
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(tmp_file_path)
        extracted_text = extract_text_from_image(image)
    elif file_ext == ".txt":
        extracted_text = read_txt_file(open(tmp_file_path, "rb"))

    if extracted_text:
        st.success("✅ Text extraction complete!")
        st.text_area("📄 Extracted Text", extracted_text, height=250)

        if st.button("🧠 Generate Clinical Insight"):
            try:
                response = openai.ChatCompletion.create(
                    model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                    messages=[
                        {"role": "system", "content": "You are a medical assistant generating clinical recommendations."},
                        {"role": "user", "content": f"Here is a lab report:\n{extracted_text}\n\nReturn only a valid JSON with this structure:\n{{\n  \"Hormones\": [],\n  \"Ranges\": [],\n  \"Goals\": [],\n  \"Dosages\": [],\n  \"Recommendations\": []\n}}"}
                    ]
                )
                output = response.choices[0].message.content
                st.markdown("### 🧾 Clinical Recommendations")
                st.code(output, language="json")
            except Exception as e:
                st.error(f"❌ OpenAI API error: {str(e)}")
    else:
        st.warning("⚠️ No text was extracted. Please upload a valid file.")
