import pytest
from unittest.mock import patch, Mock
from s3_upload import s3_uploader

@pytest.fixture
def uploader():
    uploader = s3_uploader.S3Uploader('access_key', 'secret_key', 'bucket_name', 'folder_path')
    return uploader

def test_can_upload_interaction(uploader):
    uploader.upload_file_task = Mock()
    uploader.cleanup_local_folder = Mock()

    with patch('os.path.exists', return_value=True):
        interaction_data = {
            "files": ["file1", "file2"],
            "metadata_file": "metadata.json",
            "manifest_file": "manifest.json",
            "local_folder_path": "local_folder_path",
            "interactionId": "123123",
            "deviceId": "abcd123"
        }

        uploader.upload_interaction_task(interaction_data)

    assert uploader.upload_file_task.call_count == 4
    assert uploader.cleanup_local_folder.call_count == 1

def test_given_not_all_files_uploaded_then_dont_upload_manifest_file(uploader):
    uploader.upload_file_task = Mock(side_effect=[True, False, True])
    uploader.cleanup_local_folder = Mock()

    with patch('os.path.exists', return_value=True):
        interaction_data = {
            "files": ["file1", "file2"],
            "metadata_file": "metadata.json",
            "manifest_file": "manifest.json",
            "local_folder_path": "local_folder_path",
            "interactionId": "123123",
            "deviceId": "abcd123"
        }

        uploader.upload_interaction_task(interaction_data)

    assert uploader.upload_file_task.call_count == 3
    assert uploader.cleanup_local_folder.call_count == 0

def test_when_upload_file_task_fails_then_retries(uploader):
    uploader.upload_file = Mock(side_effect=[False, True])
    uploader.cleanup_local_file = Mock()

    # Mock time.sleep so we dont have to wait
    with patch('time.sleep'):
        uploader.upload_file_task('local_path', 's3_key')

    assert uploader.upload_file.call_count == 2
    assert uploader.cleanup_local_file.call_count == 1

def test_given_max_retry_attempts_then_stop_retrying(uploader):
    uploader.upload_file = Mock(return_value=False)
    uploader.cleanup_local_file = Mock()

    # Mock time.sleep so we dont have to wait
    with patch('time.sleep'):
        uploader.upload_file_task('local_path', 's3_key')

    assert uploader.upload_file.call_count == uploader.MAX_UPLOAD_RETRIES
    assert uploader.cleanup_local_file.call_count == 0