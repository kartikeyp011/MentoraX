"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""

import os
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)

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

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message('''I am gonna give you a job description. Extract skill keywords from the description and give them to me. Dont group the keywords, provide them in a python list: Job Summary: We are seeking an experienced and visionary Data Scientist to join our dynamic advertising unit at DAZN.. As a media Data Scientist, you will play a crucial role in leveraging data-driven insights to optimize our advertising strategies and maximize revenue generation. You will work closely with cross-functional data teams to develop and implement advanced data strategies, predictive models, and algorithms that drive effective advertising campaigns, targeting, and monetization.
Responsibilities:

Data Analysis and Insights:
Develop and implement advanced analytical models, algorithms, and statistical techniques to extract meaningful insights from large-scale advertising datasets.
Conduct exploratory data analysis to identify trends, patterns, and opportunities for improving ad targeting, user engagement, and campaign performance.
Perform A/B testing, attribution modelling, and other statistical analyses to measure the effectiveness of advertising initiatives and identify areas for optimization.

Predictive Modelling and Machine Learning:
Design and develop predictive models and machine learning algorithms to optimize ad targeting, ad placement, and campaign optimization.
Collaborate with cross-functional teams (ad operations, product, engineering) to integrate data-driven solutions into the advertising platform, improving ad inventory management, audience segmentation, and performance forecasting.
Evaluate model performance and implement strategies for model monitoring, validation, and continuous improvement.

What you bring to the Table:
- BS/MS in Computer Science/Statistics/Math or other STEM field
- Expert Knowledge of Python and relevant libraries as well as ML libraries (pandas, numpy, scikit-learn, xgboost etc.)
- Successfully build and deployed Machine Learning Models into production.
- Experience with data cleaning, preparation, feature engineering and model selection techniques
- Experience with CI/CD pipelines, Docker or Similar
- Strong SQL skills and the ability to perform data analyses using data warehouses (Including Experience with Data Pipelines for example with Airflow & dbt)
- Scientist Skillset: Fast Learner, curious and sense of detail
- Problem-solving skills and the ability to deliver concise, actionable solutions from disparate sources of data

Nice to have
- Some exposure to Deep Learning and relevant frameworks (PyTorch, FastAI or Tensorflow, Keras)
- Previous experience or knowledge of the Advertising space''')

print(response.text)