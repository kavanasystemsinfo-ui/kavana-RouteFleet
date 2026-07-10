import math
from main import haversine

def test_haversine_known_distance():
    # Test distance between two known points (approximate)
    # New York City to Los Angeles
    nyc_lat, nyc_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    # Known distance is approximately 3940 km
    distance = haversine(nyc_lat, nyc_lon, la_lat, la_lon)
    # Allow 1% tolerance for floating point and earth model differences
    assert abs(distance - 3940) < 40  # within 40km

def test_haversine_same_point():
    # Distance from a point to itself should be zero
    lat, lon = 40.7128, -74.0060
    distance = haversine(lat, lon, lat, lon)
    assert distance == 0.0

def test_haversine_zero_distance():
    # Test with very close points
    lat1, lon1 = 40.7128, -74.0060
    lat2, lon2 = 40.7129, -74.0061  # ~111m apart
    distance = haversine(lat1, lon1, lat2, lon2)
    assert distance < 0.2  # should be less than 200m