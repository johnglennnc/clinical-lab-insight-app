import os
import fitz  # PyMuPDF
import streamlit as st
import openai

# Set OpenAI API Key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Clinical Lab Insight", layout="centered")
st.title("🧠 Clinical Lab Insight Generator")
st.markdown("Upload a PDF lab report to generate clinical recommendations using a fine-tuned GPT model.")

uploaded_file = st.file_uploader("📄 Upload your PDF lab report", type=["pdf"])

if uploaded_file is not None:
    try:
        with open("temp_lab_report.pdf", "wb") as f:
            f.write(uploaded_file.read())

        with fitz.open("temp_lab_report.pdf") as doc:
            extracted_text = "\n".join(page.get_text() for page in doc)

        st.success("✅ PDF text extraction complete!")
        st.text_area("📄 Extracted Text", extracted_text, height=250)

        if extracted_text.strip():
            with st.spinner("💬 Generating clinical insights..."):
                try:
                    # Try the fine-tuned model first
                    response = openai.chat.completions.create(
                        model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                        messages=[
                            {"role": "system", "content": "You are a medical assistant trained to analyze lab reports and provide clinical recommendations."},
                            {"role": "user", "content": f"Here is a lab report:\n\n{extracted_text}"}
                        ]
                    )
                    st.success("✅ Clinical recommendations generated (Fine-tuned Model)")
                    st.markdown("### 🧪 Clinical Insights")
                    st.write(response.choices[0].message.content)

                except Exception as e:
                    # Fallback to GPT-4
                    st.warning("⚠️ Fine-tuned model failed. Falling back to GPT-4.")
                    fallback_response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a medical assistant trained to analyze lab reports and provide clinical recommendations."},
                            {"role": "user", "content": f"Here is a lab report:\n\n{extracted_text}"}
                        ]
                    )
                    st.success("✅ Clinical recommendations generated (GPT-4 Fallback)")
                    st.markdown("### 🧪 Clinical Insights")
                    st.write(fallback_response.choices[0].message.content)

        else:
            st.error("❌ No text was extracted from the PDF. Please upload a valid lab report.")

    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {e}")
