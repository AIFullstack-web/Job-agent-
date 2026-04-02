from __future__ import annotations

from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass(slots=True)
class LLMClient:
    model: str
    api_key: str
    temperature: float = 0

    def build(self) -> ChatOpenAI:
        return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=self.temperature)

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3), reraise=True)
    def invoke_json(self, system_prompt: str, user_prompt: str) -> str:
        llm = self.build()
        response = llm.invoke(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )
        return response.content
