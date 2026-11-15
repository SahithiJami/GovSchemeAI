import streamlit as st
from google import genai

try:
    api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(api_key=api_key)

    print("\nAVAILABLE GEMINI MODELS:\n")

    for model in client.models.list():

        actions = model.supported_actions or []

        if "generateContent" in actions:
            print(model.name)

except Exception as e:
    print("Error:", e)