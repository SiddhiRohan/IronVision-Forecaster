from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[{"role": "user", "content": "Say 'working' and nothing else."}]
)
print(response.choices[0].message.content)