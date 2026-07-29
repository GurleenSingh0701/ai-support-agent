import sys
import os
import pytest

# Ensure backend directory is in sys.path for module resolution
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

@pytest.fixture
def mock_gemini_response():
    """Returns a mock class simulating Google Gemini API response."""
    class MockResponse:
        def __init__(self, text):
            self.text = text
    return MockResponse

@pytest.fixture
def sample_user_message():
    return "I want to return item #12345 because it arrived damaged and broken!"
