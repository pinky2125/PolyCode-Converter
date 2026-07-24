import io

from app import app


def test_api_convert_endpoint_returns_json():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.post(
            "/api/convert",
            json={
                "source_code": "print('hello')",
                "source_lang": "python",
                "target_lang": "python",
            },
        )
    assert response.status_code == 200
    data = response.get_json()
    assert "output_code" in data
    assert isinstance(data["output_code"], str)


def test_upload_endpoint_reads_uploaded_file():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.post(
            "/upload",
            data={
                "file": (io.BytesIO(b"print('uploaded')"), "sample.py"),
            },
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    assert b"uploaded" in response.data.lower()
