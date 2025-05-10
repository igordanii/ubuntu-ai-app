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

def translate_text_with_gemini(text_to_translate, target_language="pt-BR"): # Target Portuguese (Brazil)
    if not text_to_translate:
        return "No text provided for translation."

    print(f"[Gemini] Requesting translation for: '{text_to_translate[:50]}...' to {target_language}")

    if SIMULATE_GEMINI:
        return f"(Simulated) Translated to {target_language}: '{text_to_translate}'"

    # --- Actual Gemini API Call (Example) ---
    # Ensure API_KEY is configured above.
    # try:
    #     model = genai.GenerativeModel('gemini-pro') # Or the latest appropriate model
    #     prompt = f"Translate the following text to {target_language} (Brazilian Portuguese if 'pt-BR'): \"{text_to_translate}\""
    #     response = model.generate_content(prompt)
    #     return response.text.strip()
    # except AttributeError: # If genai or model is not configured due to missing API key
    #     print("ERROR: Gemini API not configured (likely missing API key).")
    #     return "Error: Gemini API not configured."
    # except Exception as e:
    #     print(f"Gemini API Error: {e}")
    #     return f"Error during translation: {str(e)}"
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Translate this text to " + target_language + ": " + text_to_translate)
    return response.text



if __name__ == "__main__":
    print(get_gemini_response_text("How does AI work?"))
