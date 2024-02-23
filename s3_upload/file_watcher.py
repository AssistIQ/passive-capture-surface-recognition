import os
import time
import threading
from interaction_handler import InteractionHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class FileWatcher(FileSystemEventHandler, InteractionHandler):
    def __init__(self, watch_directory, s3_uploader):
        self.s3_uploader = s3_uploader
        self.watch_directory = watch_directory
        self.observer = Observer()
        self.isWatching = True

    def start(self):
        self.observer.schedule(self, path=self.watch_directory, recursive=True)
        self.observer.start()
        self.directory_check_thread = threading.Thread(target=self.check_watch_folder_task)
        self.directory_check_thread.start()

    def stop(self):
        self.isWatching = False
        self.directory_check_thread.join()
        self.observer.stop()
        self.observer.join()
    
    def check_watch_folder_task(self):
        while self.isWatching:
            if not os.path.exists(self.watch_directory):
                print(f"Creating upload_queue folder")
                os.makedirs(self.watch_directory)
            time.sleep(1)

    def queue_interaction(self, file_path):
        interaction_data = self.create_interaction_data(file_path)
        if interaction_data:
            self.s3_uploader.upload_interaction_async(interaction_data)

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if file_path.lower().endswith(('manifest.json')):
            print(f"Queuing interaction: {file_path}")
            self.queue_interaction(file_path)