
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List

class Reranker(ABC):

    @abstractmethod
    def rerank(self, query: str, documents: List) -> List[Dict[str, int | float]]:
        pass
