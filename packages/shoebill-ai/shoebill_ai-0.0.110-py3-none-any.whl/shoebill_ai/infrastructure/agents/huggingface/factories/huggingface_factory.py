from typing import Optional, List, Dict, Any

from ....factories.llm_repo_factory import LlmRepoFactory
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .....domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from ..repositories.huggingface_chat_repository import HuggingFaceChatRepository
from ..repositories.huggingface_embed_repository import HuggingFaceEmbeddingRepository


class HuggingFaceFactory(LlmRepoFactory):
    """
    Factory for creating repositories for Hugging Face Inference models.
    """

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 api_token: str = None,
                 system_prompt: str = None,
                 tools: List[Dict[str, Any]] = None,
                 timeout: int = 60,
                 options: Dict[str, Any] = None):
        self.api_url = api_url
        self.options = options or {}
        self.api_token = api_token
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.tools = tools or []
        self.timeout = timeout

    def create_chat_repository(self) -> LlmChatRepository:
        kwargs: dict[str, Any] = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "api_token": self.api_token,
            "options": self.options
        }
        if self.system_prompt:
            kwargs["system_prompt"] = self.system_prompt
        if self.tools:
            kwargs["tools"] = self.tools
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout
        return HuggingFaceChatRepository(**kwargs)

    def create_embedding_repository(self) -> Optional[LlmEmbeddingRepository]:
        kwargs: dict[str, Any] = {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "api_token": self.api_token
        }
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout
        return HuggingFaceEmbeddingRepository(**kwargs)
