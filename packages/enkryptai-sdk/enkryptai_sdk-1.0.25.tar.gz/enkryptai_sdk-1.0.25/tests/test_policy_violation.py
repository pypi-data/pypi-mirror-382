import os
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import GuardrailsClient, GuardrailsConfig

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv("ENKRYPTAI_API_KEY")
if not API_KEY:
    pytest.skip("ENKRYPTAI_API_KEY not set in environment variables.")

ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

def test_policy_violation_detector():
    """
    Test the policy violation detector using the /guardrails/detect endpoint.
    """
    client = GuardrailsClient(api_key=API_KEY, base_url=ENKRYPT_BASE_URL)

    print("\n\nTesting policy violation detection")
    
    # Use the policy violation preset with a custom policy text.
    config = GuardrailsConfig.policy_violation("No rude content or hate speech allowed")
    
    # Sample text that might trigger policy violation detection.
    sample_text = "I hate all people and I will destroy everything."
    
    # Make the actual API call using the detect endpoint.
    response = client.detect(text=sample_text, config=config)
    
    # Print the response for debugging.
    print("\nResponse from policy violation detection: ", response)
    
    # Verify that the response includes a 'summary' dictionary with a 'policy_violation' key.
    summary = response.summary.to_dict()
    assert isinstance(summary, dict), "Expected summary to be a dictionary"
    assert "policy_violation" in summary, "Policy violation not detected in summary"
    
    # Assert that the violation score is greater than zero.
    violation_score = summary.get("policy_violation", 0)
    assert violation_score > 0, "Policy violation score should be greater than 0"
