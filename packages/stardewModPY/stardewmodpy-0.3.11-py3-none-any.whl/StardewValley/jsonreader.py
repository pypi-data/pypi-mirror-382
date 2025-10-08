import os, re, json, zipfile

class jsonStardewRead():
    def __init__(self):
        self.file_extension = '.zip'

    def remove_trailing_commas(self, json_string):
        # Remove apenas comentários de bloco
        json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.S)
        
        # Remove vírgulas pendentes após objetos e arrays
        json_string = re.sub(r',(\s*[\]}])', r'\1', json_string)
        # Remove vírgulas pendentes em arrays e objetos vazios
        json_string = re.sub(r',(\s*])', r'\1', json_string)
        json_string = re.sub(r',(\s*})', r'\1', json_string)
        
        return json_string
    
    def read_json(self, path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            try:
                content = f.read()
                cleaned_content = self.remove_trailing_commas(content)
                json_data = json.loads(cleaned_content)
                return json_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error in file {path}: {e}")
            except IOError as e:
                print(f"Error opening file {path}: {e}")
            except UnicodeDecodeError as e:
                print(f"Error decoding file {path} as UTF-8: {e}")
    
    def get_keys(self, json_data):
        if isinstance(json_data, dict):
            return list(json_data.keys())
        else:
            print("Provided data is not a dictionary.")
            return []
    
    def write_json(self, path, json_data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    def compress(self, folder_path:str, output_path:str, root_folder_name:str):
        with zipfile.ZipFile(output_path + self.file_extension, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(root_folder_name, os.path.relpath(file_path, folder_path))
                    zipf.write(file_path, arcname)

    def decompress(self, archive_path, extract_path):
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_path)