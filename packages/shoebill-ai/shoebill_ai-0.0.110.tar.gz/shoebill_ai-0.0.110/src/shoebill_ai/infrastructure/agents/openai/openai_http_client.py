import logging
from typing import Dict, Any, Optional, List

import openai
from openai import OpenAI


class OpenAIHttpClient:
    """
    Base HTTP client for the OpenAI API using the openai library.
    Handles authentication and common request functionality.
    """

    def __init__(self, api_url: str, api_key: str, organization: str = None, timeout: Optional[int] = None):
        """
        Initialize a new OpenAIHttpClient.

        Args:
            api_key: The API key for authentication.
            organization: Optional organization ID for API requests.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.organization = organization
        self.timeout = timeout or 60  # Default timeout of 60 seconds

        self.logger = logging.getLogger(__name__)

        # Initialize the OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            timeout=self.timeout,
            base_url=self.api_url
        )

    def post(self, endpoint: str, payload: Dict[str, Any], tools: List[dict] = None) -> Optional[Dict[str, Any]]:
        """
        Send a request to the OpenAI API using the openai library.

        Args:
            endpoint: The endpoint to send the request to (e.g., "chat", "embeddings").
            payload: The payload to send with the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
        """
        self.logger.info(f"OpenAIHttpClient: Sending request to {endpoint} endpoint")
        self.logger.debug(f"OpenAIHttpClient: Payload: {payload}")

        try:

            model = payload.get("model")
            messages = payload.get("messages", [])
            temperature = payload.get("temperature", 0.7)
            max_tokens = payload.get("max_tokens")
            seed = payload.get("seed")
            stream = payload.get("stream", False)
            response_format = payload.get("response_format")

            # Route to the appropriate OpenAI method based on the endpoint
            if endpoint == "chat":
                # Initialize response_json
                response_json: dict[str, Any] = {
                    "message": {
                        "role": "assistant",
                        "content": ""
                    }
                }

                # Common kwargs
                chat_kwargs: Dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": stream
                }
                if max_tokens is not None:
                    chat_kwargs["max_tokens"] = max_tokens
                if seed is not None:
                    chat_kwargs["seed"] = seed
                if tools:
                    chat_kwargs["tools"] = tools
                if response_format is not None:
                    chat_kwargs["response_format"] = response_format

                # Call the chat completions method
                if stream:
                    try:
                        response = self.client.chat.completions.create(**chat_kwargs)
                        try:
                            for chunk in response:
                                if chunk.choices and chunk.choices[0].delta:
                                    delta = chunk.choices[0].delta
                                    if getattr(delta, "content", None):
                                        response_json["message"]["content"] += delta.content
                                    # Note: streaming tool_calls may not be fully supported; keep simple
                        except Exception as e:
                            self.logger.error(f"OpenAIHttpClient: Error during streaming chunk response: {e}")
                    except Exception as e:
                        self.logger.error(f"OpenAIHttpClient: Error during streaming chat response: {e}")
                else:
                    response = self.client.chat.completions.create(**chat_kwargs)
                    # Format response to match the expected structure
                    if response.choices and response.choices[0].message:
                        msg = response.choices[0].message
                        response_json["message"]["role"] = msg.role
                        response_json["message"]["content"] = msg.content or ""
                        # Add tool calls if present
                        if getattr(msg, "tool_calls", None):
                            response_json["message"]["tool_calls"] = [
                                {
                                    "id": tc.id,
                                    "type": tc.type,
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                } for tc in msg.tool_calls
                            ]

            elif endpoint == "embeddings":
                # Extract required parameters for embeddings
                model = payload.get("model")
                input_text = payload.get("input")
                
                # Call the embeddings method
                response = self.client.embeddings.create(
                    model=model,
                    input=input_text
                )
                
                # Format response to match the expected structure
                response_json = {
                    "embedding": response.data[0].embedding if response.data else []
                }
                
            else:
                self.logger.error(f"OpenAIHttpClient: Unsupported endpoint: {endpoint}")
                return None
                
            self.logger.info(f"OpenAIHttpClient: Received successful response from {endpoint} endpoint")
            return response_json
            
        except Exception as e:
            self.logger.error(f"OpenAIHttpClient: Error during API call to {endpoint}: {e}")
            return None