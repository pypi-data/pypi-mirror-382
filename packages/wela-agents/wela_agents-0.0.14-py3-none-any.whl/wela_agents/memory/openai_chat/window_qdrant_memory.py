
from typing import List
from typing import Optional

from qdrant_client import QdrantClient

from wela_agents.schema.prompt.openai_chat import Message
from wela_agents.embedding.embedding import Embedding
from wela_agents.memory.openai_chat.qdrant_memory import QdrantMemory
from wela_agents.memory.openai_chat.qdrant_memory import unique
from wela_agents.memory.openai_chat.qdrant_memory import sort_key_id
from wela_agents.memory.openai_chat.qdrant_memory import sort_key_score

class WindowQdrantMemory(QdrantMemory):
    def __init__(self, memory_key: str, embedding: Embedding, qdrant_client: QdrantClient, vector_size = 512, limit: int=15, window_size: int = 5, score_threshold: Optional[float] = None) -> None:
        super().__init__(memory_key, embedding, qdrant_client, vector_size, limit, score_threshold)
        self.__limit: int = limit
        self.__window_size: int = window_size

    def get_contexts(self, contexts: List[Message]) -> List[Message]:
        scored_points = self._get_points_by_message_list(contexts)
        scored_points = scored_points + self._get_last_n_points(n=self.__window_size)
        scored_points = unique(scored_points)
        scored_points = sorted(scored_points, key=sort_key_score)
        scored_points = scored_points[-self.__limit:]
        scored_points = sorted(scored_points, key=sort_key_id)

        return [scored_point.payload["message"] for scored_point in scored_points]

__all__ = [
    "WindowQdrantMemory"
]
