import os
import zipfile
import shutil
import argparse
from huggingface_hub import hf_hub_download
from medvision_ds.utils.preprocess_utils import move_folder


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: CAMUS
# Challenge: https://www.creatis.insa-lyon.fr/Challenge/camus/
# Data: https://humanheart-project.creatis.insa-lyon.fr/database/#collection/6373703d73e9f0047faa1bc8
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
    # ====================================
    # Download and extract dataset
    for file in ["Images.zip", "Masks.zip"]:
        # Download and extract dataset
        hf_hub_download(
            repo_id="YongchengYAO/CAMUS-Lite",
            filename=file,
            repo_type="dataset",
            revision="b5f71984d0f1c11827a826e19e76cad02aa668ed", # commit hash on 2025-02-20
            local_dir=".",
        )
        print(f"Extracting {file}... This may take some time.") 
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall()
        os.remove(file)

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
