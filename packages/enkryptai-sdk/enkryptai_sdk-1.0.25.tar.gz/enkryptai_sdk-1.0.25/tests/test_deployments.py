import os
import uuid
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import DeploymentClient, DeploymentClientError

load_dotenv()

ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

# python3 -m pytest -s ./test_deployments.py --maxfail=1

policy_name = "Test Guardrails Policy"
deployment_name = "test-deployment"
model_saved_name = "Test Model"
model_version = "v1"

@pytest.fixture
def deployment_client():
    # You'll want to use a test API key here
    print("\nCreating Deployment Client")
    # Debug print statements
    # print("\nENKRYPT_API_KEY: ", ENKRYPT_API_KEY)
    print("\nENKRYPT_BASE_URL: ", ENKRYPT_BASE_URL)
    return DeploymentClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


@pytest.fixture
def sample_deployment_config():
    return {
        # "name": f"test-deployment-{str(uuid.uuid4())[:8]}",
        "name": deployment_name,
        "model_saved_name": model_saved_name,
        "model_version": model_version,
        "input_guardrails_policy": {
            "policy_name": policy_name,
            "enabled": True,
            "additional_config": {
                "pii_redaction": False
            },
            "block": [
                "injection_attack",
                "policy_violation"
            ]
        },
        "output_guardrails_policy": {
            "policy_name": policy_name,
            "enabled": False,
            "additional_config": {
                "hallucination": False,
                "adherence": False,
                "relevancy": False
            },
            "block": [
                "nsfw"
            ]
        },
    }


def test_add_deployment_success(deployment_client, sample_deployment_config):
    print("\n\nTesting add_deployment")
    response = deployment_client.add_deployment(config=sample_deployment_config)
    print("\nResponse from add_deployment: ", response)
    assert response is not None
    assert hasattr(response, "from_dict")
    assert response.message == "Deployment details added successfully"


def test_list_deployments(deployment_client):
    print("\n\nTesting list_deployments")
    # Now test the list_deployments method
    deployments = deployment_client.list_deployments()
    deployments = deployments.to_dict()
    print("\nList Deployments response: ", deployments)
    assert deployments is not None
    assert isinstance(deployments, dict)
    assert len(deployments) > 0


def test_get_deployment(deployment_client):
    print("\n\nTesting get_deployment")
    # Now test the get_deployment method
    deployment = deployment_client.get_deployment(deployment_name=deployment_name)
    deployment = deployment.to_dict()
    print("\nGet Deployment response: ", deployment)
    assert deployment is not None
    assert isinstance(deployment, dict)
    assert deployment["name"] == deployment_name

def test_modify_deployment(deployment_client, sample_deployment_config):
    print("\n\nTesting modify_deployment")
    response = deployment_client.modify_deployment(deployment_name=deployment_name, config=sample_deployment_config)
    print("\nResponse from modify_deployment: ", response)
    assert response is not None
    assert hasattr(response, "from_dict")
    assert response.message == "Deployment details updated successfully"

def test_delete_deployment(deployment_client):
    print("\n\nTesting delete_deployment")
    response = deployment_client.delete_deployment(deployment_name=deployment_name)
    print("\nResponse from delete_deployment: ", response)
    assert response is not None
    assert hasattr(response, "from_dict")
    assert response.message == "Deployment details deleted successfully"
