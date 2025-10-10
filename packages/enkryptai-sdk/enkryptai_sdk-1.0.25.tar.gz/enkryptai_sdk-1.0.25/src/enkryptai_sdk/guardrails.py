import os
# import requests
from .base import BaseClient
from .config import GuardrailsConfig
from .response import GuardrailsResponse, PIIResponse
from .dto import (
    GuardrailsHealthResponse,
    GuardrailsModelsResponse,
    # GuardrailDetectors,
    # GuardrailsDetectRequest,
    # GuardrailsBatchDetectRequest,
    # GuardrailsPolicyDetectRequest,
    # DetectResponseSummary,
    # DetectResponseDetails,
    GuardrailsDetectResponse,
    # BatchDetectResponseItem,
    GuardrailsBatchDetectResponse,
    # GuardrailsPIIRequest,
    GuardrailsPIIResponse,
    # GuardrailsHallucinationRequest,
    GuardrailsHallucinationResponse,
    # GuardrailsAdherenceRequest,
    GuardrailsAdherenceResponse,
    # GuardrailsRelevancyRequest,
    GuardrailsRelevancyResponse,
    # GuardrailsPolicyRequest,
    GuardrailsPolicyData,
    GuardrailsPolicyResponse,
    # GuardrailsDeletePolicyData,
    GuardrailsDeletePolicyResponse,
    GuardrailsListPoliciesResponse,
    GuardrailsPolicyAtomizerRequest,
    GuardrailsPolicyAtomizerResponse,
    GuardrailsScanUrlResponse
)

# ---------------------------------------
# TODO: Use DTOs for request data as well
# ---------------------------------------

class GuardrailsClientError(Exception):
    """
    A custom exception for GuardrailsClient errors.
    """

    pass


class GuardrailsClient(BaseClient):
    """
    A client for interacting with Enkrypt AI Guardrails API endpoints.
    """
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com:443"):
        super().__init__(api_key, base_url)

    # def __init__(self, api_key, base_url="https://api.enkryptai.com"):
    #     """
    #     Initializes the client.

    #     Parameters:
    #     - api_key (str): Your API key for authenticating with the service.
    #     - base_url (str): Base URL of the API (default: "https://api.enkryptai.com").
    #     """
    #     self.api_key = api_key
    #     self.base_url = base_url.rstrip('/')
    #     self.session = requests.Session()

    # def _request(self, method, endpoint, headers=None, **kwargs):
    #     """
    #     Internal helper to send an HTTP request.

    #     Automatically adds the API key to headers.
    #     """
    #     url = self.base_url + endpoint
    #     headers = headers or {}
    #     if 'apikey' not in headers:
    #         headers['apikey'] = self.api_key
            
    #     try:
    #         response = self.session.request(method, url, headers=headers, **kwargs)
    #         response.raise_for_status()
    #         return response.json()
        
    #     except Exception as e:
    #         print(e)
    #         return {"error": str(e)}

    # ----------------------------
    # Basic Guardrails Endpoints
    # ----------------------------

    def get_health(self):
        """
        Get the health status of the service.
        """
        try:
            response = self._request("GET", "/guardrails/health")
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsHealthResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def get_status(self):
        """
        Check if the API is up and running.
        """
        try:
            response = self._request("GET", "/guardrails/status")
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsHealthResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def get_models(self):
        """
        Retrieve the list of models loaded by the service.
        """
        try:
            response = self._request("GET", "/guardrails/models")
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsModelsResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def detect(self, text, config=None):
        """
        Detects prompt injection, toxicity, NSFW content, PII, hallucination, and more.

        Parameters:
        - text (str): The text to analyze.
        - guardrails_config (dict or GuardrailsConfig, optional): A configuration for detectors.
          If a GuardrailsConfig instance is provided, its underlying dictionary will be used.
          If not provided, defaults to injection attack detection only.

        Returns:
        - Response from the API.
        """
        # Use injection attack config by default if none provided
        if config is None:
            config = GuardrailsConfig.injection_attack()

        # Allow passing in either a dict or a GuardrailsConfig or GuardrailDetectors instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
        if hasattr(config, "to_dict"):
            config = config.to_dict()
            
        payload = {
            "text": text,
            "detectors": config
        }

        try:
            response = self._request("POST", "/guardrails/detect", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsDetectResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))
        
    def batch_detect(self, texts, config=None):
        """
        Detects prompt injection, toxicity, NSFW content, PII, hallucination, and more in batch.

        Parameters:
        - texts (list): A list of texts to analyze.
        - guardrails_config (dict or GuardrailsConfig, optional): A configuration for detectors.
          If a GuardrailsConfig instance is provided, its underlying dictionary will be used.
          If not provided, defaults to injection attack detection only.

        Returns:
        - Response from the API.
        """
        # Use injection attack config by default if none provided
        if config is None:
            config = GuardrailsConfig.injection_attack()

        # Allow passing in either a dict or a GuardrailsConfig or GuardrailDetectors instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
        if hasattr(config, "to_dict"):
            config = config.to_dict()
            
        payload = {
            "texts": texts,
            "detectors": config
        }

        try:
            response = self._request("POST", "/guardrails/batch/detect", json=payload)
            if isinstance(response, dict) and response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsBatchDetectResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))
        
    def policy_batch_detect(self, policy_name, texts):
        """
        Apply a specific policy to detect and filter content in multiple texts.
        
        Parameters:
        - policy_name (str): Name of the policy to apply
        - texts (list): A list of texts to analyze
        
        Returns:
        - GuardrailsBatchDetectResponse: Response from the API containing batch detection results
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {"texts": texts}

        try:
            response = self._request("POST", "/guardrails/policy/batch/detect", headers=headers, json=payload)
            if isinstance(response, dict) and response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsBatchDetectResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))
    
    def pii(self, text, mode="request", key="null", entities=None):
        """
        Detects Personally Identifiable Information (PII) and can de-anonymize it.
        """
        payload = {
            "text": text,
            "mode": mode,
            "key": key,
            "entities": entities
        }

        try:
            response = self._request("POST", "/guardrails/pii", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsPIIResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def hallucination(self, request_text, response_text, context=""):
        """
        Detects hallucination in the response text.
        """
        payload = {
            "request_text": request_text,
            "response_text": response_text,
            "context": context
        }

        try:
            response = self._request("POST", "/guardrails/hallucination", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsHallucinationResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))
        
    def adherence(self, llm_answer, context):
        """
        Check the adherence of an LLM answer to the provided context.
        """
        payload = {
            "llm_answer": llm_answer,
            "context": context
        }

        try:
            response = self._request("POST", "/guardrails/adherence", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsAdherenceResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def relevancy(self, question, llm_answer):
        """
        Check the relevancy of an LLM answer to the provided question.
        """
        payload = {
            "question": question,
            "llm_answer": llm_answer
        }

        try:
            response = self._request("POST", "/guardrails/relevancy", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsRelevancyResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def scan_url(self, url, config=None):
        """
        Scan a URL for security threats including injection attacks and policy violations.

        Parameters:
        - url (str): The URL to scan and analyze.
        - config (dict or GuardrailsConfig, optional): A configuration for detectors.
        If a GuardrailsConfig instance is provided, its underlying dictionary will be used.
        If not provided, defaults to injection attack and policy violation detection.

        Returns:
        - Response from the API.
        """
        # Use default config if none provided
        if config is None:
            config = {
                "injection_attack": {
                    "enabled": True
                },
                "policy_violation": {
                    "enabled": True,
                    "policy_text": "Detect any malicious text or injection attacks",
                    "need_explanation": True
                }
            }

        # Allow passing in either a dict or a GuardrailsConfig or GuardrailDetectors instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
        if hasattr(config, "to_dict"):
            config = config.to_dict()
            
        payload = {
            "url": url,
            "detectors": config
        }

        try:
            response = self._request("POST", "/guardrails/scan-url", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsScanUrlResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

        
    def policy_scan_url(self, policy_name, url):
        """
        Apply a specific policy to scan a URL for security threats.
        
        Parameters:
        - policy_name (str): Name of the policy to apply
        - url (str): The URL to scan and analyze
        
        Returns:
        - GuardrailsScanUrlResponse: Response from the API containing scan results
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {"url": url}

        try:
            response = self._request("POST", "/guardrails/policy/scan-url", headers=headers, json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsScanUrlResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    # ----------------------------
    # Guardrails Policy Endpoints
    # ----------------------------

    def add_policy(self, policy_name, config, description="guardrails policy"):
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
        if hasattr(config, "to_dict"):
            config = config.to_dict()
            
        payload = {
            "name": policy_name,
            "description": description,
            "detectors": config
        }

        try:
            response = self._request("POST", "/guardrails/add-policy", json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsPolicyResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def get_policy(self, policy_name):
        """
        Retrieve an existing policy by providing its header identifier.
        """
        headers = {"X-Enkrypt-Policy": policy_name}

        try:
            response = self._request("GET", "/guardrails/get-policy", headers=headers)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsPolicyData.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def modify_policy(self, policy_name, config, new_policy_name=None, description="guardrails policy"):
        """
        Modify an existing policy.
        """
        # Allow passing in either a dict or a GuardrailsConfig instance
        if hasattr(config, "as_dict"):
            config = config.as_dict()
        if hasattr(config, "to_dict"):
            config = config.to_dict()

        if new_policy_name is None:
            new_policy_name = policy_name

        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {
            "detectors": config,
            "name": new_policy_name,
            "description": description
        }

        try:
            response = self._request("PATCH", "/guardrails/modify-policy", headers=headers, json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsPolicyResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def delete_policy(self, policy_name):
        """
        Delete a policy.
        """
        headers = {"X-Enkrypt-Policy": policy_name}

        try:
            response = self._request("DELETE", "/guardrails/delete-policy", headers=headers)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsDeletePolicyResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def policy_detect(self, policy_name, text):
        """
        Apply a specific policy to detect and filter content.
        """
        headers = {"X-Enkrypt-Policy": policy_name}
        payload = {"text": text}

        try:
            response = self._request("POST", "/guardrails/policy/detect", headers=headers, json=payload)
            if response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsDetectResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

    def get_policy_list(self):
        """
        List all policies.
        """

        try:
            response = self._request("GET", "/guardrails/list-policies")
            if isinstance(response, dict) and response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
            return GuardrailsListPoliciesResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))
        
    def atomize_policy(self, file=None, text=None):
        """
        Atomize a policy from either a file or text input.

        Parameters:
        - file (str, optional): Path to the policy file
        - text (str, optional): Policy text content

        Returns:
        - GuardrailsPolicyAtomizerResponse

        Raises:
        - GuardrailsClientError: If validation fails or API returns an error
        """
        try:
            # Create and validate request
            request = GuardrailsPolicyAtomizerRequest(file=file, text=text)
            if not request.validate():
                raise GuardrailsClientError("Invalid request: Must provide either file or text. Not both.")

            # Prepare the request based on input type
            if file:
                # Normalize file path and check existence
                file_path = os.path.abspath(file)
                file_name = os.path.basename(file_path)
                print(f"File name: {file_name}")
                print(f"Reading file: {file_path}")

                if not os.path.exists(file_path):
                    raise GuardrailsClientError(f"File not found: {file_path}")

                # Check file extension
                if not file_path.lower().endswith('.pdf'):
                    raise GuardrailsClientError("Only PDF files are supported")
                                    
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    # Create form data with filename
                    form_data = {
                        'file': (file_name, file_content, 'application/pdf')
                    }
                    response = self._request(
                        "POST", 
                        "/guardrails/policy-atomizer", 
                        form_data=form_data
                    )
            else:
                form_data = {'text': text}
                response = self._request(
                    "POST", 
                    "/guardrails/policy-atomizer", 
                    form_data=form_data
                )

            if isinstance(response, dict) and response.get("error"):
                raise GuardrailsClientError(f"API Error: {str(response)}")
                
            return GuardrailsPolicyAtomizerResponse.from_dict(response)
        except Exception as e:
            raise GuardrailsClientError(str(e))

