from openai import OpenAI
from typing import List, Dict

model_path="/data/hongyili/llm/Qwen2.5-7B-Instruct/"

client = OpenAI(
    api_key="EMPTY",
    base_url='http://10.176.40.138:8091/v1',
)

def call_chat_api(history: List[Dict]):
    chat_response = client.chat.completions.create(
        model=model_path,
        messages=history,
        temperature = 0,
        # max_tokens=2048,
    )
    return chat_response.choices[0].message.content