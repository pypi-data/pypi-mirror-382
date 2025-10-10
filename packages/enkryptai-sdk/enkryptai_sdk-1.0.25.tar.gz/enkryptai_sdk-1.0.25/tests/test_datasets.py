import os
import time
import uuid
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import DatasetClient, DatasetClientError

load_dotenv()

ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

dataset_name = None
picked_dataset_name = None

@pytest.fixture
def dataset_client():
    # You'll want to use a test API key here
    return DatasetClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


@pytest.fixture
def sample_dataset_config():
    print("\nCreating sample dataset config")
    global dataset_name
    dataset_name = f"TestElectionDataset-{str(uuid.uuid4())[:8]}"
    print("\nDataset Name: ", dataset_name)
    return {
        "dataset_name": dataset_name,
        # "dataset_name": "TestElectionDataset",
        "system_description": "- **Voter Eligibility**: To vote in U.S. elections, individuals must be U.S. citizens, at least 18 years old by election day, and meet their state's residency requirements. - **Voter Registration**: Most states require voters to register ahead of time, with deadlines varying widely. North Dakota is an exception, as it does not require voter registration. - **Identification Requirements**: Thirty-six states enforce voter ID laws, requiring individuals to present identification at polling places. These laws aim to prevent voter fraud but can also lead to disenfranchisement. - **Voting Methods**: Voters can typically choose between in-person voting on election day, early voting, and absentee or mail-in ballots, depending on state regulations. - **Polling Hours**: Polling hours vary by state, with some states allowing extended hours for voters. Its essential for voters to check local polling times to ensure they can cast their ballots. - **Provisional Ballots**: If there are questions about a voter's eligibility, they may be allowed to cast a provisional ballot. This ballot is counted once eligibility is confirmed. - **Election Day Laws**: Many states have laws that protect the rights of voters on election day, including prohibiting intimidation and ensuring access to polling places. - **Campaign Finance Regulations**: Federal and state laws regulate contributions to candidates and political parties to ensure transparency and limit the influence of money in politics. - **Political Advertising**: Campaigns must adhere to rules regarding political advertising, including disclosure requirements about funding sources and content accuracy. - **Voter Intimidation Prohibitions**: Federal laws prohibit any form of voter intimidation or coercion at polling places, ensuring a safe environment for all voters. - **Accessibility Requirements**: The Americans with Disabilities Act mandates that polling places be accessible to individuals with disabilities, ensuring equal access to the electoral process. - **Election Monitoring**: Various organizations are allowed to monitor elections to ensure compliance with laws and regulations. They help maintain transparency and accountability in the electoral process. - **Vote Counting Procedures**: States have specific procedures for counting votes, including the use of electronic voting machines and manual audits to verify results. - **Ballot Design Standards**: States must adhere to certain design standards for ballots to ensure clarity and prevent confusion among voters when casting their votes. - **Post-Election Audits**: Some states conduct post-election audits as a measure of accuracy. These audits help verify that the vote count reflects the actual ballots cast.",
        "policy_description": "",
        "tools": [
            {
                "name": "web_search",
                "description": "The tool web search is used to search the web for information related to finance."
            }
        ],
        "info_pdf_url": "",
        "max_prompts": 100,
        "scenarios": 2,
        "categories": 2,
        "depth": 2
    }


def get_dataset_name_from_list(dataset_client, status=None):
    """Helper function to get a dataset name from the datasets list.
    
    Args:
        dataset_client: The DatasetClient instance
        status: Optional status filter (e.g., "Finished", "Running")
    
    Returns:
        str: A dataset name from the datasets list
    """
    print(f"\nFetching dataset with status: {status if status else 'Finished'}")
    datasets = dataset_client.list_datasets(status=status)
    datasets_dict = datasets.to_dict()
    print(f"\nDatasets list retrieved with {len(datasets_dict.get('datasets', []))} datasets")
    
    if not datasets_dict.get("datasets"):
        # If no datasets with specified status, try without status filter
        if status:
            print(f"\nNo datasets with status '{status}', fetching any dataset")
            datasets = dataset_client.list_datasets()
            datasets_dict = datasets.to_dict()
    
    if not datasets_dict.get("datasets"):
        return None
    
    dataset_name = datasets_dict["datasets"][0]
    print(f"\nSelected dataset: {dataset_name}")
    return dataset_name


def test_add_dataset_success(dataset_client, sample_dataset_config):
    print("\n\nTesting add_dataset")
    response = dataset_client.add_dataset(config=sample_dataset_config)
    print("\nAdd Dataset Response: ", response)
    assert response is not None
    assert hasattr(response, "task_id")
    assert hasattr(response, "message")
    response.message == "Dataset task has been added successfully"
    # Sleep for a while to let the task complete
    # This is also useful to avoid rate limiting issues
    print("\nSleeping for 60 seconds to let the task complete if possible ...")
    time.sleep(60)


def test_list_datasets(dataset_client):
    print("\n\nTesting list_datasets")
    # Test the list_datasets method
    datasets = dataset_client.list_datasets(status="Finished")
    datasets_dict = datasets.to_dict()
    print("\nList Datasets Response: ", datasets_dict)
    assert datasets_dict is not None
    assert isinstance(datasets_dict, dict)
    
    # Get a dataset name using our helper function
    global picked_dataset_name
    if picked_dataset_name is None:
        picked_dataset_name = get_dataset_name_from_list(dataset_client, status="Finished")
    assert picked_dataset_name is not None
    print(f"\nSelected dataset for further tests: {picked_dataset_name}")


def test_get_dataset_task(dataset_client):
    print("\n\nTesting get_dataset_task")
    global picked_dataset_name
    if picked_dataset_name is None:
        picked_dataset_name = get_dataset_name_from_list(dataset_client, status="Finished")
    assert picked_dataset_name is not None
    print(f"\nSelected dataset for further tests: {picked_dataset_name}")

    # Now test the get_dataset_task method
    dataset_task = dataset_client.get_dataset_task(dataset_name=picked_dataset_name)
    print("\nDataset Task: ", dataset_task)
    assert dataset_task is not None
    assert hasattr(dataset_task, "dataset_name")
    assert dataset_task.dataset_name == picked_dataset_name
    assert hasattr(dataset_task, "data")
    data = dataset_task.data
    assert data is not None
    assert hasattr(data, "status")
    status = data.status
    assert status is not None
    print("\nDataset Task Status: ", status)


def test_get_dataset_task_status(dataset_client):
    print("\n\nTesting get_dataset_task_status")
    global picked_dataset_name
    if picked_dataset_name is None:
        picked_dataset_name = get_dataset_name_from_list(dataset_client, status="Finished")
    assert picked_dataset_name is not None
    print(f"\nSelected dataset for further tests: {picked_dataset_name}")

    # Now test the get_dataset_task_status method
    dataset_task_status = dataset_client.get_dataset_task_status(dataset_name=picked_dataset_name)
    print("\nDataset Task Status: ", dataset_task_status)
    assert dataset_task_status is not None
    assert hasattr(dataset_task_status, "dataset_name")
    assert dataset_task_status.dataset_name == picked_dataset_name
    assert hasattr(dataset_task_status, "status")


def test_get_datacard(dataset_client):
    print("\n\nTesting get_datacard")
    global picked_dataset_name
    if picked_dataset_name is None:
        picked_dataset_name = get_dataset_name_from_list(dataset_client, status="Finished")
    assert picked_dataset_name is not None
    print(f"\nSelected dataset for further tests: {picked_dataset_name}")

    # Now test the get_datacard method
    datacard = dataset_client.get_datacard(dataset_name=picked_dataset_name)
    print("\nDatacard: ", datacard)
    assert datacard is not None
    # # Dataset might not be generated yet
    # # TODO: How to handle this?
    # assert hasattr(datacard, "dataset_name")
    # assert datacard.dataset_name == picked_dataset_name
    # assert hasattr(datacard, "description")


def test_get_summary(dataset_client):
    print("\n\nTesting get_summary")
    global picked_dataset_name
    if picked_dataset_name is None:
        picked_dataset_name = get_dataset_name_from_list(dataset_client, status="Finished")
    assert picked_dataset_name is not None
    print(f"\nSelected dataset for further tests: {picked_dataset_name}")

    # Now test the get_summary method
    summary = dataset_client.get_summary(dataset_name=picked_dataset_name)
    print("\nsummary: ", summary)
    assert summary is not None
    # # Dataset might not be generated yet
    # # TODO: How to handle this?
    # assert hasattr(summary, "dataset_name")
    # assert summary.dataset_name == picked_dataset_name
    # assert hasattr(summary, "test_types")
