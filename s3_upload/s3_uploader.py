import os
import threading
import time

import boto3
import boto3.session

class S3Uploader:
    def __init__(self, access_key, secret_key, bucket_name, folder_path):
        self.bucket_name = bucket_name
        self.folder_path = folder_path
        self.access_key = access_key
        self.secret_key = secret_key
        self.MAX_UPLOAD_RETRIES = 10

    def upload_interaction_async(self, interaction_data):
        thread = threading.Thread(target=self.upload_interaction_task, args=(interaction_data,))
        thread.daemon = True
        thread.start()

    def decode_interaction_data(self, interaction_data):
        try:
            files = interaction_data['files']
            interaction_id = interaction_data['interactionId']
            deviceId = interaction_data['deviceId']
            return (interaction_id, deviceId, files)
        except KeyError as e:
            # LOG TO CLOUDWATCH
            print(f"Error decoding interaction data: {e}")
            return None
        
    def upload_interaction_task(self, interaction_data):
        decoded = self.decode_interaction_data(interaction_data)
        if not decoded:
            return
        
        interaction_id, deviceId, files = decoded
        s3_folder = f'{deviceId}/{interaction_id}/'
        total_files = len(files) + 2 # +1 for the metadata file, +1 for the manifest file
        num_files_uploaded = 0

        for file_name in files:
            local_path = f'{interaction_data["local_folder_path"]}/{file_name}'

            if not os.path.exists(local_path):
                # LOG TO CLOUDWATCH
                print(f"File {local_path} does not exist!")
                continue

            if self.upload_file_task(local_path, s3_folder + file_name):
                num_files_uploaded += 1
            

        if self.upload_file_task(interaction_data['metadata_file'], s3_folder + 'metadata.json'):
            num_files_uploaded += 1

        if num_files_uploaded != total_files - 1:
            # LOG TO CLOUDWATCH
            print(f"Only {num_files_uploaded} out of {total_files} files were uploaded for interaction {s3_folder}.")
            return

        if self.upload_file_task(interaction_data['manifest_file'], s3_folder + 'manifest.json'):
            num_files_uploaded += 1
    
        self.cleanup_local_folder(interaction_data["local_folder_path"])
        print(f"Interaction {s3_folder} uploaded to s3!")

    def upload_file_task(self, local_path, s3_key):
        retries = 0
        while retries < self.MAX_UPLOAD_RETRIES and not self.upload_file(local_path, s3_key):
            retries += 1
            time.sleep(5)

        if retries == self.MAX_UPLOAD_RETRIES:
            # LOG TO CLOUDWATCH
            print(f"Failed to upload file {local_path} to s3 after {self.MAX_UPLOAD_RETRIES} retries!")
            return False
        
        self.cleanup_local_file(local_path)
        return True
    
    def upload_file(self, local_path, s3_key):
        # boto3 s3 resource is not thread safe (cannot be shared), need to create a new one per thread.
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html#multithreading-or-multiprocessing-with-resources
        session = boto3.session.Session()
        s3 = session.resource('s3', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

        try:
            s3.meta.client.upload_file(local_path, self.bucket_name, s3_key)
            return True
        except Exception as e:
            # LOG TO CLOUDWATCH
            print(f"Error uploading file: {str(e)}")
            return False
        
    def cleanup_local_file(self, local_path):
        os.system(f'rm -f {local_path}')

    def cleanup_local_folder(self, interaction_folder):
        os.system(f'rm -rf {interaction_folder}')