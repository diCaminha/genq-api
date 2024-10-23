import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
api_key = os.getenv('API_KEY')
client = OpenAI(api_key=api_key)