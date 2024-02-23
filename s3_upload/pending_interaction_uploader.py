import os
from interaction_handler import InteractionHandler

class PendingInteractionUploader(InteractionHandler):
    def __init__(self, s3_uploader, folder_path):
        self.folder_path = folder_path
        self.s3_uploader = s3_uploader

    def get_pending_interactions(self):
        # look for files names manifest.json in the folder, these files can be within subfolders
        pending_interactions = []
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith("manifest.json"):
                    pending_interactions.append(root)
                    break
        return pending_interactions
    
    def upload_pending_interactions(self):
        pending_interactions = self.get_pending_interactions()
        print(f"Pending interactions: {pending_interactions}")
        for interaction in pending_interactions:
            file_path = f"{interaction}/manifest.json"
            interaction_data = self.create_interaction_data(file_path)
            if interaction_data:
                self.s3_uploader.upload_interaction_async(interaction_data)