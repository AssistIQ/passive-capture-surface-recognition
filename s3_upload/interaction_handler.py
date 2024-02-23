import json
import os

class InteractionHandler:
    def create_interaction_data(self, manifest_path):
        interaction_data = self.get_json_data(manifest_path)
        if not interaction_data:
            return None

        local_folder_path = os.path.dirname(manifest_path)

        metadata_path = f"{local_folder_path}/metadata.json"
        metadata = self.get_json_data(metadata_path)
        if not metadata:
            return None
        interaction_data.update(metadata)

        interaction_data['local_folder_path'] = local_folder_path
        interaction_data['manifest_file'] = manifest_path
        interaction_data['metadata_file'] = metadata_path

        return interaction_data
    
    def get_json_data(self, path):
        file = open(path)
        try: 
            data = json.load(file)
            return data
        except Exception as e:
            # LOG TO CLOUDWATCH
            print(f"Error parsing json file {path}: {str(e)}")
            return None    