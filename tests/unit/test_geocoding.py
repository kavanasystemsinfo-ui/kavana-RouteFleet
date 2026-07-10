import pytest
from unittest.mock import AsyncMock, MagicMock
from main import geocode_address

@pytest.mark.asyncio
async def test_geocode_address_success():
    """Test successful geocoding"""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"lat": "40.7128", "lon": "-74.0060"}]
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    result = await geocode_address("New York, NY", mock_client)
    
    assert result == (40.7128, -74.0060)
    mock_client.get.assert_called_once_with(
        "https://nominatim.openstreetmap.org/search",
        params={"q": "New York, NY", "format": "json", "limit": 1},
        headers={"User-Agent": "KavanaLogistic/1.0 (+https://kavana.dev)"},
        timeout=10.0
    )

@pytest.mark.asyncio
async def test_geocode_address_not_found():
    """Test when address is not found"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    result = await geocode_address("Invalid Address 12345", mock_client)
    
    assert result is None

@pytest.mark.asyncio
async def test_geocode_address_http_error():
    """Test when HTTP request fails"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    result = await geocode_address("Any Address", mock_client)
    
    assert result is None

@pytest.mark.asyncio
async def test_geocode_address_exception():
    """Test when an exception occurs"""
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Network error")
    
    result = await geocode_address("Any Address", mock_client)
    
    assert result is None

@pytest.mark.asyncio
async def test_geocode_address_invalid_json():
    """Test when response is not valid JSON"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    result = await geocode_address("Any Address", mock_client)
    
    assert result is None