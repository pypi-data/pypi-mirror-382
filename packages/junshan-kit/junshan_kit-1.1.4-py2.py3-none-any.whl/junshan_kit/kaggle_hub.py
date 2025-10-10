import kagglehub
import os
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi

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


def list_user_datasets(username = 'junshan888'):
    api = KaggleApi()
    api.authenticate()

    # Get the list of datasets for a specific user
    datasets = api.dataset_list(user='junshan888')

    print('*' * 60)
    if datasets is not None:
        for ds in datasets:
            if ds is not None:
                # Print the dataset title
                print(ds.title)
    print('*' * 60)
list_user_datasets()
