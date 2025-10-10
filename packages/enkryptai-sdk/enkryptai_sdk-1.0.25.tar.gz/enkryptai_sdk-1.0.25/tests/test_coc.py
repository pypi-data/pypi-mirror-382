# python3 -m pytest -s ./test_coc.py # --maxfail=1

import os
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import CoCClient, CoCClientError

load_dotenv()

ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

policy_name = None
test_coc_policy_name = "Test CoC Policy"

example_coc_policy_text = """
The model should not provide medical advice when asked about health symptoms.
    The model should not promote violence or harm.
    The model must be respectful of users and their privacy.
    The model must not use hate speech or engage in discrimination.
"""

example_coc_policy_rules = "1. The assistant's response must not be relied upon as the sole basis for clinical decisions when providing healthcare information.\n2. Users must not request professional medical judgment from the assistant when seeking healthcare advice.\n3. The assistant's response must not provide personalized medical diagnoses, treatments, or advice when asked about health-related issues."


@pytest.fixture
def coc_client():
    # You'll want to use a test API key here
    # debug
    # print("\nCreating CoC client")
    # print("\nENKRYPT_API_KEY: ", ENKRYPT_API_KEY)
    # print("\nENKRYPT_BASE_URL: ", ENKRYPT_BASE_URL)
    return CoCClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


def test_add_coc_policy_with_text(coc_client):
    print("\n\nTesting CoC add policy with text input")
    
    response = coc_client.add_policy(policy_name=test_coc_policy_name,policy_rules=example_coc_policy_text, total_rules=3, policy_text=example_coc_policy_text)
    print("\nResponse from CoC add policy with text: ", response)
    
    assert response is not None
    policyData = response.data
    assert policyData is not None
    assert hasattr(policyData, "policy_id")
    atomized = policyData.get_rules_list()
    print("\nAtomized policy rules with text: ", atomized)
    assert hasattr(policyData, "policy_rules")
    assert len(atomized) > 0


def test_delete_coc_policy_with_text(coc_client):
    print("\n\nTesting CoC delete_policy with text")
    response = coc_client.delete_policy(policy_name=test_coc_policy_name)
    print("\nResponse from delete_policy with text: ", response)
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details deleted successfully"


def test_add_coc_policy_with_file(coc_client):
    print("\n\nTesting CoC add policy with file ../docs/healthcare_guidelines.pdf")

    policy_file = "../docs/healthcare_guidelines.pdf"
    
    response = coc_client.add_policy(policy_name=test_coc_policy_name,policy_rules=example_coc_policy_text, total_rules=3, policy_file=policy_file)
    print("\nResponse from CoC add policy with file: ", response)
    
    assert response is not None
    policyData = response.data
    assert policyData is not None
    assert hasattr(policyData, "policy_id")
    atomized = policyData.get_rules_list()
    print("\nAtomized policy rules with file: ", atomized)
    assert hasattr(policyData, "policy_rules")
    assert len(atomized) > 0


def test_get_coc_policy(coc_client):
    print("\n\nTesting get_coc_policy")
    # Now test the get_policy method
    policy = coc_client.get_policy(policy_name=test_coc_policy_name)
    assert policy is not None
    assert policy.name == test_coc_policy_name


def test_modify_coc_policy(coc_client):
    print("\n\nTesting modifying coc policy")

    policy_file = "../docs/healthcare_guidelines.pdf"

    response = coc_client.modify_policy(policy_name=test_coc_policy_name,policy_rules=example_coc_policy_text, total_rules=3, policy_file=policy_file)

    print("\nResponse from modifying policy: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details updated successfully"
    # assert hasattr(response, "data")
    policy_info = response.data
    assert policy_info is not None
    assert policy_info.name == test_coc_policy_name


def test_delete_coc_policy_with_file(coc_client):
    print("\n\nTesting CoC delete_policy with file")
    response = coc_client.delete_policy(policy_name=test_coc_policy_name)
    print("\nResponse from delete_policy with file: ", response)
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details deleted successfully"

