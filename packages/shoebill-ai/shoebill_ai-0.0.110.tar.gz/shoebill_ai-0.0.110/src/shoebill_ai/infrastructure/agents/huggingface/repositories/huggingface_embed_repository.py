from typing import Optional, List
import logging

from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from .base_huggingface_repository import BaseHuggingFaceRepository


class HuggingFaceEmbeddingRepository(BaseHuggingFaceRepository, LlmEmbeddingRepository):
    """
    Repository for creating embeddings using the Hugging Face Inference API.
    """

    def __init__(self, api_url: str, model_name: str, api_token: str = None, timeout: int = None):
        super().__init__(api_url, model_name, api_token, timeout)
        self.logger = logging.getLogger(__name__)

    def embed(self, text: str) -> Optional[List[float]]:

        try:
            self.logger.info(f"Creating embedding")
            embeddings = self.http_client.feature_extraction(text=text)
            return embeddings.tolist()
        except Exception as e:
            repository_error = f"Error creating embeddings: {str(e)}"
            self.logger.error(repository_error)
            return None
