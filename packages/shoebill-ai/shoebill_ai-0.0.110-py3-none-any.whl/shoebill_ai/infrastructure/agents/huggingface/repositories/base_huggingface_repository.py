from huggingface_hub import InferenceClient

from .....domain.agents.interfaces.base_repository import BaseRepository
from ..huggingface_http_client import HuggingFaceHttpClient


class BaseHuggingFaceRepository(BaseRepository):
    """
    Base class for all Hugging Face repositories.
    Provides common functionality for interacting with the HF Inference API.
    """

    def __init__(self, api_url: str, model_name: str, api_token: str = None, timeout: int = None):
        """
        Initialize a new BaseHuggingFaceRepository.

        Args:
            api_url: The base URL or model repo id for the Hugging Face Inference API.
            model_name: The name of the model to use (can be repo id). If api_url is a base URL, model_name can still be used in payloads.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        self.model_name = model_name
        self.http_client = InferenceClient(model=api_url, token= api_token, timeout=timeout)
