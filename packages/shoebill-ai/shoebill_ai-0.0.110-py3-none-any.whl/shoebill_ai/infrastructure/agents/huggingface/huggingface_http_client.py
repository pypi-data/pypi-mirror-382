import logging
from typing import Dict, Any, Optional, List

from huggingface_hub import InferenceClient


class HuggingFaceHttpClient:
    """
    HTTP client for the Hugging Face Inference API using huggingface_hub.InferenceClient.
    Provides a unified post(endpoint, payload, tools) similar to Ollama/OpenAI clients.
    """

    def __init__(self, api_url: str, api_token: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize a new HuggingFaceHttpClient.

        Args:
            api_url: The base URL of the HF Inference endpoint (can be model repo like "meta-llama/Llama-3.1-8B-Instruct").
            api_token: Optional HF token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url.rstrip('/') if api_url else ""
        self.api_token = api_token
        self.timeout = timeout or 60

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"HuggingFaceHttpClient: Initializing client for {self.api_url}")
        self.client = InferenceClient(
            token=self.api_token,
            model=self.api_url,
            timeout=self.timeout
        )

    def post(self, endpoint: str, payload: Dict[str, Any], tools: List[dict] = None) -> Optional[Dict[str, Any]]:
        """
        Send a request to the Hugging Face Inference API using huggingface_hub.

        Supported endpoints: "chat" and "embeddings".
        """
        self.logger.info(f"HuggingFaceHttpClient: Sending request to {endpoint} endpoint")

        try:
            model = payload.get("model")  # optional, can override default client model
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)
            max_tokens = payload.get("max_tokens")
            seed = payload.get("seed")
            stream = payload.get("stream", False)
            response_format = payload.get("response_format")
            input_text = payload.get("input")

            client = self.client

            if endpoint == "chat":
                # Normalize messages to HF SDK format
                # messages: list of {role, content}
                hf_messages = []
                for m in messages:
                    role = m.get("role", "user")
                    content = m.get("content", "")
                    hf_messages.append({"role": role, "content": content})

                # Build kwargs for client.chat.completions
                kwargs: Dict[str, Any] = {
                    "messages": hf_messages,
                    "temperature": temperature,
                    "stream": stream,
                    "model": model
                }

                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                if seed is not None:
                    kwargs["seed"] = seed
                if response_format is not None:
                    kwargs["response_format"] = response_format

                self.logger.info(f"HuggingFaceHttpClient: Sending chat request with {kwargs}")
                # The HF SDK provides a chat.completions API compatible with OpenAI schema for many models.
                response_json: Dict[str, Any] = {
                    "message": {
                        "role": "assistant",
                        "content": ""
                    }
                }

                if stream:
                    try:
                        response = client.chat.completions.create(**kwargs)
                        try:
                            for chunk in response:
                                if chunk.choices and chunk.choices[0].delta:
                                    delta = chunk.choices[0].delta
                                    if getattr(delta, "content", None):
                                        response_json["message"]["content"] += delta.content
                        except Exception as e:
                            self.logger.error(f"HuggingFaceHttpClient: Error during streaming chunk response: {e}")
                    except Exception as e:
                        self.logger.error(f"HuggingFaceHttpClient: Error during streaming chat response: {e}")
                else:
                    completion = client.chat.completions.create(**kwargs)
                    if completion.choices and completion.choices[0].message:
                        msg = completion.choices[0].message
                        response_json["message"]["role"] = msg.role
                        response_json["message"]["content"] = msg.content or ""

                return response_json

            elif endpoint == "feature_extraction":
                resp = client.feature_extraction(text=input_text)
                # resp.data[0].embedding is consistent with OpenAI style
                return {"embedding": resp.data[0].embedding if getattr(resp, "data", None) else []}

            else:
                self.logger.error(f"HuggingFaceHttpClient: Unsupported endpoint: {endpoint}")
                return None

        except Exception as e:
            self.logger.error(f"HuggingFaceHttpClient: Error during API call to {endpoint}: {e}")
            return None
