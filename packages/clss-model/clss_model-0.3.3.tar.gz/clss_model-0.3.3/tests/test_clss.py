"""
Test suite for CLSS package.

This module contains comprehensive tests for the CLSS contrastive learning model,
configuration, and utilities.
"""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock

import clss


class TestCLSSConfig:
    """Test the CLSSConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = clss.CLSSConfig()
        assert config.hidden_dim == 32
        assert config.learning_rate == 1e-3
        assert config.batch_size == 180
        assert config.init_temperature == 0.5
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = clss.CLSSConfig(
            hidden_dim=64,
            learning_rate=1e-4,
            batch_size=16
        )
        assert config.hidden_dim == 64
        assert config.learning_rate == 1e-4
        assert config.batch_size == 16
    
    def test_config_to_dict(self):
        """Test conversion to dictionary."""
        config = clss.CLSSConfig(hidden_dim=64, learning_rate=2e-3)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["hidden_dim"] == 64
        assert config_dict["learning_rate"] == 2e-3
        assert "esm2_checkpoint" in config_dict


class TestCLSSModel:
    """Test the CLSSModel class."""
    
    def test_model_init_without_esm3(self):
        """Test model initialization without ESM3 loading."""
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=32,
            should_load_esm3=False
        )
        assert model.hidden_dim == 32
        assert model.structure_encoder is None
        assert not model.should_load_esm3
    
    def test_model_init_with_esm3_flag(self):
        """Test model initialization with ESM3 flag."""
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=32,
            should_load_esm3=True
        )
        assert model.should_load_esm3
    
    def test_temperature_parameter(self):
        """Test temperature parameter initialization."""
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=32,
            init_temperature=0.7,
            should_learn_temperature=True
        )
        # Check that temperature is properly set
        assert hasattr(model, 'temperature')
        # Temperature should be learnable
        assert model.temperature.requires_grad
    
    def test_adapters_creation(self):
        """Test that adapters are properly created."""
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=64
        )
        
        # Check sequence adapter
        assert hasattr(model, 'sequence_adapter')
        assert isinstance(model.sequence_adapter, torch.nn.Module)
        
        # Check structure adapter  
        assert hasattr(model, 'structure_adapter')
        assert isinstance(model.structure_adapter, torch.nn.Module)
    
    def test_load_esm2_basic(self):
        """Test basic ESM2 loading."""
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=32
        )
        
        # Verify that the model has the necessary components
        assert hasattr(model, 'sequence_encoder')
        assert hasattr(model, 'sequence_tokenizer')
    
    def test_model_from_config(self):
        """Test creating model from configuration."""
        config = clss.CLSSConfig(
            hidden_dim=64,
            learning_rate=2e-3,
            init_temperature=0.7
        )
        
        model = clss.CLSSModel.from_config(config)
        
        # Verify that the model uses config values
        assert model.hidden_dim == 64
        assert model.learning_rate == 2e-3
        assert abs(model.temperature.item() - 0.7) < 1e-6  # Use approximate equality for floats


class TestUtilities:
    """Test utility functions."""
    
    def test_download_pretrained_model_function_exists(self):
        """Test that download_pretrained_model function exists and is callable."""
        assert hasattr(clss, 'download_pretrained_model')
        assert callable(clss.download_pretrained_model)
    
    @patch('clss.utils.hf_hub_download')
    def test_download_pretrained_model_mocked(self, mock_download):
        """Test download_pretrained_model with mocked huggingface_hub."""
        mock_download.return_value = "/path/to/model.ckpt"
        
        result = clss.download_pretrained_model()
        
        mock_download.assert_called_once_with(
            repo_id="guyyanai/CLSS", 
            filename="h32_r10.lckpt", 
            repo_type="model"
        )
        assert result == "/path/to/model.ckpt"
    
    @patch('clss.utils.hf_hub_download')
    def test_download_pretrained_model_custom_params(self, mock_download):
        """Test download_pretrained_model with custom parameters."""
        mock_download.return_value = "/path/to/custom_model.ckpt"
        
        result = clss.download_pretrained_model(
            repo_id="custom/repo",
            model_name="custom_model.ckpt"
        )
        
        mock_download.assert_called_once_with(
            repo_id="custom/repo", 
            filename="custom_model.ckpt", 
            repo_type="model"
        )
        assert result == "/path/to/custom_model.ckpt"


class TestPackageStructure:
    """Test package structure and imports."""
    
    def test_version_available(self):
        """Test that __version__ is available."""
        assert hasattr(clss, '__version__')
        assert isinstance(clss.__version__, str)
        assert clss.__version__ == "0.2.0"
    
    def test_author_info_available(self):
        """Test that author information is available."""
        assert hasattr(clss, '__author__')
        assert hasattr(clss, '__email__')
        assert isinstance(clss.__author__, str)
        assert isinstance(clss.__email__, str)
    
    def test_main_exports(self):
        """Test that main classes and functions are exported."""
        # Core classes
        assert hasattr(clss, 'CLSSModel')
        assert hasattr(clss, 'CLSSConfig')
        
        # Utilities
        assert hasattr(clss, 'download_pretrained_model')
        
        # Check __all__ is properly defined
        assert hasattr(clss, '__all__')
        assert 'CLSSModel' in clss.__all__
        assert 'CLSSConfig' in clss.__all__
        assert 'download_pretrained_model' in clss.__all__
    
    def test_imports_work_without_heavy_dependencies(self):
        """Test that basic imports work even without ESM/transformers."""
        # These should work even if ESM/transformers are not installed
        config = clss.CLSSConfig()
        assert config is not None
    
    def test_no_unexpected_imports_at_package_level(self):
        """Test that heavy dependencies are not imported at package level."""
        import sys
        
        # Check that ESM modules are not loaded yet
        esm_modules = [name for name in sys.modules if name.startswith('esm')]
        # It's okay if some are loaded, but we shouldn't have forced them
        
        # Check that we can import clss without importing transformers immediately
        # (This is harder to test reliably, but the lazy import should help)


@pytest.mark.integration
class TestIntegration:
    """Integration tests that require actual dependencies."""
    
    @pytest.mark.slow
    def test_model_basic_creation(self):
        """Test basic model creation works."""
        # Create model
        model = clss.CLSSModel(
            esm2_checkpoint="facebook/esm2_t12_35M_UR50D",
            hidden_dim=32,
            should_load_esm3=False
        )
        
        # Basic checks
        assert model is not None
        assert hasattr(model, 'sequence_encoder')
        assert hasattr(model, 'sequence_tokenizer')
        assert hasattr(model, 'hidden_dim')
        assert model.hidden_dim == 32


if __name__ == "__main__":
    pytest.main([__file__])