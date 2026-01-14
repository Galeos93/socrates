import os
from openai import OpenAI


def openai_llm_call(prompt: str, model="gpt-4", temperature=0.0) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a precise knowledge assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
