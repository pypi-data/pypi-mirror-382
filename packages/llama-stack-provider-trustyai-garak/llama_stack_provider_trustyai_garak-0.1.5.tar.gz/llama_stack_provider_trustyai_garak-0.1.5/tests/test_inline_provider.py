"""Tests for inline provider implementation"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from llama_stack_provider_trustyai_garak.inline import get_provider_impl
from llama_stack_provider_trustyai_garak.inline.garak_eval import GarakEvalAdapter
from llama_stack_provider_trustyai_garak.inline.provider import get_provider_spec
from llama_stack_provider_trustyai_garak.config import GarakEvalProviderConfig

from llama_stack.apis.datatypes import Api


class TestInlineProvider:
    """Test cases for inline provider"""

    def test_get_provider_spec(self):
        """Test provider specification"""
        spec = get_provider_spec()
        
        assert spec.api == Api.eval
        assert spec.provider_type == "inline::trustyai_garak"
        assert "garak==0.12.0" in spec.pip_packages
        assert spec.config_class == "llama_stack_provider_trustyai_garak.config.GarakEvalProviderConfig"
        assert spec.module == "llama_stack_provider_trustyai_garak.inline"
        assert Api.inference in spec.api_dependencies
        assert Api.files in spec.api_dependencies
        assert Api.benchmarks in spec.api_dependencies
        assert Api.safety in spec.optional_api_dependencies
        assert Api.shields in spec.optional_api_dependencies

    @pytest.mark.asyncio
    async def test_get_provider_impl_success(self):
        """Test successful provider implementation creation"""
        config = GarakEvalProviderConfig()
        mock_deps = {
            Api.files: Mock(),
            Api.benchmarks: Mock()
        }
        
        with patch.object(GarakEvalAdapter, 'initialize', new_callable=AsyncMock):
            with patch.object(GarakEvalAdapter, '_ensure_garak_installed'):
                with patch.object(GarakEvalAdapter, '_get_all_probes', return_value=set()):
                    impl = await get_provider_impl(config, mock_deps)
                    
                    assert isinstance(impl, GarakEvalAdapter)
                    assert impl._config == config
                    impl.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_provider_impl_with_base_url(self):
        """Test provider implementation with base_url from config"""
        config = GarakEvalProviderConfig(base_url="https://custom.api.com")
        
        # Provide required mock dependencies
        mock_deps = {
            Api.files: Mock(),
            Api.benchmarks: Mock()
        }
        
        with patch.object(GarakEvalAdapter, 'initialize', new_callable=AsyncMock):
            with patch.object(GarakEvalAdapter, '_ensure_garak_installed'):
                with patch.object(GarakEvalAdapter, '_get_all_probes', return_value=set()):
                    impl = await get_provider_impl(config, mock_deps)
                    
                    assert impl._config.base_url == "https://custom.api.com"

    @pytest.mark.asyncio
    async def test_get_provider_impl_error_handling(self):
        """Test error handling in provider implementation creation"""
        config = GarakEvalProviderConfig()
        
        # Provide required mock dependencies
        mock_deps = {
            Api.files: Mock(),
            Api.benchmarks: Mock()
        }
        
        with patch.object(GarakEvalAdapter, 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = Exception("Initialization failed")
            
            with pytest.raises(Exception) as exc_info:
                await get_provider_impl(config, mock_deps)
            
            assert "Failed to create inline Garak implementation" in str(exc_info.value)

    @pytest.mark.asyncio 
    async def test_get_provider_impl_no_deps(self):
        """Test provider implementation with None dependencies (converted to empty dict internally)"""
        config = GarakEvalProviderConfig()
        
        with patch.object(GarakEvalAdapter, 'initialize', new_callable=AsyncMock):
            with patch.object(GarakEvalAdapter, '_ensure_garak_installed'):
                with patch.object(GarakEvalAdapter, '_get_all_probes', return_value=set()):
                    # Pass None but the implementation should convert it to {}
                    # We'll need to mock the constructor to handle this
                    impl = await get_provider_impl(config, None)
                    
                    assert isinstance(impl, GarakEvalAdapter)

    @pytest.mark.asyncio
    async def test_get_provider_impl_with_optional_deps(self):
        """Test provider implementation with optional safety and shields dependencies"""
        config = GarakEvalProviderConfig()
        
        # Provide all dependencies including optional ones
        mock_deps = {
            Api.files: Mock(),
            Api.benchmarks: Mock(),
            Api.safety: Mock(),
            Api.shields: Mock()
        }
        
        with patch.object(GarakEvalAdapter, 'initialize', new_callable=AsyncMock):
            with patch.object(GarakEvalAdapter, '_ensure_garak_installed'):
                with patch.object(GarakEvalAdapter, '_get_all_probes', return_value=set()):
                    impl = await get_provider_impl(config, mock_deps)
                    
                    assert isinstance(impl, GarakEvalAdapter)
                    assert impl._config == config
                    assert impl.safety_api is not None
                    assert impl.shields_api is not None
                    impl.initialize.assert_called_once()