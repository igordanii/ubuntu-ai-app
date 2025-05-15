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

def is_api_configured():
    if SIMULATE_GEMINI: # If simulating, we don't strictly need a key for these functions to "work"
        return True
    # Check if genai is configured (assuming API_KEY was set and genai.configure called)
    # A more robust check would be to see if genai.get_model throws an error or if the API key var is set
    api_key_present = bool(os.getenv("GOOGLE_API_KEY"))
    if not api_key_present:
        print("ERROR: GOOGLE_API_KEY environment variable not set. Cannot make live API calls.")
    return api_key_present


def translate_text_with_gemini(text_to_translate, target_language="pt-BR"):
    if not text_to_translate:
        return "No text provided for translation."
    
    print(f"[Gemini] Requesting translation for: '{text_to_translate[:50]}...' to {target_language}")

    if SIMULATE_GEMINI:
        return f"(Simulated) Translated to {target_language}: '{text_to_translate}'"
    
    if not is_api_configured():
        return "Error: Gemini API not configured (API key missing)."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash') # Or specific model for translation if available
        # Crafting a good prompt is key
        prompt = f"Translate the following text into {target_language} (be precise, if {target_language} is 'pt-BR', use Brazilian Portuguese variant):\n\n\"{text_to_translate}\""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (translate_text_with_gemini): {e}")
        return f"Error during translation: {str(e)}"


def summarize_text_with_gemini(text_to_summarize, length="medium"): # length can be "short", "medium", "long"
    if not text_to_summarize:
        return "No text provided for summarization."

    print(f"[Gemini] Requesting summarization for: '{text_to_summarize[:50]}...' (length: {length})")

    if SIMULATE_GEMINI:
        return f"(Simulated) {length.capitalize()} summary of: '{text_to_summarize}'"

    if not is_api_configured():
        return "Error: Gemini API not configured (API key missing)."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Prompt engineering for summarization
        if length == "short":
            prompt = f"Summarize the following text in one or two concise sentences:\n\n\"{text_to_summarize}\""
        elif length == "long":
            prompt = f"Provide a detailed summary (multiple paragraphs if necessary) of the following text, capturing key points and nuances:\n\n\"{text_to_summarize}\""
        else: # medium
            prompt = f"Summarize the following text in a few sentences (e.g., a short paragraph):\n\n\"{text_to_summarize}\""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (summarize_text_with_gemini): {e}")
        return f"Error during summarization: {str(e)}"


def improve_formatting_with_gemini(text_to_format):
    if not text_to_format:
        return "No text provided for formatting."

    print(f"[Gemini] Requesting formatting improvement for: '{text_to_format[:50]}...'")

    if SIMULATE_GEMINI:
        return f"(Simulated) Improved formatting for: '{text_to_format}'\n- Example bullet point 1\n- Example bullet point 2"

    if not is_api_configured():
        return "Error: Gemini API not configured (API key missing)."
        
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Prompt for formatting improvement. This is highly dependent on what kind of "improvement" is desired.
        # Examples: Fixing markdown, making paragraphs more readable, converting to bullet points, etc.
        prompt = (
            "Please improve the formatting of the following text for better readability. "
            "This might include adjusting paragraph breaks, ensuring consistent spacing, "
            "using markdown for lists or emphasis if appropriate (like *italic* or **bold**), "
            "and correcting any obvious formatting errors. "
            "Return only the improved text, without any introductory phrases like 'Here is the improved text:'.\n\n"
            f"Original text:\n\"{text_to_format}\""
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (improve_formatting_with_gemini): {e}")
        return f"Error during formatting improvement: {str(e)}"



# --- Direct Test Block ---
if __name__ == '__main__':
 
    # Ensure your GOOGLE_API_KEY is set as an environment variable for live tests.
    # Or set SIMULATE_GEMINI = False after configuring the API key in the script for testing.
    
    print("--- Testing Gemini Utils ---")
    # print("Ensure GOOGLE_API_KEY is set in your environment for live tests, or SIMULATE_GEMINI=False above.")

    sample_text_en = "The quick brown fox jumps over the lazy dog. This is a classic pangram used to test typewriters and keyboards. It contains all letters of the English alphabet."
    sample_text_pt = "A rápida raposa marrom salta sobre o cão preguiçoso. Este é um pangrama clássico usado para testar máquinas de escrever e teclados. Ele contém todas as letras do alfabeto."
    
    # Test Translation
    print("\n--- Testing Translation ---")
    # Set SIMULATE_GEMINI = False and ensure API key is configured to test live
    translated = translate_text_with_gemini(sample_text_en, target_language="pt-BR")
    print(f"To pt-BR: {translated}")
    translated_en = translate_text_with_gemini(sample_text_pt, target_language="en")
    print(f"To en: {translated_en}")

    # Test Summarization
    print("\n--- Testing Summarization ---")
    summary_short = summarize_text_with_gemini(sample_text_en, length="short")
    print(f"Short Summary: {summary_short}")
    summary_medium = summarize_text_with_gemini(sample_text_en, length="medium")
    print(f"Medium Summary: {summary_medium}")

    # Test Formatting Improvement
    print("\n--- Testing Formatting Improvement ---")
    messy_text = "first item.second item.also a third item that is a bit longer and could use better structure.Contact: test@example.com or (123) 456-7890"
    formatted_text = improve_formatting_with_gemini(messy_text)
    print(f"Original Messy Text:\n{messy_text}")
    print(f"\nImproved Formatting:\n{formatted_text}")

    no_text = ""
    print(f"\n--- Testing with empty input ---")
    print(f"Translate empty: {translate_text_with_gemini(no_text)}")
    print(f"Summarize empty: {summarize_text_with_gemini(no_text)}")
    print(f"Format empty: {improve_formatting_with_gemini(no_text)}")

