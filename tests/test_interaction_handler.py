from unittest.mock import mock_open, patch, Mock

import pytest

from s3_upload import interaction_handler

@pytest.fixture
def handler():
    handler = interaction_handler.InteractionHandler()
    return handler

def test_when_valid_manifest_path_then_create_interaction_data(handler):
    manifest_file = {
        'files': []
    }
    metadata_file = {
        "startTime": 1707869004,
        "endTime": 1707869013,
        "interactionId": "123123",
        "deviceId": "abcd123"
    }

    def get_json_data_side_effect(path):
        if path == "mock_manifest_path":
            return manifest_file
        if path == "local_folder_path/metadata.json":
            return metadata_file

    handler.get_json_data = Mock(side_effect=get_json_data_side_effect)

    expected_result = {
        "files": [],
        "startTime": 1707869004,
        "endTime": 1707869013,
        "interactionId": "123123",
        "deviceId": "abcd123",
        "local_folder_path": "local_folder_path",
        "manifest_file": "mock_manifest_path",
        "metadata_file": "local_folder_path/metadata.json",
    }

    with patch('os.path.dirname', return_value='local_folder_path'):
        result = handler.create_interaction_data("mock_manifest_path")

    assert result == expected_result

def test_when_invalid_manifest_path_then_return_none(handler):
    handler.get_json_data = Mock(return_value=None)

    result = handler.create_interaction_data("mock_manifest_path")

    assert result == None

def test_when_invalid_metadata_path_then_return_none(handler):
    handler.get_json_data = Mock(side_effect=[{"files": []}, None])

    result = handler.create_interaction_data("mock_manifest_path")

    assert result == None


def test_can_get_json_data(handler):
    mock_file_content = '{"key": "value"}'
    mock_file = mock_open(read_data=mock_file_content)

    with patch("builtins.open", mock_file):
        result = handler.get_json_data("mock_path")

    expected_result = {"key": "value"}

    assert result == expected_result