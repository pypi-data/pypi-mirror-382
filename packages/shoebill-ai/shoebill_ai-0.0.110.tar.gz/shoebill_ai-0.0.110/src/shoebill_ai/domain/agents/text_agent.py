from typing import Dict, List, Any, Optional

from .. import LlmChatRepository

# Provide a module-level reference for OllamaFactory so tests can patch it
OllamaFactory: Any | None = None
HuggingFaceFactory: Any | None = None

class TextAgent:

    def __init__(self,
               api_url: str,
               model_name: str,
               system_prompt: str = None,
               api_token: str = None,
               tools: List[Dict[str, Any]] = None,
               timeout: int = 60,
               options: Dict[str, Any] = None,
               provider: str = "huggingface"):
        """
        Create a new TextAgent
        """
        self.api_url = api_url
        self.model_name = model_name
        self.api_token = api_token
        self.system_prompt = system_prompt
        self.tools = tools
        self.timeout = timeout
        self.options = options or {}



        self.llm_chat_repository: LlmChatRepository|None = None
        if provider == "ollama":
            global OllamaFactory
            if OllamaFactory is None:
                from ...infrastructure.agents.ollama.factories.ollama_factory import OllamaFactory as _OF
                OllamaFactory = _OF
            self.ollama_fac = OllamaFactory(api_url=self.api_url,
                                            model_name=self.model_name,
                                            system_prompt=self.system_prompt,
                                            api_token=self.api_token,
                                            tools=self.tools,
                                            timeout=self.timeout,
                                            options=self.options)
            self.llm_chat_repository = self.ollama_fac.create_chat_repository()
        elif provider == "huggingface":
            global HuggingFaceFactory
            if HuggingFaceFactory is None:
                from ...infrastructure.agents.huggingface.factories.huggingface_factory import HuggingFaceFactory as _HF
                HuggingFaceFactory = _HF
            self.huggingface_fac = HuggingFaceFactory(api_url=self.api_url,
                                                     model_name=self.model_name,
                                                     system_prompt=self.system_prompt,
                                                     api_token=self.api_token,
                                                     tools=self.tools,
                                                     timeout=self.timeout,
                                                     options=self.options)
            self.llm_chat_repository = self.huggingface_fac.create_chat_repository()
        else:
            self.llm_chat_repository = None


    def chat(self,
             user_message: str,
             system_prompt: Optional[str] = None,
             chat_history: List[dict[str, Any]] = None,
             tools: List[Dict[str, Any]] = None) -> Optional[list[dict[str, Any]]]:

        chat_system_prompt = system_prompt or self.system_prompt
        chat_tools = tools or self.tools

        return self.llm_chat_repository.chat(
            user_message=user_message,
            system_prompt=chat_system_prompt,
            chat_history=chat_history,
            tools=chat_tools)