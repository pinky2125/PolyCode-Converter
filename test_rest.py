import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.skipif(os.getenv("GEMINI_API_KEY") is None, reason="Gemini API key not configured")
def test_list_gemini_models():
    api_key = os.getenv("GEMINI_API_KEY")
    response = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json().get("models", []), list)
