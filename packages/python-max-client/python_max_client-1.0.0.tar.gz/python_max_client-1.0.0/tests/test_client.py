"""
Tests for MaxClient
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from python_max_client.client import MaxClient


class TestMaxClient:
    """Test cases for MaxClient"""
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = MaxClient()
        assert client is not None
        assert hasattr(client, 'connect')
        assert hasattr(client, 'login_by_token')
        assert hasattr(client, 'send_code')
        assert hasattr(client, 'sign_in')
    
    @pytest.mark.asyncio
    async def test_connect_method_exists(self):
        """Test that connect method exists and is callable"""
        client = MaxClient()
        assert callable(client.connect)
    
    @pytest.mark.asyncio
    async def test_login_methods_exist(self):
        """Test that login methods exist and are callable"""
        client = MaxClient()
        assert callable(client.login_by_token)
        assert callable(client.send_code)
        assert callable(client.sign_in)
    
    def test_callback_setting(self):
        """Test callback setting functionality"""
        client = MaxClient()
        
        def test_callback(client, packet):
            pass
        
        # This should not raise an exception
        client.set_callback(test_callback)
        assert hasattr(client, 'set_callback')
