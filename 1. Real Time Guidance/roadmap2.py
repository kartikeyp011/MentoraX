# roadmap_creator.py

import google.generativeai as genai
import json


def create_roadmap(keywords_list):
    # Flatten the list of keywords from multiple job descriptions
    all_keywords = [keyword for keywords in keywords_list for keyword in keywords]

    # Initialize the Gemini model
    genai.configure(api_key='***REMOVED***')
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

    chat_session = model.start_chat(
        history=[]
    )

    # Create a prompt to generate a ranked roadmap
    prompt = (
        "You are a career advisor. Based on the following list of skills extracted from job descriptions, "
        "please rank them by priority and skill level required to learn. Provide the ranked skills in a JSON list format, "
        "with each skill including its name, priority (based on the frequency of appearance), and required skill level.\n\n"
        f"Skills: {', '.join(all_keywords)}"
    )

    response = chat_session.send_message(prompt)

    # Parse the response to get the roadmap
    try:
        roadmap = json.loads(response.text)
    except json.JSONDecodeError:
        print("Error decoding response from Gemini model.")
        roadmap = []

    return roadmap


# Example usage:
if __name__ == "__main__":
    # Load keywords from a file for testing
    with open('keywords.json', 'r') as file:
        keywords_list = json.load(file)

    roadmap = create_roadmap(keywords_list)

    # Print the roadmap
    print(json.dumps(roadmap, indent=4))
