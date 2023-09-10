import os

DOCS_PATH = '../docs'
DB_PATH = '../cache' 

def create_folder(folder_path):
    if os.path.exists(folder_path):
        return
    os.makedirs(folder_path)
    print(f"Folder '{folder_path}' created successfully!")