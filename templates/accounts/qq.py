from openai import OpenAI
import os

client = OpenAI(
    base_url="dotapi.nvidia.com",
    api_key=os.environ["NVIDIA_API_KEY"]
)

completion = client.chat.completions.create(
    model="deepseek-ai/deepseek-v4-pro",
    messages=[
        {"role": "user", "content": "Hello! Say 'API is working' if you can see this."}
    ],
    temperature=0.7,
    top_p=0.95,
    max_tokens=100,
    stream=False
)

print(completion.choices[0].message.content)