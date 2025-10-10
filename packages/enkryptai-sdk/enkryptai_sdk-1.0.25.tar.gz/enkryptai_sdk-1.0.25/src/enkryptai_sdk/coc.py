import os
# import requests
from .base import BaseClient
from .dto import (
    CoCPolicyData,
    CoCPolicyResponse,
    CoCDeletePolicyResponse,
    CoCListPoliciesResponse,
)


class CoCClientError(Exception):
    """
    A custom exception for CoCClient errors.
    """

    pass


class CoCClient(BaseClient):
    """
    A client for interacting with Enkrypt AI CoC API endpoints.
    """
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com:443"):
        super().__init__(api_key, base_url)

    def add_policy(self, policy_name, policy_rules=None, total_rules=None, policy_file=None, policy_text=None):
        """
        Create a new policy with policy_rules.
        
        Parameters:
        - policy_name (str): Name of the policy
        - policy_rules (List or Str): List of rules for the policy
        - total_rules (int): Total number of rules
        - policy_file (str, optional): Path to the policy file (PDF)
        - policy_text (str, optional): Policy text content

        Returns:
        - CoCPolicyResponse

        Raises:
        - CoCClientError: If validation fails or API returns an error
        """
        try:
            if not policy_file and not policy_text:
                raise CoCClientError("Must provide either policy_file or policy_text")
            if policy_file and policy_text:
                raise CoCClientError("Cannot provide both policy_file and policy_text")
            
            if isinstance(policy_rules, list):
                policy_rules = "\n".join(policy_rules)
            elif isinstance(policy_rules, str):
                policy_rules = policy_rules.strip()
            else:
                raise CoCClientError("policy_rules must be a string or list of strings")

            form_data = {
                'name': policy_name,
                'policy_rules': policy_rules,
                'total_rules': total_rules
            }

            if policy_file:
                # Normalize file path and check existence
                file_path = os.path.abspath(policy_file)
                file_name = os.path.basename(file_path)

                if not os.path.exists(file_path):
                    raise CoCClientError(f"File not found: {file_path}")

                # Check file extension
                if not file_path.lower().endswith('.pdf'):
                    raise CoCClientError("Only PDF files are supported")
                                    
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    form_data['policy_file'] = (file_name, file_content, 'application/pdf')
            else:
                form_data['policy_text'] = policy_text

            response = self._request(
                "POST",
                "/code-of-conduct/add-policy",
                form_data=form_data
            )

            if isinstance(response, dict) and response.get("error"):
                raise CoCClientError(f"API Error: {str(response)}")
                
            return CoCPolicyResponse.from_dict(response)
        except Exception as e:
            raise CoCClientError(str(e))
        
    def get_policy(self, policy_name):
        """
        Retrieve an existing policy by providing its header identifier.
        """
        headers = {"X-Enkrypt-Policy": policy_name}

        try:
            response = self._request("GET", "/code-of-conduct/get-policy", headers=headers)
            if response.get("error"):
                raise CoCClientError(f"API Error: {str(response)}")
            return CoCPolicyData.from_dict(response)
        except Exception as e:
            raise CoCClientError(str(e))

    def modify_policy(self, policy_name, policy_rules=None, total_rules=None, policy_file=None, policy_text=None):
        """
        Modify a policy with policy_rules.
        
        Parameters:
        - policy_name (str): Name of the policy
        - policy_rules (List or Str): List of rules for the policy
        - total_rules (int): Total number of rules
        - policy_file (str, optional): Path to the policy file (PDF)
        - policy_text (str, optional): Policy text content

        Returns:
        - CoCPolicyResponse

        Raises:
        - CoCClientError: If validation fails or API returns an error
        """
        try:
            if not policy_file and not policy_text:
                raise CoCClientError("Must provide either policy_file or policy_text")
            if policy_file and policy_text:
                raise CoCClientError("Cannot provide both policy_file and policy_text")
            
            if isinstance(policy_rules, list):
                policy_rules = "\n".join(policy_rules)
            elif isinstance(policy_rules, str):
                policy_rules = policy_rules.strip()
            else:
                raise CoCClientError("policy_rules must be a string or list of strings")

            form_data = {
                'name': policy_name,
                'policy_rules': policy_rules,
                'total_rules': total_rules
            }

            if policy_file:
                # Normalize file path and check existence
                file_path = os.path.abspath(policy_file)
                file_name = os.path.basename(file_path)

                if not os.path.exists(file_path):
                    raise CoCClientError(f"File not found: {file_path}")

                # Check file extension
                if not file_path.lower().endswith('.pdf'):
                    raise CoCClientError("Only PDF files are supported")
                                    
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    form_data['policy_file'] = (file_name, file_content, 'application/pdf')
            else:
                form_data['policy_text'] = policy_text

            headers = {"X-Enkrypt-Policy": policy_name}

            response = self._request(
                "PATCH",
                "/code-of-conduct/modify-policy",
                form_data=form_data,
                headers=headers
            )

            if isinstance(response, dict) and response.get("error"):
                raise CoCClientError(f"API Error: {str(response)}")
                
            return CoCPolicyResponse.from_dict(response)
        except Exception as e:
            raise CoCClientError(str(e))
    
    def delete_policy(self, policy_name):
        """
        Delete a policy.
        """
        headers = {"X-Enkrypt-Policy": policy_name}

        try:
            response = self._request("DELETE", "/code-of-conduct/delete-policy", headers=headers)
            if response.get("error"):
                raise CoCClientError(f"API Error: {str(response)}")
            return CoCDeletePolicyResponse.from_dict(response)
        except Exception as e:
            raise CoCClientError(str(e))

    def get_policy_list(self):
        """
        List all policies.
        """

        try:
            response = self._request("GET", "/code-of-conduct/list-policies")
            if isinstance(response, dict) and response.get("error"):
                raise CoCClientError(f"API Error: {str(response)}")
            return CoCListPoliciesResponse.from_dict(response)
        except Exception as e:
            raise CoCClientError(str(e))
