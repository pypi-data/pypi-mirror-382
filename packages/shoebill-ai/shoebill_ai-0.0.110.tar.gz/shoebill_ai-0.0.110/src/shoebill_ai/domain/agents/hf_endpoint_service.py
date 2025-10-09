from typing import Optional

from huggingface_hub import HfApi, InferenceEndpointStatus


class HfEndpointService:
    def __init__(self, token: str):
        self.token = token
        # 1. Initialize the HfApi client
        self.api = HfApi()

    def get_endpoint_status(self, endpoint_name: str) -> Optional[str]:
        try:
            # 2. Get the endpoint details
            endpoint = self.api.get_inference_endpoint(name=endpoint_name,
                                                  token=self.token)

            # 3. Check the status
            status = endpoint.status
            return f"{status}"

        except Exception as e:
            print(f"An error occurred: {e}")

    def scale_to_zero(self, endpoint_name: str) -> None:
        self.api.scale_to_zero_inference_endpoint(endpoint_name, token=self.token)

    def start_endpoint(self, endpoint_name: str) -> None:
        self.api.resume_inference_endpoint(endpoint_name, token=self.token)