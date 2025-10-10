from .base import BaseClient
from .dto import (
    DatasetConfig,
    DatasetCollection,
    DatasetSummary,
    DatasetResponse,
    DatasetCard,
    DatasetTaskStatus,
    DatasetTask,
    DatasetAddTaskResponse,
)


class DatasetClientError(Exception):
    pass


class DatasetClient(BaseClient):
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        super().__init__(api_key, base_url)

    @staticmethod
    def prepare_dataset_payload(config: DatasetConfig | dict, is_custom: bool = False) -> dict:
        """
        Prepare the payload for dataset operations from a config object.
        
        Args:
            config (Union[DatasetConfig, dict]): Configuration object or dictionary containing dataset details
            
        Returns:
            dict: Processed payload ready for API submission
        """
        if isinstance(config, dict):
            config = DatasetConfig.from_dict(config)
        
        payload = config.to_dict()

        if not is_custom:
            # Remove empty tools configuration
            if (payload.get("tools") is None or 
                payload["tools"] == [] or 
                payload["tools"] == [{}] or
                payload["tools"] == [{"name": "", "description": ""}]):
                del payload["tools"]
        
        return payload

    def add_dataset(self, config: DatasetConfig):
        """
        Add a new dataset to the system.

        Args:
            config (DatasetConfig): Configuration object containing dataset details

        Returns:
            dict: Response from the API containing the added dataset details
        """
        headers = {"Content-Type": "application/json"}

        if isinstance(config, dict):
            config = DatasetConfig.from_dict(config)

        payload = self.prepare_dataset_payload(config)

        # Print payload
        # print(f"\nAdd Dataset Payload: {payload}")

        response = self._request(
            "POST", "/datasets/add-task", headers=headers, json=payload
        )

        # Print response
        # print(f"\nAdd Dataset Response: {response}")

        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        return DatasetAddTaskResponse.from_dict(response)
    
    def get_dataset_task_status(self, dataset_name: str):
        """
        Get dataset task status for a specific dataset task.

        Args:
            dataset_name (str): The name of the dataset

        Returns:
            dict: Response from the API containing the dataset task status
        """
        headers = {"X-Enkrypt-Dataset": dataset_name}
        response = self._request("GET", "/datasets/task-status", headers=headers)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        response["dataset_name"] = dataset_name
        return DatasetTaskStatus.from_dict(response)

    def get_dataset_task(self, dataset_name: str):
        """
        Get detailed information for a specific dataset task.

        Args:
            dataset_name (str): The name of the dataset

        Returns:
            dict: Response from the API containing the dataset task information
        """
        headers = {"X-Enkrypt-Dataset": dataset_name}
        response = self._request("GET", "/datasets/get-task", headers=headers)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        response["dataset_name"] = dataset_name
        return DatasetTask.from_dict(response)

    def get_datacard(self, dataset_name: str):
        """
        Get datacard information for a specific dataset.

        Args:
            dataset_name (str): The name of the dataset

        Returns:
            dict: Response from the API containing the datacard information
        """
        headers = {"X-Enkrypt-Dataset": dataset_name}
        response = self._request("GET", "/datasets/get-datacard", headers=headers)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        response["dataset_name"] = dataset_name
        return DatasetCard.from_dict(response)

    def get_dataset(self, dataset_name: str):
        """
        Get detailed information for a specific dataset.

        Args:
            dataset_name (str): The name of the dataset

        Returns:
            dict: Response from the API containing the dataset information
        """
        headers = {"X-Enkrypt-Dataset": dataset_name}
        response = self._request("GET", "/datasets/get-dataset", headers=headers)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        response["dataset_name"] = dataset_name
        return DatasetResponse.from_dict(response)

    def get_summary(self, dataset_name: str):
        """
        Get summary information for a specific dataset.

        Args:
            dataset_name (str): The name of the dataset

        Returns:
            dict: Response from the API containing the dataset summary
        """
        headers = {"X-Enkrypt-Dataset": dataset_name}
        response = self._request("GET", "/datasets/get-summary", headers=headers)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        response["dataset_name"] = dataset_name
        return DatasetSummary.from_dict(response)

    def list_datasets(self, status: str = None):
        """
        Get a list of all available dataset tasks.

        Args:
            status (str): Filter the list of dataset tasks by status

        Returns:
            dict: Response from the API containing the list of dataset tasks
        """

        url = "/datasets/list-tasks"
        if status:
            url += f"?status={status}"
        response = self._request("GET", url)
        if response.get("error"):
            raise DatasetClientError(f"API Error: {str(response)}")
        return DatasetCollection.from_dict(response)
