"""
Tests for BoxAI provider functionality in Enkrypt AI SDK.
"""

import pytest
from enkryptai_sdk.dto.models import (
    ModelProviders,
    BoxAIAuthData,
    ModelDetailConfig,
    DetailModelConfig,
    PathsConfig,
    EndpointConfig
)


class TestBoxAIProvider:
    """Test BoxAI provider functionality."""
    
    def test_boxai_provider_enum(self):
        """Test that BOXAI is included in ModelProviders enum."""
        assert "boxai" in [p.value for p in ModelProviders]
        assert ModelProviders.BOXAI == "boxai"
    
    def test_boxai_auth_data_creation(self):
        """Test creating BoxAIAuthData with all fields."""
        auth_data = BoxAIAuthData(
            boxai_client_id="test_client_id",
            boxai_client_secret="test_client_secret",
            boxai_user_id="test_user_id",
            boxai_default_file_id="test_file_id"
        )
        
        assert auth_data.boxai_client_id == "test_client_id"
        assert auth_data.boxai_client_secret == "test_client_secret"
        assert auth_data.boxai_user_id == "test_user_id"
        assert auth_data.boxai_default_file_id == "test_file_id"
        
        # Check that fields are stored in extra_fields for backward compatibility
        assert auth_data._extra_fields["boxai_client_id"] == "test_client_id"
        assert auth_data._extra_fields["boxai_client_secret"] == "test_client_secret"
        assert auth_data._extra_fields["boxai_user_id"] == "test_user_id"
        assert auth_data._extra_fields["boxai_default_file_id"] == "test_file_id"
    
    def test_boxai_auth_data_partial_creation(self):
        """Test creating BoxAIAuthData with partial fields."""
        auth_data = BoxAIAuthData(
            boxai_client_id="test_client_id"
            # Missing other fields
        )
        
        assert auth_data.boxai_client_id == "test_client_id"
        assert auth_data.boxai_client_secret is None
        assert auth_data.boxai_user_id is None
        assert auth_data.boxai_default_file_id is None
        
        # Check that only set fields are in extra_fields
        assert "boxai_client_id" in auth_data._extra_fields
        assert "boxai_client_secret" not in auth_data._extra_fields
    
    def test_boxai_auth_data_to_dict(self):
        """Test converting BoxAIAuthData to dictionary."""
        auth_data = BoxAIAuthData(
            boxai_client_id="test_client_id",
            boxai_client_secret="test_client_secret",
            boxai_user_id="test_user_id",
            boxai_default_file_id="test_file_id"
        )
        
        auth_dict = auth_data.to_dict()
        
        assert "boxai_client_id" in auth_dict
        assert "boxai_client_secret" in auth_dict
        assert "boxai_user_id" in auth_dict
        assert "boxai_default_file_id" in auth_dict
        assert auth_dict["boxai_client_id"] == "test_client_id"
    
    def test_boxai_auth_data_from_dict(self):
        """Test creating BoxAIAuthData from dictionary."""
        auth_dict = {
            "boxai_client_id": "test_client_id",
            "boxai_client_secret": "test_client_secret",
            "boxai_user_id": "test_user_id",
            "boxai_default_file_id": "test_file_id"
        }
        
        auth_data = BoxAIAuthData.from_dict(auth_dict)
        
        assert auth_data.boxai_client_id == "test_client_id"
        assert auth_data.boxai_client_secret == "test_client_secret"
        assert auth_data.boxai_user_id == "test_user_id"
        assert auth_data.boxai_default_file_id == "test_file_id"
    
    def test_boxai_auth_data_from_dict_with_extra_fields(self):
        """Test creating BoxAIAuthData from dictionary with extra_fields."""
        auth_dict = {
            "_extra_fields": {
                "boxai_client_id": "test_client_id",
                "boxai_client_secret": "test_client_secret",
                "boxai_user_id": "test_user_id",
                "boxai_default_file_id": "test_file_id"
            }
        }
        
        auth_data = BoxAIAuthData.from_dict(auth_dict)
        
        assert auth_data.boxai_client_id == "test_client_id"
        assert auth_data.boxai_client_secret == "test_client_secret"
        assert auth_data.boxai_user_id == "test_user_id"
        assert auth_data.boxai_default_file_id == "test_file_id"
    
    def test_boxai_auth_data_from_dict_mixed(self):
        """Test creating BoxAIAuthData from dictionary with mixed field sources."""
        auth_dict = {
            "boxai_client_id": "direct_client_id",
            "_extra_fields": {
                "boxai_client_secret": "extra_client_secret",
                "boxai_user_id": "extra_user_id",
                "boxai_default_file_id": "extra_file_id"
            }
        }
        
        auth_data = BoxAIAuthData.from_dict(auth_dict)
        
        # Direct fields should take precedence
        assert auth_data.boxai_client_id == "direct_client_id"
        assert auth_data.boxai_client_secret == "extra_client_secret"
        assert auth_data.boxai_user_id == "extra_user_id"
        assert auth_data.boxai_default_file_id == "extra_file_id"


class TestBoxAIModelConfiguration:
    """Test BoxAI model configuration functionality."""
    
    def test_boxai_model_detail_config(self):
        """Test creating ModelDetailConfig with BoxAI provider."""
        auth_data = BoxAIAuthData(
            boxai_client_id="test_client_id",
            boxai_client_secret="test_client_secret",
            boxai_user_id="test_user_id",
            boxai_default_file_id="test_file_id"
        )
        
        model_detail_config = ModelDetailConfig(
            model_source="https://boxai.com",
            model_provider=ModelProviders.BOXAI,
            system_prompt="You are a helpful BoxAI assistant.",
            endpoint_url="https://api.boxai.com/v1/chat/completions",
            auth_data=auth_data
        )
        
        assert model_detail_config.model_provider == ModelProviders.BOXAI
        assert model_detail_config.model_source == "https://boxai.com"
        assert model_detail_config.auth_data.boxai_client_id == "test_client_id"
        assert isinstance(model_detail_config.auth_data, BoxAIAuthData)
    
    def test_boxai_complete_model_config(self):
        """Test creating complete model configuration with BoxAI."""
        auth_data = BoxAIAuthData(
            boxai_client_id="test_client_id",
            boxai_client_secret="test_client_secret",
            boxai_user_id="test_user_id",
            boxai_default_file_id="test_file_id"
        )
        
        model_detail_config = ModelDetailConfig(
            model_source="https://boxai.com",
            model_provider=ModelProviders.BOXAI,
            system_prompt="You are a helpful BoxAI assistant.",
            endpoint_url="https://api.boxai.com/v1/chat/completions",
            auth_data=auth_data
        )
        
        model_config = DetailModelConfig(
            model_saved_name="BoxAI Test Model",
            model_version="v1",
            testing_for="foundationModels",
            model_name="boxai-test-model",
            model_config=model_detail_config
        )
        
        assert model_config.model_saved_name == "BoxAI Test Model"
        assert model_config.model_config.model_provider == ModelProviders.BOXAI
        assert model_config.model_config.auth_data.boxai_client_id == "test_client_id"
    
    def test_boxai_model_config_from_dict(self):
        """Test creating BoxAI model configuration from dictionary."""
        config_dict = {
            "model_saved_name": "BoxAI Dict Model",
            "model_version": "v1",
            "testing_for": "foundationModels",
            "model_name": "boxai-dict-model",
            "model_config": {
                "model_source": "https://boxai.com",
                "model_provider": "boxai",
                "system_prompt": "You are a helpful BoxAI assistant.",
                "endpoint_url": "https://api.boxai.com/v1/chat/completions",
                "auth_data": {
                    "boxai_client_id": "dict_client_id",
                    "boxai_client_secret": "dict_client_secret",
                    "boxai_user_id": "dict_user_id",
                    "boxai_default_file_id": "dict_file_id"
                }
            }
        }
        
        model_config = DetailModelConfig.from_dict(config_dict)
        
        assert model_config.model_saved_name == "BoxAI Dict Model"
        assert model_config.model_config.model_provider == ModelProviders.BOXAI
        assert model_config.model_config.auth_data.boxai_client_id == "dict_client_id"
        assert isinstance(model_config.model_config.auth_data, BoxAIAuthData)


class TestBoxAIEndpointConfiguration:
    """Test BoxAI endpoint configuration functionality."""
    
    def test_boxai_endpoint_config(self):
        """Test creating endpoint configuration for BoxAI."""
        endpoint_config = EndpointConfig(
            scheme="https",
            host="api.boxai.com",
            port=443,
            base_path="v1"
        )
        
        assert endpoint_config.scheme == "https"
        assert endpoint_config.host == "api.boxai.com"
        assert endpoint_config.port == 443
        assert endpoint_config.base_path == "v1"
    
    def test_boxai_paths_config(self):
        """Test creating paths configuration for BoxAI."""
        paths_config = PathsConfig(
            completions="/chat/completions",
            chat="chat/completions",
            vision="images",
            embeddings="embeddings"
        )
        
        assert paths_config.completions == "/chat/completions"
        assert paths_config.chat == "chat/completions"
        assert paths_config.vision == "images"
        assert paths_config.embeddings == "embeddings"


class TestBoxAIEdgeCases:
    """Test BoxAI edge cases and error conditions."""
    
    def test_boxai_auth_data_empty_fields(self):
        """Test BoxAIAuthData with empty string fields."""
        auth_data = BoxAIAuthData(
            boxai_client_id="",
            boxai_client_secret="",
            boxai_user_id="",
            boxai_default_file_id=""
        )
        
        assert auth_data.boxai_client_id == ""
        assert auth_data.boxai_client_secret == ""
        assert auth_data.boxai_user_id == ""
        assert auth_data.boxai_default_file_id == ""
        
        # Empty strings should still be stored in extra_fields
        assert auth_data._extra_fields["boxai_client_id"] == ""
    
    def test_boxai_auth_data_none_fields(self):
        """Test BoxAIAuthData with None fields."""
        auth_data = BoxAIAuthData()
        
        assert auth_data.boxai_client_id is None
        assert auth_data.boxai_client_secret is None
        assert auth_data.boxai_user_id is None
        assert auth_data.boxai_default_file_id is None
        
        # None fields should not be stored in extra_fields
        assert "boxai_client_id" not in auth_data._extra_fields
    
    def test_boxai_auth_data_inheritance(self):
        """Test that BoxAIAuthData properly inherits from AuthData."""
        auth_data = BoxAIAuthData(
            header_name="Custom-Auth",
            header_prefix="BoxAI",
            space_after_prefix=False,
            boxai_client_id="test_client_id"
        )
        
        # Check inherited fields
        assert auth_data.header_name == "Custom-Auth"
        assert auth_data.header_prefix == "BoxAI"
        assert auth_data.space_after_prefix is False
        
        # Check BoxAI-specific fields
        assert auth_data.boxai_client_id == "test_client_id"
        
        # Check that it's an instance of both classes
        assert isinstance(auth_data, BoxAIAuthData)
        from enkryptai_sdk.dto.models import AuthData
        assert isinstance(auth_data, AuthData)


if __name__ == "__main__":
    pytest.main([__file__])
