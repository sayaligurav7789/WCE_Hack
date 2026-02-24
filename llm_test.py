import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL")

client = OpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

while True:
    prompt = input("\nEnter prompt (or type exit): ")

    if prompt.lower() == "exit":
        break

    response = client.chat.completions.create(
        model="meta/llama3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )
    
    print(response.choices[0].message.content)