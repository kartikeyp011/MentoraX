# Install the Google AI Python SDK
# $ pip install google-generativeai

import os
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="***REMOVED***")

# Create the model
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
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Fetch job and skills from another source (example placeholder)
def fetch_user_job_and_skills():
    # Placeholder for fetching job and skills from the actual source
    job = "Data Scientist"
    skills = ["Python", "Machine Learning", "Data Analysis"]
    return job, skills

# Generate the query
def generate_query(job, skills):
    skills_list = ", ".join(skills)
    query = (f"I am looking for a job in {job} and i have these skills : {skills_list}. Remember this data for any further responses. Now i will ask you further questions and you need to answer for those only. Dont give any additional out of the box information. Give first response as hello, how are you what would you like to ask ? Reframe this")
    return query

# Start a chat session with Gemini
chat_session = model.start_chat(history=[])

# Fetch user job and skills
job, skills = fetch_user_job_and_skills()

# Generate query and send to Gemini
query = generate_query(job, skills)
response = chat_session.send_message(query)

# Print only the topics from the response
# Assume the response contains a list of topics or steps in a structured way

topics = response.text.split('\n')  # Assuming topics are separated by new lines
for topic in topics:
    print(f"{topic.strip()}")

# Example output processing
# You might need to adjust the parsing based on the actual response format from Gemini