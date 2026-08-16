from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

models = client.models.list()

for model in models:
    print(model.name)