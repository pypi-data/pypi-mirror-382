from typing import Optional, List, Dict, Any

from .....domain.agents.interfaces.llm_chat_repository import LlmChatRepository
from .base_openai_repository import BaseOpenAIRepository
from ...utils.image_utils import encode_image

import logging


class OpenAIChatRepository(BaseOpenAIRepository, LlmChatRepository):
    """
    Repository for chat interactions using the OpenAI API in an Ollama-like pattern.
    """

    def __init__(self,
                 api_url: str,
                 model_name: str,
                 system_prompt: str = None,
                 api_key: str = None,
                 organization: str = None,
                 tools: List[Dict[str, Any]] = None,
                 timeout: int = 60,
                 temperature: float = 0.7,
                 max_tokens: int = None,
                 seed: int = None):
        """
        Initialize a new OpenAIChatRepository.

        Args:
            api_url: The base URL of the OpenAI API.
            model_name: The name of the model to use.
            system_prompt: Optional system prompt to use for the chat.
            api_key: API key for authentication.
            organization: Optional organization ID.
            tools: Optional list of tools to make available to the model.
            timeout: Optional timeout in seconds for API requests.
            temperature: Sampling temperature.
            max_tokens: Max tokens in the response.
            seed: Optional seed for reproducibility.
        """
        super().__init__(api_url, model_name, api_key, organization, timeout)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
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
        Chat with the model using the OpenAI API.

        Returns a list of messages including the assistant reply (similar to OllamaChatRepository).
        """
        messages: List[dict[str, Any]] = []
        if chat_history:
            messages = chat_history.copy()

        # System prompt
        sys_prompt = system_prompt or self.system_prompt
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})

        # User message (text only or multimodal)
        if image_path:
            image_base64 = encode_image(image_path)
            # OpenAI vision expects content as a list of typed parts
            user_content = [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": user_message})

        result = self._call_openai_api(messages, tools)

        if result is not None:
            messages.append({"role": "assistant", "content": result})
        else:
            messages.append({"role": "assistant", "content": "Failed to get response"})

        return messages

    def _call_openai_api(self, messages: List[dict[str, Any]], tools: List[Dict[str, Any]] = None) -> Optional[str]:
        """
        Call the OpenAI API with the given messages using OpenAIHttpClient.
        """
        self.logger.info(f"OpenAIChatRepository: Preparing chat request for model {self.model_name}")

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if self.seed is not None:
            payload["seed"] = self.seed
        # Default to non-streaming for now; streaming accumulation is handled internally if enabled later
        payload["stream"] = False

        available_tools = tools if tools is not None else self.tools

        response_data = self.http_client.post("chat", payload, tools=available_tools)
        if response_data:
            self.logger.info("OpenAIChatRepository: Received response from API")
            content = response_data.get("message", {}).get("content", "")
            return content

        self.logger.error("OpenAIChatRepository: Failed to get response from API")
        return None
