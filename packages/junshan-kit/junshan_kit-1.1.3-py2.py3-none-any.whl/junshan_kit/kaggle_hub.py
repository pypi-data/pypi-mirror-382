import kagglehub
import os
import shutil

def read_data(data_name = 'evpd-test', copy_path = None):
    path = kagglehub.dataset_download(f'junshan888/{data_name}')
    # print("Downloaded to:", path)
    if copy_path is not None:
        # Create target directory if it doesn't exist
        os.makedirs(copy_path, exist_ok=True)
        # Copy dataset to target directory
        shutil.copytree(path, copy_path, dirs_exist_ok=True)

        print(f"✅ Dataset has been copied to: {copy_path}/{data_name}")

# example: read_data(copy_path='./exp_data')
