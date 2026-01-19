import os
from typing import Callable
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


def create_openai_llm_call(client: OpenAI, model: str = "gpt-4") -> Callable[[str], str]:
    """Create an llm_call function using the provided client and model."""
    def llm_call(prompt: str, temperature: float = 0.0) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise knowledge assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    return llm_call
