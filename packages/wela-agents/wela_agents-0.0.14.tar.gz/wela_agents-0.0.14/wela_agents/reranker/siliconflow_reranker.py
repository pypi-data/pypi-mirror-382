
import httpx

from typing import Dict
from typing import List

from wela_agents.reranker.reranker import Reranker

class SiliconflowReRanker(Reranker):

    def __init__(self,
        *,
        model_name: str,
        api_key: str | None = None
    ) -> None:
        self.__model_name: str = model_name
        self.__api_key: str = api_key

    def rerank(self, query: str, documents: List) -> List[Dict[str, int | float]]:
        url = "https://api.siliconflow.cn/v1/rerank"

        payload = {
            "model": self.__model_name,
            "query": query,
            "documents": documents
        }
        headers = {
            "Authorization": f"Bearer {self.__api_key}",
            "Content-Type": "application/json"
        }

        response = httpx.post(url, json=payload, headers=headers)
        return [
            {
                "index": result["index"],
                "score": result["relevance_score"]
            } for result in response.json().get("results", [])
        ]
