
import streamlit as st
from openai import OpenAI
import json

# === CONFIG ===
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

# === UI ===
st.set_page_config(page_title="Clinical Lab Insight Generator", layout="centered")
st.title("🧠 Clinical Lab Insight Generator")
st.write("Paste OCR text from a lab report and get Eric-style clinical recommendations.")

lab_text = st.text_area("📝 Paste OCR Lab Report Text Here", height=300)

if st.button("Generate Clinical Insights", key="generate_button") and lab_text:
    with st.spinner("Thinking like Eric..."):
        prompt = f'''
You are a medical assistant trained in Eric's clinical style. Read this OCR-extracted lab report text and extract any lab values, hormones, ranges, goals, dosages, and Eric-style clinical recommendations.

OCR Text:
"""
{lab_text}
"""

Respond only in JSON format as a list of entries. Example format:
[
  {{
    "test": "TSH",
    "value": "0.998",
    "units": "uIU/mL",
    "range": "0.450–4.500",
    "recommendation": "TSH is within optimal range."
  }},
  {{
    "hormone": "Estradiol",
    "value": "42",
    "goal": ">75",
    "dosage": "PLS",
    "recommendation": "Estradiol is low. Recommend compounded E2 capsule."
  }}
]
'''

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1000
        )

        st.success("✅ Clinical recommendations generated.")
        try:
            parsed = json.loads(response.choices[0].message.content)
            st.json(parsed)
        except json.JSONDecodeError:
            st.error("⚠️ GPT response was not valid JSON. Here’s the raw output:")
            st.text(response.choices[0].message.content)
