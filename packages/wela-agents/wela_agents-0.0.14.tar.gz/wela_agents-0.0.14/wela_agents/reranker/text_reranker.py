
from typing import Dict
from typing import List

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from wela_agents.reranker.reranker import Reranker

class TextReranker(Reranker):

    def __init__(self, model: str) -> None:
        self.__pipeline = pipeline(
            Tasks.sentence_embedding,
            model=model,
            sequence_length=512
        )

    def rerank(self, query: str, documents: List) -> List[Dict[str, int | float]]:
        pipeline_result = self.__pipeline(
            input={
                "source_sentence": [query],
                "sentences_to_compare": documents
            }
        )
        results = [
            {
                "index": idx,
                "score": pipeline_result["scores"][idx]
            }
            for idx, _ in enumerate(documents)
        ]
        return sorted(results, key=lambda x: x["score"], reverse=True)
