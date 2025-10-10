import os
import pytest
from dotenv import load_dotenv
from enkryptai_sdk import ModelClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
ENKRYPT_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPT_BASE_URL = os.getenv("ENKRYPTAI_BASE_URL") or "https://api.enkryptai.com"

model_saved_name = None
test_model_saved_name = "Test Model"
model_version = None
test_model_version = "v1"
model_provider = "openai"
model_name = "gpt-4o-mini"
model_endpoint_url = "https://api.openai.com/v1/chat/completions"

@pytest.fixture
def model_client():
    # You'll want to use a test API key here
    return ModelClient(api_key=ENKRYPT_API_KEY, base_url=ENKRYPT_BASE_URL)


@pytest.fixture
def sample_model_config():
    return {
        "model_saved_name": test_model_saved_name,
        "model_version": test_model_version,
        "testing_for": "foundationModels",
        "model_name": model_name,
        "model_config": {
            "model_provider": model_provider,
            # "model_provider": "custom",
            "endpoint_url": model_endpoint_url,
            "apikey": OPENAI_API_KEY,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
            # "custom_headers": [
            #     {
            #         "key": "Content-Type",
            #         "value": "application/json"
            #     },
            #     {
            #         "key": "Authorization",
            #         "value": "Bearer " + OPENAI_API_KEY
            #     }
            # ],
            # "custom_payload": {
            #     "model": model_name,
            #     "messages": [
            #         {
            #             "role": "user",
            #             "content": "{prompt}"
            #         }
            #     ]
            # },
            # "custom_response_content_type": "json",
            # "custom_response_format": ".choices[0].message.content",
        },
    }


def test_add_model(model_client, sample_model_config):
    print("\n\nTesting adding a new model")
    # Test creating a new model
    response = model_client.add_model(config=sample_model_config)
    print("\nResponse from adding a new model: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Model details added successfully"
    # assert hasattr(response, "data")
    model_info = response.data
    assert model_info is not None
    assert model_info["model_saved_name"] == test_model_saved_name
    assert model_info["model_version"] == test_model_version


def test_list_models(model_client):
    print("\n\nTesting list_models")
    # Test the list_models method
    models = model_client.get_model_list()
    print("\nModels list: ", models)
    assert models is not None
    # assert isinstance(models, ModelCollection)
    assert len(models.to_dict()) > 0
    # global model_saved_name
    # model_info = models.models[0]
    # assert model_info is not None
    # model_saved_name = model_info.model_saved_name
    # assert model_saved_name is not None
    # print("\nPicked model in list_models: ", model_saved_name)
    # assert model_info.model_version is not None


def test_get_model(model_client):
    print("\n\nTesting get_model")
    # global model_saved_name
    # if model_saved_name is None:
    #     print("\nModel saved name is None, fetching it from list_models")
    #     response = model_client.get_model_list()
    #     model_info = response.models[0]
    #     assert model_info is not None
    #     model_saved_name = model_info.model_saved_name
    #     assert model_saved_name is not None
    #     print("\nPicked model in get_model: ", model_saved_name)
    model_saved_name = test_model_saved_name
    model_version = test_model_version

    # Now test the get_model method
    model = model_client.get_model(model_saved_name=model_saved_name, model_version=model_version)
    assert model is not None
    # assert hasattr(model, "model_id")
    assert model.model_saved_name == model_saved_name
    assert model.model_version == model_version
    # assert hasattr(model, "status")


def test_modify_model(model_client, sample_model_config):
    print("\n\nTesting modifying a new model")
    # Test creating a new model
    response = model_client.modify_model(config=sample_model_config, old_model_saved_name=None, old_model_version=None)
    print("\nResponse from modifying a new model: ", response)
    print("\nResponse data type: ", type(response))
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Model details updated successfully"
    # assert hasattr(response, "data")
    model_info = response.data
    assert model_info is not None
    assert model_info["model_saved_name"] == test_model_saved_name
    assert model_info["model_version"] == test_model_version


def test_delete_model(model_client):
    print("\n\nTesting delete_model")
    response = model_client.delete_model(model_saved_name=test_model_saved_name, model_version=test_model_version)
    print("\nResponse from delete_model: ", response)
    assert response is not None
    # assert hasattr(response, "message")
    assert response.message == "Model details deleted successfully"
