import os
from typing import List
from openai import OpenAI

class OpenAIProvider:
    name = "openai"
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        out = []
        for p in prompts:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Avoid stereotypes."},
                    {"role": "user", "content": p},
                ],
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                max_tokens=kwargs.get("max_tokens", 300),
            )
            out.append(resp.choices[0].message.content)
        return out
