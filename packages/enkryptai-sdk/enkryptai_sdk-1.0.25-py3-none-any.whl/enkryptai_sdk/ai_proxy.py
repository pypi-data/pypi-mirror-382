from .base import BaseClient
from .dto import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionErrorResponse,
    ChatCompletionDirectErrorResponse,
)


class AIProxyClientError(Exception):
    pass


class AIProxyClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        super().__init__(api_key, base_url)

    def chat(self, chat_body: ChatCompletionRequest, deployment_name: str, tags: str = None, refresh_cache: bool = False, return_error: bool = False):
        """
        Get chat completion response for a given prompt.

        Args:
            chat_body (ChatCompletionRequest): Configuration object containing chat details

        Returns:
            dict: Response from the API containing the chat completion response
        """
        headers = {"Content-Type": "application/json"}

        if deployment_name is None:
            raise AIProxyClientError("Deployment name is required")
        headers["X-Enkrypt-Deployment"] = deployment_name

        if tags is not None:
            headers["X-Enkrypt-Tags"] = tags

        if refresh_cache is not None:
            headers["X-Enkrypt-Refresh-Cache"] = str(refresh_cache).lower()

        if isinstance(chat_body, dict):
            chat_body = ChatCompletionRequest.from_dict(chat_body)

        payload = chat_body.to_dict()

        response = self._request(
            "POST", "/ai-proxy/chat/completions", headers=headers, json=payload
        )

        # print("Response from API: ", response)

        if response.get("error"):
            error_message = response["error"]
            is_json_str = error_message.startswith("{") and error_message.endswith("}")
            # Try to parse nested JSON error if it's a string
            if isinstance(error_message, str) and is_json_str:
                import ast
                # import json
                try:
                    # # Using ast.literal_eval to safely evaluate the string as a Python literal
                    # # As json.loads is not working with literal string representation of dict
                    # parsed_error = json.loads(error_message.replace("'", '"'))
                    # # Convert Python string representation to proper dict
                    parsed_error = ast.literal_eval(f"API Error: {str(response)}")
                    # # Preserve both error and enkrypt_policy_detections fields
                    response["error"] = parsed_error.get("error", parsed_error)
                    if "enkrypt_policy_detections" in parsed_error:
                        response["enkrypt_policy_detections"] = parsed_error["enkrypt_policy_detections"]
                # except json.JSONDecodeError:
                except Exception:
                    # If parsing fails, keep the original error
                    pass
                    
            # print("Error in response: ", response)
            if return_error:
                # if is_json_str:
                #     return ChatCompletionErrorResponse.from_dict(response)
                # else:
                #     return ChatCompletionDirectErrorResponse.from_dict(response)
                try:
                    # print("Error in response: ", response)
                    return ChatCompletionErrorResponse.from_dict(response)
                # except (json.JSONDecodeError, TypeError, ValueError, SyntaxError):
                except Exception:
                    # Fallback to direct error if error object can't be parsed
                    # print("Failed to parse error response: ", response)
                    return ChatCompletionDirectErrorResponse.from_dict(response)
            raise AIProxyClientError(f"API Error: {str(response)}")

        return ChatCompletionResponse.from_dict(response)
