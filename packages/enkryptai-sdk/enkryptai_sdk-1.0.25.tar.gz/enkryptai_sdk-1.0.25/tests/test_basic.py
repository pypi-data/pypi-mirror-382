import os
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import GuardrailsClient, GuardrailsConfig

load_dotenv()

# Dummy API key and base URL for local testing.
# For real testing, you might mock requests or use a staging endpoint.
API_KEY = os.getenv("ENKRYPTAI_API_KEY")
BASE_URL = os.getenv("ENK_BASE_URL", "https://api.enkryptai.com")

@pytest.fixture
def client():
    return GuardrailsClient(api_key=API_KEY, base_url=BASE_URL)

# def test_health(client):
#     print("\n\nTesting Guardrails health")
#     # Since we're using a dummy API key, you might want to mock the response.
#     # For now, let's just check that the client object has been created.
#     assert hasattr(client, "health")

def test_config_injection_attack():
    print("\n\nTesting Guardrails injection attack config")
    # Test that the injection attack preset returns a valid configuration.
    config = GuardrailsConfig.injection_attack()
    config_dict = config.as_dict()
    print("\nGuardrails injection attack Config Dict: ", config_dict)
    assert config_dict["injection_attack"]["enabled"] is True

def test_config_topic_detector():
    print("\n\nTesting Guardrails topic detector config")
    # Test that the topic detector preset returns a valid configuration.
    config = GuardrailsConfig.topic(topics=["science", "technology"])
    config_dict = config.as_dict()
    print("\nGuardrails topic detector Config Dict: ", config_dict)
    assert config_dict["topic_detector"]["enabled"] is True
    assert "science" in config_dict["topic_detector"]["topic"]

def test_policy_violation_config():
    print("\n\nTesting Guardrails policy violation config")
    policy_text = "Test Guardrails Policy"
    config = GuardrailsConfig.policy_violation(policy_text)
    config_dict = config.as_dict()
    print("\nGuardrails policy violation Config Dict: ", config_dict)
    assert config_dict["policy_violation"]["enabled"] is True
    assert config_dict["policy_violation"]["policy_text"] == policy_text
