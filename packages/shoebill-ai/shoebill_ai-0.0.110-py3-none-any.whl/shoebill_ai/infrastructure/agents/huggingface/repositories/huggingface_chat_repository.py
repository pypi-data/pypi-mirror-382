from typing import Optional, List, Dict, Any

from ...utils.image_utils import encode_image
from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .base_huggingface_repository import BaseHuggingFaceRepository

import logging


class HuggingFaceChatRepository(BaseHuggingFaceRepository, LlmChatRepository):
    """
    Repository for chat interactions using the Hugging Face Inference API.
    """

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 system_prompt: str = None,
                 api_token: str = None,
                 tools: List[Dict[str, Any]] = None,
                 timeout: int = 60,
                 options: Dict[str, Any] = None):
        """
        Initialize a new HuggingFaceChatRepository.
        """
        super().__init__(api_url, model_name, api_token, timeout)

        self.options = options or {}
        self.system_prompt = system_prompt
        self.tools = tools or []

        self.logger = logging.getLogger(__name__)

    def chat(self,
             user_message: str,
             system_prompt: Optional[str] = None,
             chat_history: List[dict[str, Any]] = None,
             tools: List[Dict[str, Any]] = None,
             image_path: Optional[str] = None) -> Optional[list[dict[str, Any]]]:
        """
        Chat with the model using the Hugging Face Inference API.
        """
        messages: List[dict[str, Any]] = []
        if chat_history:
            messages = chat_history.copy()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        if image_path:
            # HF chat.completions with images depends on specific models; include a best-effort base64 if supported
            image_base64 = encode_image(image_path)
            # Some HF models accept content as a dict with type/image_url; we keep text + mention
            messages.append({"role": "user", "content": f"{user_message}\n[Image attached: base64 inline not shown]"})
        else:
            messages.append({"role": "user", "content": user_message})

        result = self._call_hf_api(messages, tools)

        if result:
            messages.append({"role": "assistant", "content": result})
        else:
            messages.append({"role": "assistant", "content": "Failed to get response"})

        return messages

    def _call_hf_api(self, messages: List[dict[str, Any]], tools: List[Dict[str, Any]]) -> Optional[str]:
        self.logger.info(f"HuggingFaceChatRepository: Preparing chat request for model {self.model_name}")

        payload = self.options.copy()
        # payload["model"] = self.model_name
        # payload["messages"] = messages
        # Align with OpenAI-like params if present in options
        endpoint = "chat"

        available_tools = self.tools
        if tools is not None:
            available_tools = tools

        chat_completion = self.http_client.chat.completions.create(model=self.model_name, messages=messages, tools=available_tools)
        self.logger.info(f"HuggingFaceChatRepository: Received response from API::{chat_completion}")
        if chat_completion.choices and chat_completion.choices[0].message:
            msg = chat_completion.choices[0].message
            content = msg.content or ""
            return content

        self.logger.error("HuggingFaceChatRepository: Failed to get response from API")
        return None
