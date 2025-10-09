import os
import shutil
import argparse
import zipfile
from huggingface_hub import hf_hub_download
from medvision_ds.utils.preprocess_utils import move_folder


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: ISLES24
# Challenge: https://isles-24.grand-challenge.org
# Data:
# - Original: https://isles-24.grand-challenge.org/dataset/
# - Huggingface Dataset: https://huggingface.co/datasets/YongchengYAO/ISLES24-MR-Lite
# Format: nii.gz
# ====================================


def download_and_extract(dataset_dir, dataset_name, **kwargs):
    """
    Download and extract the AbdomenAtlas dataset.

    NOTE: Function signature: the first 2 arguments must be dataset_dir and dataset_name
    the other arguments must be kwargs
    """
    # Download files
    current_dir = os.getcwd()
    os.chdir(dataset_dir)
    tmp_dir = os.path.join(dataset_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    os.chdir(tmp_dir)
    print(f"Downloading {dataset_name} dataset to {dataset_dir}...")

    # ====================================
    # Add download logic here [!]
    # Download dataset from Hugging Face Hub
    files_to_download = ["Images-DWI.zip", "Images-ADC.zip", "Masks.zip"]
    for filename in files_to_download:
        hf_hub_download(
            repo_id="YongchengYAO/ISLES24-MR-Lite",
            filename=filename,
            repo_type="dataset",
            revision="16bedc54a9c1e4c32672f7a6ffdc838a3a195946", # commit hash on 2025-07-07
            local_dir=".",
        )

    # Extract the downloaded zip files
    for filename in files_to_download:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall()

    # Move folder to dataset_dir
    folders_to_move = [
        "Images-DWI",
        "Images-ADC",
        "Masks",
    ]
    for folder in folders_to_move:
        move_folder(
            os.path.join(tmp_dir, folder),
            os.path.join(dataset_dir, folder),
            create_dest=True,
        )
    # ====================================

    print(f"Download and extraction completed for {dataset_name}")
    os.chdir(dataset_dir)
    shutil.rmtree(tmp_dir)
    os.chdir(current_dir)


def main(dir_datasets_data, dataset_name, **kwargs):
    # Create dataset directory
    dataset_dir = os.path.join(dir_datasets_data, dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)

    # Change to dataset directory
    os.chdir(dataset_dir)

    # Download and extract dataset
    download_and_extract(dataset_dir, dataset_name, **kwargs)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download and extract dataset")
    parser.add_argument(
        "-d",
        "--dir_datasets_data",
        help="Directory path where datasets will be stored",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--dataset_name",
        help="Name of the dataset",
        required=True,
    )
    args = parser.parse_args()

    main(
        dir_datasets_data=args.dir_datasets_data,
        dataset_name=args.dataset_name,
    )
