
import streamlit as st
import fitz  # PyMuPDF
import openai
import os

# Securely get the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Clinical Lab Insight (Powered by Fine-Tuned GPT)")

uploaded_file = st.file_uploader("Upload a lab report PDF", type="pdf")
if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    doc = fitz.open("temp.pdf")
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text()

    st.text_area("Extracted Text", extracted_text)

    if st.button("Generate Clinical Insights") and extracted_text:
        with st.spinner("Analyzing..."):
            try:
                response = openai.ChatCompletion.create(
                    model="ft:gpt-3.5-turbo-0125:the-bad-company-holdings-llc::BKB3w2h2",
                    messages=[
                        {"role": "system", "content": "You are a functional medicine clinical lab specialist."},
   {"role": "user", "content": f"""Here is a lab report:
{lab_text}"""}

{extracted_text}"}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                st.success("✅ Clinical recommendations generated.")
                st.markdown(content)
            except Exception as e:
                st.error(f"❌ Error generating insights: {e}")
