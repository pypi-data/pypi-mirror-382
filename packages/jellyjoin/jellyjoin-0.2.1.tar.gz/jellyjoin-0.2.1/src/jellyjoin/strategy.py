from typing import Union, List, Optional, Any, Tuple, Literal, Callable, TypeAlias
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from collections.abc import Collection

from .similarity import damerau_levenshtein_similarity
from .similarity import get_similarity_function
from .type_definitions import (
    PreprocessorCallable,
    SimilarityCallable,
    SimilarityIdentifier,
)

__all__ = [
    "SimilarityStrategy",
    "OpenAIEmbeddingSimilarityStrategy",
    "PairwiseSimilarityStrategy",
]


# identity function used as a default argument to several functions
def identity(x: str) -> str:
    return x


class SimilarityStrategy(ABC):
    @abstractmethod
    def __call__(
        self,
        left_texts: Collection[str],
        right_texts: Collection[str],
    ) -> np.ndarray:
        """
        Computes the NxM similarity matrix between N left_texts and M right_texts.
        """
        pass


class OpenAIEmbeddingSimilarityStrategy(SimilarityStrategy):
    def __init__(
        self,
        client,
        embedding_model: str = "text-embedding-3-large",
        preprocessor: PreprocessorCallable = identity,
    ):
        """
        Uses an OpenAI embedding model (text-embedding-3-large by default) to
        calculate the embeddings, then uses a matrix product to quickly
        calculate all cosine similarities. OpenAI embeddings are already
        normalized, so this inner product is the same as the cosine similarity.
        """
        self.client = client
        self.embedding_model = embedding_model
        self.preprocessor = preprocessor

    def __call__(
        self,
        left_texts: Collection[str],
        right_texts: Collection[str],
    ) -> np.ndarray:
        """
        Compute an NxM matrix of similarities using an embedding model.
        """
        left_texts = [self.preprocessor(text) for text in left_texts]
        right_texts = [self.preprocessor(text) for text in right_texts]

        if not left_texts:
            return np.zeros((0, len(right_texts)))
        elif not right_texts:
            return np.zeros((len(left_texts), 0))

        # compute embeddings
        left_embeddings = self.embed(left_texts)
        right_embeddings = self.embed(right_texts)

        # calculate similarity matrix
        similarity_matrix = left_embeddings @ right_embeddings.T

        return similarity_matrix

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Helper function to get embeddings from the OpenAI client.
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts,
            encoding_format="float",
        )
        vectors = [np.array(e.embedding) for e in response.data]
        return np.stack(vectors)


class PairwiseSimilarityStrategy(SimilarityStrategy):
    def __init__(
        self,
        similarity_function: SimilarityIdentifier = None,
        preprocessor: PreprocessorCallable = identity,
    ):
        """
        preprocessor: A callable that preprocesses each input string (e.g., soundex or metaphone).
        similarity_func: A callable that computes similarity between two strings (e.g., jellyfish.jaro_winkler).
        """
        self.preprocessor = preprocessor
        self.similarity_function: SimilarityCallable = get_similarity_function(
            similarity_function
        )

    def __call__(
        self,
        left_texts: Collection[str],
        right_texts: Collection[str],
    ) -> np.ndarray:
        """
        Compute an NxM matrix of similarities using the specified preprocessor and similarity function.
        """
        size = (len(left_texts), len(right_texts))
        similarity_matrix = np.zeros(size)

        for row, left_text in enumerate(left_texts):
            left = self.preprocessor(left_text)
            for column, right_text in enumerate(right_texts):
                right = self.preprocessor(right_text)
                similarity_matrix[row, column] = self.similarity_function(right, left)

        return similarity_matrix


def get_automatic_similarity_strategy() -> SimilarityStrategy:
    """
    Instantiate the `OpenAIEmbeddingSimilarityStrategy`, if possible, or
    default to `PairwiseSimilarityStrategy` with the Damerau-levenshtein.
    """
    try:
        import openai

        # will usually succeed if OPENAI_API_KEY is defined
        client = openai.OpenAI()
        return OpenAIEmbeddingSimilarityStrategy(client)
    except:
        pass
    return PairwiseSimilarityStrategy()
