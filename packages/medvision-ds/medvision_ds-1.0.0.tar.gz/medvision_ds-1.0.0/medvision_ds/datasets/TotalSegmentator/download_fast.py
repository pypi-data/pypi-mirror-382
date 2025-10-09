import os
import argparse
import shutil
import zipfile
from huggingface_hub import hf_hub_download
from medvision_ds.utils.preprocess_utils import move_folder


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: TotalSegmentator
# GitHub: https://github.com/wasserth/TotalSegmentator
# Data: CT: https://zenodo.org/records/10047292
#       MR: https://zenodo.org/records/14710732
# Preprocessed Data:
#       CT: https://huggingface.co/datasets/YongchengYAO/TotalSegmentator-CT-Lite
#       MR: https://huggingface.co/datasets/YongchengYAO/TotalSegmentator-MR-Lite
# Format: nii.gz
# ====================================


def download_and_extract(dataset_dir, dataset_name, **kwargs):
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
    # Download CT dataset from Hugging Face Hub
    ct_dir = os.path.join(tmp_dir, "TotalSegmentator-CT")
    os.makedirs(ct_dir, exist_ok=True)
    hf_hub_download(
        repo_id="YongchengYAO/TotalSegmentator-CT-Lite",
        filename="Images.zip",
        repo_type="dataset",
        revision="cbbab480af869bf7abc3f4c86da56ef5f6436232",  # commit hash on 2025-04-11
        local_dir=ct_dir,
    )
    hf_hub_download(
        repo_id="YongchengYAO/TotalSegmentator-CT-Lite",
        filename="Masks.zip",
        repo_type="dataset",
        revision="cbbab480af869bf7abc3f4c86da56ef5f6436232",  # commit hash on 2025-04-11
        local_dir=ct_dir,
    )

    # Download MR dataset from Hugging Face Hub
    mr_dir = os.path.join(tmp_dir, "TotalSegmentator-MR")
    os.makedirs(mr_dir, exist_ok=True)
    hf_hub_download(
        repo_id="YongchengYAO/TotalSegmentator-MR-Lite",
        filename="Images.zip",
        repo_type="dataset",
        revision="6d6135d58049c7f5dc694be43b7f0870b55f2392",  # commit hash on 2025-04-11
        local_dir=mr_dir,
    )
    hf_hub_download(
        repo_id="YongchengYAO/TotalSegmentator-MR-Lite",
        filename="Masks.zip",
        repo_type="dataset",
        revision="6d6135d58049c7f5dc694be43b7f0870b55f2392",  # commit hash on 2025-04-11
        local_dir=mr_dir,
    )

    # Extract CT datasets
    print("Extracting files... This may take some time.") 
    with zipfile.ZipFile(os.path.join(ct_dir, "Images.zip"), 'r') as zip_ref:
        zip_ref.extractall(ct_dir)
    with zipfile.ZipFile(os.path.join(ct_dir, "Masks.zip"), 'r') as zip_ref:
        zip_ref.extractall(ct_dir)
    
    # Extract MR datasets
    print("Extracting files... This may take some time.") 
    with zipfile.ZipFile(os.path.join(mr_dir, "Images.zip"), 'r') as zip_ref:
        zip_ref.extractall(mr_dir)
    with zipfile.ZipFile(os.path.join(mr_dir, "Masks.zip"), 'r') as zip_ref:
        zip_ref.extractall(mr_dir)

    # Move folder to dataset_dir
    folders_to_move = [
        "TotalSegmentator-CT",
        "TotalSegmentator-MR",
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
