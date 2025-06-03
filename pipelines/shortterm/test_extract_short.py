import pytest

from extract_short import fetch_all_plants, fetch_plant_info, APIError, URL_BASE


def test_fetch_plant_info_ok(requests_mock):
    plant_id = 1
    mock_url = f"{URL_BASE}{plant_id}"

    mock_data = {"plant_id": 1, "name": "Test Plant 1"}

    requests_mock.get(mock_url, json=mock_data, status_code=200)

    result = fetch_plant_info(plant_id)
    assert result["name"] == "Test Plant 1"
    assert isinstance(result, dict)


def test_fetch_plant_info_500(requests_mock):

    plant_id = 0

    mock_url = f"{URL_BASE}{plant_id}"
    requests_mock.get(mock_url, status_code=500)

    with pytest.raises(APIError, match="Server error occurred."):
        fetch_plant_info(plant_id)


def test_fetch_plant_info_404(requests_mock):
    plant_id = 53

    mock_url = f"{URL_BASE}{plant_id}"
    requests_mock.get(mock_url, status_code=404)

    with pytest.raises(APIError, match="Plant not found."):
        fetch_plant_info(plant_id)


def test_fetch_plant_info_403(requests_mock):
    plant_id = 2

    mock_url = f"{URL_BASE}{plant_id}"
    requests_mock.get(mock_url, status_code=403)

    with pytest.raises(APIError, match="Access to resource is forbidden."):
        fetch_plant_info(plant_id)


def test_fetch_plant_info_400(requests_mock):
    plant_id = "50x"

    mock_url = f"{URL_BASE}{plant_id}"
    requests_mock.get(mock_url, status_code=400)

    with pytest.raises(APIError, match="Bad Request."):
        fetch_plant_info(plant_id)


def test_fetch_all_plants_correct_length(requests_mock):

    for p_id in range(1, 6):
        mock_url = f"{URL_BASE}{p_id}"
        mock_data = {"plant_id": p_id, "name": f"Test Plant {p_id}"}
        requests_mock.get(mock_url, json=mock_data, status_code=200)

    results = fetch_all_plants(1, 6)
    assert len(results) == 5
    assert isinstance(results, list)
