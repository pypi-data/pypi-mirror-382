import requests
from .config import GuardrailsConfig
from .response import GuardrailsResponse, PIIResponse

class GuardrailsClient:
    """
    A client for interacting with Enkrypt AI Guardrails API endpoints.
    """

    def __init__(self, api_key, base_url="https://api.enkryptai.com"):
        """
        Initializes the client.

        Parameters:
        - api_key (str): Your API key for authenticating with the service.
        - base_url (str): Base URL of the API (default: "https://api.enkryptai.com").
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _request(self, method, endpoint, headers=None, **kwargs):
        """
        Internal helper to send an HTTP request.

        Automatically adds the API key to headers.
        """
        url = self.base_url + endpoint
        headers = headers or {}
        if 'apikey' not in headers:
            headers['apikey'] = self.api_key
            
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            print(e)
            return {"error": str(e)}

    # ----------------------------
    # Basic Guardrails Endpoints
    # ----------------------------

    def health(self):
        """
        Get the health status of the service.
        """
        return self._request("GET", "/guardrails/health")

    def status(self):
        """
        Check if the API is up and running.
        """
        return self._request("GET", "/guardrails/status")

    def models(self):
        """
        Retrieve the list of models loaded by the service.
        """
        return self._request("GET", "/guardrails/models")

    def detect(self, text, config=None):
        """
        Detects prompt injection, toxicity, NSFW content, PII, hallucination, and more.

        Parameters:
        - text (str): The text to analyze.
        - guardrails_config (dict or GuardrailsConfig, optional): A configuration for detectors.
          If a GuardrailsConfig instance is provided, its underlying dictionary will be used.
          If not provided, defaults to injection attack detection only.

        Returns:
        - JSON response from the API.
        """
        # Use injection attack config by default if none provided
        if config is None:
            config = GuardrailsConfig.injection_attack()

        # Allow passing in either a dict or a GuardrailsConfig instance.
        if hasattr(config, "as_dict"):
            config = config.as_dict()
            
        payload = {
            "text": text,
            "detectors": config
        }
        response_body = self._request("POST", "/guardrails/detect", json=payload)
        return GuardrailsResponse(response_body)

    def pii(self, text, mode, key="null", entities=None):
        """
        Detects Personally Identifiable Information (PII) and can de-anonymize it.
        """
        payload = {
            "text": text,
            "mode": mode,
            "key": key,
            "entities": entities
        }
        response_body = self._request("POST", "/guardrails/pii", json=payload)
        return PIIResponse(response_body)

    # ----------------------------
    # Guardrails Policy Endpoints
    # ----------------------------

    def add_policy(self, name, config, description="guardrails policy"):
        """
        Create a new policy with custom configurations.
        
        Args:
            name (str): Name of the policy
            config (dict or GuardrailsConfig): Configuration for the policy detectors.
                If a GuardrailsConfig instance is provided, its underlying dictionary will be used.
            description (str, optional): Description of the policy. Defaults to "guardrails policy"
        """
        # Allow passing in either a dict or a GuardrailsConfig instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
            
        payload = {
            "name": name,
            "description": description,
            "detectors": config
        }
        
        try:
            return self._request("POST", "/guardrails/add-policy", json=payload)
        
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def get_policy(self, policy_name):
        """
        Retrieve an existing policy by providing its header identifier.
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        try:
            return self._request("GET", "/guardrails/get-policy", headers=headers)
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def modify_policy(self, policy_name, config, name=None, description="guardrails policy"):
        """
        Modify an existing policy.
        """
        # Allow passing in either a dict or a GuardrailsConfig instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
            
        if name is None:
            name = policy_name
            
        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {
            "detectors": config,
            "name": name,
            "description": description
        }
        try:
            return self._request("PATCH", "/guardrails/modify-policy", headers=headers, json=payload)
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def delete_policy(self, policy_name):
        """
        Delete a policy.
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        try:
            return self._request("DELETE", "/guardrails/delete-policy", headers=headers)
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def policy_detect(self, policy_name, text):
        """
        Apply a specific policy to detect and filter content.
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {"text": text}
        
        try:
            
            response_body = self._request("POST", "/guardrails/policy/detect", headers=headers, json=payload)
            return GuardrailsResponse(response_body)
        
        except Exception as e:
            print(e)
            return {"error": str(e)}
