from .base import BaseClient
from .dto import (
    # InputGuardrailBlockType,
    # OutputGuardrailBlockType,
    # InputGuardrailsAdditionalConfig,
    # OutputGuardrailsAdditionalConfig,
    # InputGuardrailsPolicy,
    # OutputGuardrailsPolicy,
    DeploymentInput,
    DeploymentAddTaskResponse,
    GetDeploymentResponse,
    ModifyDeploymentResponse,
    # DeleteDeploymentData,
    DeleteDeploymentResponse,
    # DeploymentSummary,
    DeploymentCollection,
)


class DeploymentClientError(Exception):
    pass


class DeploymentClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        super().__init__(api_key, base_url)

    def add_deployment(self, config: DeploymentInput):
        """
        Add a new deployment to the system.

        Args:
            config (DeploymentInput): Configuration object containing deployment details

        Returns:
            dict: Response from the API containing the added deployment details
        """
        headers = {"Content-Type": "application/json"}

        if isinstance(config, dict):
            config = DeploymentInput.from_dict(config)

        payload = config.to_dict()

        response = self._request(
            "POST", "/deployments/add-deployment", headers=headers, json=payload
        )
        if response.get("error"):
            raise DeploymentClientError(f"API Error: {str(response)}")
        return DeploymentAddTaskResponse.from_dict(response)

    def get_deployment(self, deployment_name: str, refresh_cache: bool = False):
        """
        Get detailed information for a specific deployment.

        Args:
            deployment_name (str): The name of the deployment
            refresh_cache (bool): Whether to refresh the cache

        Returns:
            dict: Response from the API containing the deployment information
        """
        headers = {"X-Enkrypt-Deployment": deployment_name}
        headers["X-Enkrypt-Refresh-Cache"] = "true" if refresh_cache else "false"
        response = self._request("GET", "/deployments/get-deployment", headers=headers)
        if response.get("error"):
            raise DeploymentClientError(f"API Error: {str(response)}")
        return GetDeploymentResponse.from_dict(response)
    
    def modify_deployment(self, deployment_name: str, config: DeploymentInput):
        """
        Modify an existing deployment in the system.

        Args:
            config (DeploymentInput): Configuration object containing deployment details

        Returns:
            dict: Response from the API containing the modified deployment details
        """
        headers = {"Content-Type": "application/json", "X-Enkrypt-Deployment": deployment_name}

        if isinstance(config, dict):
            config = DeploymentInput.from_dict(config)

        payload = config.to_dict()

        response = self._request(
            "PATCH", "/deployments/modify-deployment", headers=headers, json=payload
        )
        if response.get("error"):
            raise DeploymentClientError(f"API Error: {str(response)}")
        return ModifyDeploymentResponse.from_dict(response)

    def delete_deployment(self, deployment_name: str):
        """
        Delete a deployment from the system.

        Args:
            deployment_name (str): The name of the deployment

        Returns:
            dict: Response from the API containing the deployment deleted
        """
        headers = {"X-Enkrypt-Deployment": deployment_name}
        response = self._request("DELETE", "/deployments/delete-deployment", headers=headers)
        if response.get("error"):
            raise DeploymentClientError(f"API Error: {str(response)}")
        return DeleteDeploymentResponse.from_dict(response)

    def list_deployments(self):
        """
        Get a list of all available deployments.

        Returns:
            dict: Response from the API containing the list of deployments
        """

        response = self._request("GET", "/deployments/list-deployments")
        if response.get("error"):
            raise DeploymentClientError(f"API Error: {str(response)}")
        return DeploymentCollection.from_dict(response)
