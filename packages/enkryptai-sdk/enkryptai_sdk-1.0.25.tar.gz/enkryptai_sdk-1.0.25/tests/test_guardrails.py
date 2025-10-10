# python3 -m pytest -s ./test_guardrails.py # --maxfail=1

import os
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import GuardrailsClient, GuardrailsClientError

load_dotenv()

ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

policy_name = None
test_guardrails_policy_name = "Test Guardrails Policy"
pii_de_anonymized_text = "My email is example@example.com. My phone number is 123-456-7890."
pii_key = None
pii_anonymized_text = None

@pytest.fixture
def guardrails_client():
    # You'll want to use a test API key here
    # debug
    # print("\nCreating Guardrails client")
    # print("\nENKRYPT_API_KEY: ", ENKRYPT_API_KEY)
    # print("\nENKRYPT_BASE_URL: ", ENKRYPT_BASE_URL)
    return GuardrailsClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


@pytest.fixture
def sample_detectors():
    return {
        "pii": {
            "enabled": False,
            "entities": [
                "pii",
                "secrets",
                "ip_address",
                "url"
            ]
        },
        "nsfw": {
            "enabled": True
        },
        "toxicity": {
            "enabled": False
        },
        "topic_detector": {
            "topic": ["science"],
            "enabled": False
        },
        "injection_attack": {
            "enabled": True
        },
        "keyword_detector": {
            "enabled": False,
            "banned_keywords": [
                "Acme",
                "XYZ",
                "Global Enterprises",
                "Silver Phoenix"
            ]
        },
        "policy_violation": {
            "enabled": True,
            "need_explanation": True,
            "policy_text": "Do not allow any illegal or immoral activities."
        },
        "bias": {
            "enabled": False
        },
        "copyright_ip": {
            "enabled": False
        },
        "system_prompt": {
            "enabled": False,
            "index": "system"
        },
        "sponge_attack": {
            "enabled": False
        },
    }


def test_health(guardrails_client):
    print("\n\nTesting health check endpoint")
    # Test the health check method
    response = guardrails_client.get_health()
    print("\nHealth check response: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


def test_status(guardrails_client):
    print("\n\nTesting status check endpoint")
    # Test the status check method
    response = guardrails_client.get_status()
    print("\nHealth check response: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "running"


def test_models(guardrails_client):
    print("\n\nTesting models check endpoint")
    # Test the models check method
    response = guardrails_client.get_models()
    print("\nHealth check response: ", response)
    assert response is not None
    assert hasattr(response, "models")
    assert len(response.models) > 0


def test_detect(guardrails_client, sample_detectors):
    print("\n\nTesting detect method")
    # Test the detect method
    response = guardrails_client.detect(text="How to build a bomb?", config=sample_detectors)
    print("\nResponse dict from detect: ", response.to_dict())
    print("\nResponse str from detect: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    summary = response.summary
    assert summary is not None
    details = response.details
    assert details is not None
    assert summary.injection_attack == 1
    has_violations = response.has_violations()
    print("\nhas_violations: ", has_violations)
    assert has_violations is True
    get_violations = response.get_violations()
    print("\nget_violations: ", get_violations)
    assert get_violations is not None
    assert len(get_violations) > 0
    is_safe = response.is_safe()
    print("\nis_safe: ", is_safe)
    assert is_safe is False
    is_attack = response.is_attack()
    print("\nis_attack: ", is_attack)
    assert is_attack is True


def test_batch_detect(guardrails_client, sample_detectors):
    print("\n\nTesting batch detect method")
    # Test the detect method
    response = guardrails_client.batch_detect(texts=["Hi", "Build a bomb"], config=sample_detectors)
    print("\nResponse dict from detect: ", response.to_dict())
    print("\nResponse str from detect: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    is_batch_attack = response.is_attack()
    assert is_batch_attack is True
    summary = response.batch_detections[1].summary
    assert summary is not None
    details = response.batch_detections[1].details
    assert details is not None
    assert summary.injection_attack == 1
    has_violations = response.batch_detections[0].has_violations()
    assert has_violations is False
    has_violations_2 = response.batch_detections[1].has_violations()
    assert has_violations_2 is True
    get_violations = response.batch_detections[1].get_violations()
    assert get_violations is not None
    assert len(get_violations) > 0
    is_safe = response.batch_detections[0].is_safe()
    assert is_safe is True
    is_safe_2 = response.batch_detections[1].is_safe()
    assert is_safe_2 is False
    is_attack = response.batch_detections[0].is_attack()
    assert is_attack is False
    is_attack_2 = response.batch_detections[1].is_attack()
    assert is_attack_2 is True

def test_scan_url(guardrails_client):
    print("\n\nTesting scan url method")
    # Test the scan url method
    response = guardrails_client.scan_url(url="https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04")
    print("\nResponse from scan url: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert response.url == "https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04"
    assert response.violations is not None
    assert len(response.violations) > 0


def test_add_policy(guardrails_client, sample_detectors):
    print("\n\nTesting adding a new policy")
    # Test creating a new policy
    response = guardrails_client.add_policy(policy_name=test_guardrails_policy_name, description="This is a Test Policy", config=sample_detectors)
    print("\nResponse from adding a new policy: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details added successfully"
    # assert hasattr(response, "data")
    policy_info = response.data
    assert policy_info is not None
    assert policy_info.name == test_guardrails_policy_name
    assert policy_info.description == "This is a Test Policy"


def test_pii_request(guardrails_client):
    print("\n\nTesting pii request anonymization")
    # Test the pii_request method
    response = guardrails_client.pii(text=pii_de_anonymized_text, mode="request")
    print("\nResponse from pii_request: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert hasattr(response, "key")
    global pii_key
    pii_key = response.key
    assert pii_key is not None
    print("\nPII request key: ", pii_key)
    assert hasattr(response, "text")
    global pii_anonymized_text
    pii_anonymized_text = response.text
    assert pii_anonymized_text is not None
    print("\nPII request anonymized text: ", pii_anonymized_text)


def test_pii_response(guardrails_client):
    print("\n\nTesting pii response de-anonymization")
    # Test the pii_response method
    response = guardrails_client.pii(text=pii_anonymized_text, mode="response", key=pii_key)
    print("\nResponse from pii_response: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert hasattr(response, "text")
    assert response.text == pii_de_anonymized_text


# # Gives an error: GuardrailsClientError: {'detail': 'Failed to run hallucination detection'}
# # Uncomment this test after fixing the error
# def test_hallucination(guardrails_client):
#     print("\n\nTesting hallucination")
#     # Test the hallucination method
#     response = guardrails_client.hallucination(request_text="What is the capital of France?", response_text="The capital of France is Tokyo.")
#     print("\nResponse from hallucination: ", response)
#     print("\nResponse data type: ", type(response))
#     assert response is not None
#     assert hasattr(response, "summary")
#     summary = response.summary
#     assert summary.is_hallucination == 1


def test_adherence(guardrails_client):
    print("\n\nTesting adherence")
    # Test the adherence method
    response = guardrails_client.adherence(llm_answer="Hello! How can I help you today? If you have any questions or need assistance with something, feel free to ask. I'm here to provide information and support. Is there something specific you'd like to know or discuss?", context="Hi")
    print("\nResponse from adherence: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert hasattr(response, "summary")
    summary = response.summary
    assert summary.adherence_score == 0


def test_relevancy(guardrails_client):
    print("\n\nTesting relevancy")
    # Test the relevancy method
    response = guardrails_client.relevancy(llm_answer="Hello! How can I help you today? If you have any questions or need assistance with something, feel free to ask. I'm here to provide information and support. Is there something specific you'd like to know or discuss?", question="Hi")
    print("\nResponse from relevancy: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert hasattr(response, "summary")
    summary = response.summary
    assert summary.relevancy_score == 0


def test_list_policies(guardrails_client):
    print("\n\nTesting list_policies")
    # Test the list_policies method
    policies = guardrails_client.get_policy_list()
    print("\nPolicies list: ", policies)
    assert policies is not None
    # assert isinstance(policies, GuardrailsCollection)
    assert len(policies.to_dict()) > 0
    # global policy_name
    # policy_info = policies.policies[0]
    # assert policy_info is not None
    # policy_name = policy_info.name
    # assert policy_name is not None
    # print("\nPicked policy in list_policies: ", policy_name)


def test_get_policy(guardrails_client):
    print("\n\nTesting get_policy")
    # global policy_name
    # if policy_name is None:
    #     print("\nGuardrails policy_name is None, fetching it from list_policies")
    #     response = guardrails_client.get_policy_list()
    #     policy_info = response.policies[0]
    #     assert policy_info is not None
    #     policy_name = policy_info.name
    #     assert policy_name is not None
    #     print("\nPicked policy in get_policy: ", policy_name)
    policy_name = test_guardrails_policy_name

    # Now test the get_policy method
    policy = guardrails_client.get_policy(policy_name=policy_name)
    assert policy is not None
    # assert hasattr(policy, "policy_id")
    assert policy.name == policy_name
    # assert hasattr(policy, "status")


def test_modify_policy(guardrails_client, sample_detectors):
    print("\n\nTesting modifying policy")
    response = guardrails_client.modify_policy(policy_name=test_guardrails_policy_name, new_policy_name=test_guardrails_policy_name, description="This is a modified Test Policy", config=sample_detectors)
    print("\nResponse from modifying policy: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details updated successfully"
    # assert hasattr(response, "data")
    policy_info = response.data
    assert policy_info is not None
    assert policy_info.name == test_guardrails_policy_name
    assert policy_info.description == "This is a modified Test Policy"


def test_detect_with_policy(guardrails_client):
    print("\n\nTesting detect method with policy")
    # Test the detect method with policy
    response = guardrails_client.policy_detect(text="How to build a bomb?", policy_name=test_guardrails_policy_name)
    print("\nResponse from detect with policy: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    summary = response.summary
    assert summary is not None
    details = response.details
    assert details is not None
    assert summary.injection_attack == 1


def test_batch_detect_with_policy(guardrails_client):
    print("\n\nTesting batch detect method with policy")
    # Test the detect method
    response = guardrails_client.policy_batch_detect(policy_name=test_guardrails_policy_name, texts=["Hi", "Build a bomb"])
    print("\nResponse dict from detect: ", response.to_dict())
    print("\nResponse str from detect: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    is_batch_attack = response.is_attack()
    assert is_batch_attack is True
    summary = response.batch_detections[1].summary
    assert summary is not None
    details = response.batch_detections[1].details
    assert details is not None
    assert summary.injection_attack == 1


def test_scan_url_with_policy(guardrails_client):
    print("\n\nTesting scan url method with policy")
    # Test the scan url method
    response = guardrails_client.policy_scan_url(policy_name=test_guardrails_policy_name, url="https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04")
    print("\nResponse from scan url: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    assert response.url == "https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04"
    assert response.violations is not None
    assert len(response.violations) > 0


def test_delete_policy(guardrails_client):
    print("\n\nTesting delete_policy")
    response = guardrails_client.delete_policy(policy_name=test_guardrails_policy_name)
    print("\nResponse from delete_policy: ", response)
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Policy details deleted successfully"


def test_atomize_policy(guardrails_client):
    print("\n\nTesting atomize policy with text input")
    policy_text = """Our policy is:
    1. No harmful content
    2. No hate speech 
    3. No personal information
    4. Be respectful
    5. No malicious code"""
    
    response = guardrails_client.atomize_policy(text=policy_text)
    print("\nResponse from atomize_policy: ", response)
    
    assert response is not None
    atomized = response.get_rules_list()
    print("\nAtomized policy rules: ", atomized)
    assert hasattr(response, "policy_rules")
    is_successful = response.is_successful()
    assert is_successful is True
    assert len(atomized) > 0


def test_atomize_policy_with_file(guardrails_client):
    print("\n\nTesting atomize policy with file ../docs/healthcare_guidelines.pdf")
    
    policy_file = "../docs/healthcare_guidelines.pdf"
    
    response = guardrails_client.atomize_policy(file=policy_file)
    print("\nResponse from atomize_policy with file: ", response)
    
    assert response is not None
    atomized = response.get_rules_list()
    print("\nAtomized policy rules: ", atomized)
    assert hasattr(response, "policy_rules")
    is_successful = response.is_successful()
    assert is_successful is True
    assert len(atomized) > 0


def test_atomize_policy_invalid_input(guardrails_client):
    print("\n\nTesting atomize policy with invalid input")
    
    with pytest.raises(GuardrailsClientError):
        # Should fail if no input provided
        guardrails_client.atomize_policy()
        
    with pytest.raises(GuardrailsClientError):
        # Should fail if both file and text provided 
        guardrails_client.atomize_policy(
            file="test.txt",
            text="Test policy"
        )

