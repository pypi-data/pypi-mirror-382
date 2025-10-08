
from typing import List

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from wela_agents.embedding.embedding import Embedding

class TextEmbedding(Embedding):

    def __init__(self, model: str) -> None:
        self.__pipeline = pipeline(
            Tasks.sentence_embedding,
            model=model,
            sequence_length=512
        )

    def embed(self, source_sentence: List[str]) -> List[List[float]]:
        return [
        [float(x) for x in i] for i in self.__pipeline(
            input={
                "source_sentence": source_sentence
            }
        )["text_embedding"]
        ]
