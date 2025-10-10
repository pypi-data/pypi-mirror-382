# import json
# import urllib3
from .base import BaseClient
from .models import ModelClient
from .datasets import DatasetClient
from .dto import (
    RedteamHealthResponse,
    RedTeamModelHealthConfig,
    RedTeamModelHealthConfigV3,
    RedteamModelHealthResponse,
    RedTeamConfig,
    RedTeamConfigWithSavedModel,
    RedTeamCustomConfig,
    RedTeamCustomConfigWithSavedModel,
    RedTeamCustomConfigV3,
    RedTeamCustomConfigWithSavedModelV3,
    RedTeamResponse,
    RedTeamResultSummary,
    RedTeamResultDetails,
    RedTeamTaskStatus,
    RedTeamTaskDetails,
    RedTeamTaskList,
    RedTeamRiskMitigationGuardrailsPolicyConfig,
    RedTeamRiskMitigationGuardrailsPolicyResponse,
    RedTeamRiskMitigationSystemPromptConfig,
    RedTeamRiskMitigationSystemPromptResponse,
    RedTeamFindingsResponse,
    RedTeamDownloadLinkResponse
)


class RedTeamClientError(Exception):
    """
    A custom exception for Red Team errors.
    """

    pass


class RedTeamClient(BaseClient):
    """
    A client for interacting with the Red Team API.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        super().__init__(api_key, base_url)

    # def get_model(self, model):
    #     models = self._request("GET", "/models/list-models")
    #     models = models["models"]
    #     for _model_data in models:
    #         if _model_data["model_saved_name"] == model:
    #             return _model_data["model_saved_name"]
    #     else:
    #         return None

    def get_health(self):
        """
        Get the health status of the service.
        """
        try:
            response = self._request("GET", "/redteam/health")
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedteamHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))

    def check_model_health(self, config: RedTeamModelHealthConfig):
        """
        Get the health status of a model.
        """
        try:
            config = RedTeamModelHealthConfig.from_dict(config)
            # Print the config as json string
            # print(f"Config: {json.dumps(config.to_dict(), indent=4)}")
            response = self._request("POST", "/redteam/model-health", json=config.to_dict())
            # if response.get("error"):
            if response.get("error") not in [None, ""]:
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedteamModelHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))
        
    def check_saved_model_health(self, model_saved_name: str, model_version: str):
        """
        Get the health status of a saved model.
        """
        try:
            headers = {
                "X-Enkrypt-Model": model_saved_name,
                "X-Enkrypt-Model-Version": model_version,
            }
            response = self._request("POST", "/redteam/model/model-health", headers=headers)
            # if response.get("error"):
            if response.get("error") not in [None, ""]:
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedteamModelHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))
    
    def check_model_health_v3(self, config: RedTeamModelHealthConfigV3):
        """
        Get the health status of a model using V3 format with endpoint_configuration.
        
        This method accepts endpoint_configuration (similar to add_custom_task) and
        converts it internally to target_model_configuration format for backend compatibility.
        
        Args:
            config (RedTeamModelHealthConfigV3): Configuration object containing endpoint_configuration
            
        Returns:
            RedteamModelHealthResponse: Response from the API containing health status
            
        Raises:
            RedTeamClientError: If there's an error from the API
        """
        try:
            config = RedTeamModelHealthConfigV3.from_dict(config)
            
            # Convert endpoint_configuration to target_model_configuration
            target_config = config.to_target_model_configuration()
            
            # Create the payload in the format expected by the backend
            payload = {
                "target_model_configuration": target_config.to_dict()
            }
            
            response = self._request("POST", "/redteam/model-health", json=payload)
            if response.get("error") not in [None, ""]:
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedteamModelHealthResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))

    def add_task(
        self,
        config: RedTeamConfig,
    ):
        """
        Add a new red teaming task.
        """
        config = RedTeamConfig.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            # "async": config.async_enabled,
            "dataset_name": config.dataset_name,
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        if config.target_model_configuration:
            payload["target_model_configuration"] = (
                config.target_model_configuration.to_dict()
            )
            # print(payload)
            response = self._request(
                "POST",
                "/redteam/v2/add-task",
                json=payload,
            )
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedTeamResponse.from_dict(response)
        else:
            raise RedTeamClientError(
                "Please provide a target model configuration"
            )

    def add_task_with_saved_model(
        self,
        config: RedTeamConfigWithSavedModel,
        model_saved_name: str,
        model_version: str,
    ):
        """
        Add a new red teaming task using a saved model.
        """
        if not model_saved_name:
            raise RedTeamClientError("Please provide a model_saved_name")
        
        if not model_version:
            raise RedTeamClientError("Please provide a model_version. Default is 'v1'")

        config = RedTeamConfigWithSavedModel.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            # "async": config.async_enabled,
            "dataset_name": config.dataset_name,
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        headers = {
            "X-Enkrypt-Model": model_saved_name,
            "X-Enkrypt-Model-Version": model_version,
            "Content-Type": "application/json",
        }
        response = self._request(
            "POST",
            "/redteam/v2/model/add-task",
            headers=headers,
            json=payload,
        )
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamResponse.from_dict(response)

    def add_custom_task(
        self,
        config: RedTeamCustomConfig,
        policy_name: str = None,
    ):
        """
        Add a new custom red teaming task.
        """
        headers = {
            "Content-Type": "application/json",
        }

        if policy_name is not None:
            headers["X-Enkrypt-Policy"] = policy_name

        config = RedTeamCustomConfig.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            # "async": config.async_enabled,
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        # Only add frameworks if provided and not empty
        if config.frameworks:
            payload["frameworks"] = config.frameworks

        if config.dataset_configuration:
            payload["dataset_configuration"] = DatasetClient.prepare_dataset_payload(
                config.dataset_configuration, True)
        else:
            raise RedTeamClientError(
                "Please provide a dataset configuration"
            )

        if config.endpoint_configuration:
            payload["endpoint_configuration"] = ModelClient.prepare_model_payload(
                config.endpoint_configuration, True)
            # print(payload)

            response = self._request(
                "POST",
                "/redteam/v2/add-custom-task",
                headers=headers,
                json=payload,
            )
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedTeamResponse.from_dict(response)
        else:
            raise RedTeamClientError(
                "Please provide a endpoint configuration"
            )

    def add_custom_task_with_saved_model(
        self,
        config: RedTeamCustomConfigWithSavedModel,
        model_saved_name: str,
        model_version: str,
        policy_name: str = None,
    ):
        """
        Add a new red teaming custom task using a saved model.
        """
        if not model_saved_name:
            raise RedTeamClientError("Please provide a model_saved_name")
        
        if not model_version:
            raise RedTeamClientError("Please provide a model_version. Default is 'v1'")

        config = RedTeamCustomConfigWithSavedModel.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            # "async": config.async_enabled,
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        # Only add frameworks if provided and not empty
        if config.frameworks:
            payload["frameworks"] = config.frameworks

        if config.dataset_configuration:
            payload["dataset_configuration"] = DatasetClient.prepare_dataset_payload(
                config.dataset_configuration, True)
        else:
            raise RedTeamClientError(
                "Please provide a dataset configuration"
            )

        headers = {
            "X-Enkrypt-Model": model_saved_name,
            "X-Enkrypt-Model-Version": model_version,
            "Content-Type": "application/json",
        }

        if policy_name is not None:
            headers["X-Enkrypt-Policy"] = policy_name

        response = self._request(
            "POST",
            "/redteam/v2/model/add-custom-task",
            headers=headers,
            json=payload,
        )
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamResponse.from_dict(response)

    def add_custom_task_v3(
        self,
        config: RedTeamCustomConfigV3,
        policy_name: str = None,
    ):
        """
        Add a new custom red teaming task with v3 attack methods format.
        
        V3 format supports nested attack methods:
        {
            "test_name": {
                "sample_percentage": 50,
                "attack_methods": {
                    "method_category": {
                        "method_name": {
                            "params": {}
                        }
                    }
                }
            }
        }
        """
        headers = {
            "Content-Type": "application/json",
        }

        if policy_name is not None:
            headers["X-Enkrypt-Policy"] = policy_name

        config = RedTeamCustomConfigV3.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        # Only add frameworks if provided and not empty
        if config.frameworks:
            payload["frameworks"] = config.frameworks

        if config.dataset_configuration:
            payload["dataset_configuration"] = DatasetClient.prepare_dataset_payload(
                config.dataset_configuration, True)
        else:
            raise RedTeamClientError(
                "Please provide a dataset configuration"
            )

        if config.endpoint_configuration:
            payload["endpoint_configuration"] = ModelClient.prepare_model_payload(
                config.endpoint_configuration, True)

            response = self._request(
                "POST",
                "/redteam/v3/add-custom-task",
                headers=headers,
                json=payload,
            )
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedTeamResponse.from_dict(response)
        else:
            raise RedTeamClientError(
                "Please provide a endpoint configuration"
            )

    def add_custom_task_with_saved_model_v3(
        self,
        config: RedTeamCustomConfigWithSavedModelV3,
        model_saved_name: str,
        model_version: str,
        policy_name: str = None,
    ):
        """
        Add a new red teaming custom task using a saved model with v3 attack methods format.
        
        V3 format supports nested attack methods:
        {
            "test_name": {
                "sample_percentage": 50,
                "attack_methods": {
                    "method_category": {
                        "method_name": {
                            "params": {}
                        }
                    }
                }
            }
        }
        """
        if not model_saved_name:
            raise RedTeamClientError("Please provide a model_saved_name")
        
        if not model_version:
            raise RedTeamClientError("Please provide a model_version. Default is 'v1'")

        config = RedTeamCustomConfigWithSavedModelV3.from_dict(config)
        test_configs = config.redteam_test_configurations.to_dict()
        # Remove None or empty test configurations
        test_configs = {k: v for k, v in test_configs.items() if v is not None}

        payload = {
            "test_name": config.test_name,
            "redteam_test_configurations": test_configs,
        }

        # Only add frameworks if provided and not empty
        if config.frameworks:
            payload["frameworks"] = config.frameworks

        if config.dataset_configuration:
            payload["dataset_configuration"] = DatasetClient.prepare_dataset_payload(
                config.dataset_configuration, True)
        else:
            raise RedTeamClientError(
                "Please provide a dataset configuration"
            )

        headers = {
            "X-Enkrypt-Model": model_saved_name,
            "X-Enkrypt-Model-Version": model_version,
            "Content-Type": "application/json",
        }

        if policy_name is not None:
            headers["X-Enkrypt-Policy"] = policy_name

        response = self._request(
            "POST",
            "/redteam/v3/model/add-custom-task",
            headers=headers,
            json=payload,
        )
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamResponse.from_dict(response)

    def status(self, task_id: str = None, test_name: str = None):
        """
        Get the status of a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to check status
            test_name (str, optional): The name of the test to check status

        Returns:
            dict: The task status information
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/task-status", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamTaskStatus.from_dict(response)

    def cancel_task(self, task_id: str = None, test_name: str = None):
        """
        Cancel a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to cancel
            test_name (str, optional): The name of the test to cancel

        Returns:
            dict: The cancellation response

        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        raise RedTeamClientError(
            "This feature is currently under development. Please check our documentation "
            "at https://docs.enkrypt.ai for updates or contact support@enkrypt.ai for assistance."
        )

        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")

        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("POST", "/redteam/cancel-task", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return response

    def get_task(self, task_id: str = None, test_name: str = None):
        """
        Get the status and details of a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to retrieve
            test_name (str, optional): The name of the test to retrieve

        Returns:
            dict: The task details and status
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/get-task", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        # print(f"RedTeamTaskDetails response: {response}")
        return RedTeamTaskDetails.from_dict(response["data"])

    def get_result_summary(self, task_id: str = None, test_name: str = None):
        """
        Get the summary of results for a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to get results for
            test_name (str, optional): The name of the test to get results for

        Returns:
            dict: The summary of the task results
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        response = self._request("GET", "/redteam/v3/results/summary", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        # print(f"Response: {response}")
        return RedTeamResultSummary.from_dict(response)
    
    def get_result_summary_test_type(self, task_id: str = None, test_name: str = None, test_type: str = None):
        """
        Get the summary of results for a specific red teaming task for a specific test type.

        Args:
            task_id (str, optional): The ID of the task to get results for
            test_name (str, optional): The name of the test to get results for
            test_type (str, optional): The type of test to get results for

        Returns:
            dict: The summary of the task results for the specified test type
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        if not test_type:
            raise RedTeamClientError("test_type must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        url = f"/redteam/v3/results/summary/{test_type}"
        response = self._request("GET", url, headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        # print(f"Response: {response}")
        return RedTeamResultSummary.from_dict(response)

    def get_result_details(self, task_id: str = None, test_name: str = None):
        """
        Get the detailed results for a specific red teaming task.

        Args:
            task_id (str, optional): The ID of the task to get detailed results for
            test_name (str, optional): The name of the test to get detailed results for

        Returns:
            dict: The detailed task results
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name
            
        response = self._request("GET", "/redteam/v3/results/details", headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamResultDetails.from_dict(response)
    
    def get_result_details_test_type(self, task_id: str = None, test_name: str = None, test_type: str = None):
        """
        Get the detailed results for a specific red teaming task for a specific test type.

        Args:
            task_id (str, optional): The ID of the task to get detailed results for
            test_name (str, optional): The name of the test to get detailed results for
            test_type (str, optional): The type of test to get detailed results for

        Returns:
            dict: The detailed task results
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        if not test_type:
            raise RedTeamClientError("test_type must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        url = f"/redteam/v3/results/details/{test_type}"
        response = self._request("GET", url, headers=headers)
        if response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamResultDetails.from_dict(response)

    def get_task_list(self, status: str = None):
        """
        Get a list of red teaming tasks.

        Args:
            status (str, optional): The status of the tasks to retrieve

        Returns:
            dict: The list of tasks
        """
        url = "/redteam/list-tasks"
        if status:
            url += f"?status={status}"

        response = self._request("GET", url)
        if isinstance(response, dict) and response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamTaskList.from_dict(response)

    def risk_mitigation_guardrails_policy(self, config: RedTeamRiskMitigationGuardrailsPolicyConfig):
        """
        Get the guardrails policy generated for risk mitigation.
        """
        config = RedTeamRiskMitigationGuardrailsPolicyConfig.from_dict(config)
        payload = config.to_dict()
        
        response = self._request("POST", "/redteam/risk-mitigation/guardrails-policy", json=payload)
        if isinstance(response, dict) and response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamRiskMitigationGuardrailsPolicyResponse.from_dict(response)

    def risk_mitigation_system_prompt(self, config: RedTeamRiskMitigationSystemPromptConfig):
        """
        Get the system prompt generated for risk mitigation.
        """
        config = RedTeamRiskMitigationSystemPromptConfig.from_dict(config)
        payload = config.to_dict()
        
        response = self._request("POST", "/redteam/risk-mitigation/system-prompt", json=payload)
        if isinstance(response, dict) and response.get("error"):
            raise RedTeamClientError(f"API Error: {str(response)}")
        return RedTeamRiskMitigationSystemPromptResponse.from_dict(response)

    def get_findings(self, redteam_summary):
        """
        Get findings and insights based on red team summary data.
        
        Parameters:
        - redteam_summary (dict or ResultSummary): Red team test summary data
        
        Returns:
        - RedTeamFindingsResponse: Response from the API containing findings
        """
        # Allow passing in either a dict or a ResultSummary instance
        if hasattr(redteam_summary, "to_dict"):
            redteam_summary = redteam_summary.to_dict()
            
        payload = {
            "redteam_summary": redteam_summary
        }

        try:
            response = self._request("POST", "/redteam/findings", json=payload)
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedTeamFindingsResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))

    def get_download_link(self, task_id: str = None, test_name: str = None):
        """
        Get a download link for red team test results.
        
        Args:
            task_id (str, optional): The ID of the task to get download link for
            test_name (str, optional): The name of the test to get download link for
            
        Returns:
            RedTeamDownloadLinkResponse: Response containing download link and expiry information
            
        Raises:
            RedTeamClientError: If neither task_id nor test_name is provided, or if there's an error from the API
        """
        if not task_id and not test_name:
            raise RedTeamClientError("Either task_id or test_name must be provided")
        
        headers = {}
        if task_id:
            headers["X-Enkrypt-Task-ID"] = task_id
        if test_name:
            headers["X-Enkrypt-Test-Name"] = test_name

        try:
            response = self._request("GET", "/redteam/download-link", headers=headers)
            if response.get("error"):
                raise RedTeamClientError(f"API Error: {str(response)}")
            return RedTeamDownloadLinkResponse.from_dict(response)
        except Exception as e:
            raise RedTeamClientError(str(e))
        