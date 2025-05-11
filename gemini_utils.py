import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

SIMULATE_GEMINI = False

def get_gemini_response_text(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def translate_text_with_gemini(text_to_translate, target_language): # Target Portuguese (Brazil)
    if not text_to_translate:
        return "No text provided for translation."

    print(f"[Gemini] Requesting translation for: '{text_to_translate[:50]}...' to {target_language}")

    if SIMULATE_GEMINI:
        return f"(Simulated) Translated to {target_language}: '{text_to_translate}'"


    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Translate this text to " + target_language + ": " + text_to_translate)
    return response.text



if __name__ == "__main__":
    print(get_gemini_response_text("How does AI work?"))
