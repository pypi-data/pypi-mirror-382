
import httpx

from typing import List
from openai import OpenAI

from wela_agents.embedding.embedding import Embedding

class OpenAIEmbedding(Embedding):
    def __init__(self,
        *,
        model_name: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
    ) -> None:
        self.__model_name: str = model_name
        self.__client: OpenAI = OpenAI(api_key=api_key, base_url=base_url)

    def embed(self, source_sentence: List[str]) -> List[List[float]]:
        response = self.__client.embeddings.create(model=self.__model_name, input=source_sentence)

        return [data_i.embedding for data_i in response.data]
