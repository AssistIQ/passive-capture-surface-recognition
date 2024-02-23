import threading
import time
import os

from watchdog.observers import Observer

from file_watcher import FileWatcher
from pending_interaction_uploader import PendingInteractionUploader
from s3_uploader import S3Uploader

def get_upload_queue_folder_path():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    parent_directory = os.path.dirname(current_directory)

    folder_name = 'upload_queue/'
    folder_path = parent_directory + '/' + folder_name

    return folder_path

if __name__ == "__main__":
    aws_access_key = ''
    aws_secret_key = ''
    aws_bucket_name = 'andrew-testing-assistiq'

    upload_folder = get_upload_queue_folder_path()

    s3_uploader = S3Uploader(aws_access_key, aws_secret_key, aws_bucket_name, upload_folder)
    file_watcher = FileWatcher(upload_folder, s3_uploader)
    pending_interaction_uploader = PendingInteractionUploader(s3_uploader, upload_folder)

    pending_interaction_thread = threading.Thread(target=pending_interaction_uploader.upload_pending_interactions)
    pending_interaction_thread.start()

    file_watcher.start()

    try:
        print("Monitoring folder for interaction logs, images and videos")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping S3 Uploader...")
        pending_interaction_thread.join()
        file_watcher.stop()
    
