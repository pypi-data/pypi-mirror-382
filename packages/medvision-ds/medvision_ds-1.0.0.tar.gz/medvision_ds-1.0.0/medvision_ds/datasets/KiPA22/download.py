import os
import shutil
import argparse
import zipfile
from huggingface_hub import hf_hub_download
from medvision_ds.utils.preprocess_utils import move_folder


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: KiPA22
# Challenge: https://kipa22.grand-challenge.org
# Data: https://kipa22.grand-challenge.org/dataset/
# Format: nii.gz
# ====================================


# Define HuggingFace dataset ID
BiometricVQA_KiPA22_HF_ID = os.environ.get(
    "BiometricVQA_KiPA22_HF_ID", "YongchengYAO/KiPA22"
)


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
    # ====================================
    # Download dataset from HuggingFace
    if BiometricVQA_KiPA22_HF_ID == "YongchengYAO/KiPA22":
        hf_hub_download(
            repo_id=BiometricVQA_KiPA22_HF_ID,
            filename="train.zip",
            repo_type="dataset",
            revision="5d5761d6e4a17e911eca558b251d2f3e4650b85e",  # commit hash on 2025-02-07
            local_dir=".",
        )
    else:
        hf_hub_download(
            repo_id=BiometricVQA_KiPA22_HF_ID,
            filename="train.zip",
            repo_type="dataset",
            local_dir=".",
        )

    # Extract zip file
    with zipfile.ZipFile("train.zip", "r") as zip_ref:
        zip_ref.extractall()

    # Move directories to standard locations
    shutil.rmtree("Images") if os.path.exists("Images") else None
    shutil.rmtree("Masks") if os.path.exists("Masks") else None
    shutil.move(os.path.join("train", "image"), "Images")
    shutil.move(os.path.join("train", "label"), "Masks")

    # Move folder to dataset_dir
    folders_to_move = [
        "Images",
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
