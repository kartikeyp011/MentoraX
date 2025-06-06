# extract_keywords.py

import google.generativeai as genai
import json


# Configure the Google Generative AI API
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    return model


def extract_keywords(description):
    # Initialize the model
    model = configure_genai('YOUR_GOOGLE_API_KEY')  # Replace with your API key

    chat_session = model.start_chat(
        history=[]
    )

    # Create a prompt to extract skill keywords
    prompt = (
        "Extract skill keywords from the following job description and return them as a Python list. "
        "Do not group the keywords; provide them in a simple list format.\n\n"
        f"Job Description: {description}"
    )

    response = chat_session.send_message(prompt)

    # Parse the response
    try:
        keywords = json.loads(response.text)
    except json.JSONDecodeError:
        print("Error decoding response from Gemini model.")
        keywords = []

    return keywords


# Example usage (optional, for testing):
if __name__ == "__main__":
    # Example job description
    description = (
        "We are seeking an experienced Data Scientist with skills in Python, machine learning, data analysis, "
        "and statistical modeling. Experience with SQL and data visualization tools is also preferred."
    )

    keywords = extract_keywords(description)

    print("Extracted Keywords:", keywords)
