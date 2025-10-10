import os
import pytest
from openai import OpenAI
from dotenv import load_dotenv
from enkryptai_sdk import ModelClient

load_dotenv()

ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

client = OpenAI(
    base_url=f"{ENKRYPT_BASE_URL}/ai-proxy"
)

test_deployment_name = "test-deployment"

# Custom headers
custom_headers = {
    'apikey': ENKRYPT_API_KEY,
    'X-Enkrypt-Deployment': test_deployment_name
}

# Example of making a request with custom headers
response = client.chat.completions.create(
    model='gpt-4o',
    messages=[{'role': 'user', 'content': 'Hello!'}],
    extra_headers=custom_headers
)

print("\n\nResponse from OpenAI API with custom headers: ", response)
print("\nResponse data type: ", type(response))

def test_openai_response():
    assert response is not None
    assert hasattr(response, "choices")
    assert len(response.choices) > 0
    print("\n\nOpenAI API response is: ", response.choices[0].message.content)
    assert hasattr(response, "enkrypt_policy_detections")
