import os
import shutil
import argparse
import glob
import zipfile
from huggingface_hub import snapshot_download
from medvision_ds.utils.preprocess_utils import move_folder


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: OAIZIB-CM
# Website: https://github.com/YongchengYAO/CartiMorph
# Data: https://huggingface.co/datasets/YongchengYAO/OAIZIB-CM
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
    # Download dataset
    snapshot_download(
        repo_id="YongchengYAO/OAIZIB-CM",
        allow_patterns="*.zip",
        repo_type="dataset",
        revision="ba18c844309f6288b51772fd79a8f7cdb6aabc01",  # commit hash on 2025-05-06
        local_dir=".",
        max_workers=kwargs.get('max_workers', 1),
    )

    # Extract all zip files
    for zip_file in glob.glob("*.zip"):
        print(f"extracting {zip_file}")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('.')
        os.remove(zip_file)
        print(f"{zip_file} deleted")

    # Move test files to training directories
    for f in glob.glob(os.path.join("imagesTs", "*.nii.gz")):
        shutil.move(f, os.path.join("imagesTr", os.path.basename(f)))
    for f in glob.glob(os.path.join("labelsTs", "*.nii.gz")):
        shutil.move(f, os.path.join("labelsTr", os.path.basename(f)))

    # Rename directories to standard format
    shutil.rmtree("Images") if os.path.exists("Images") else None
    shutil.rmtree("Masks") if os.path.exists("Masks") else None 
    shutil.move("imagesTr", "Images")
    shutil.move("labelsTr", "Masks")

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
    parser.add_argument(
        "--max_workers",
        type=int,
        default=1,
        help="Maximum number of workers for download",
    )
    args = parser.parse_args()

    # Extract known arguments and pass the rest as kwargs
    kwargs = {"max_workers": args.max_workers}
    
    main(
        dir_datasets_data=args.dir_datasets_data,
        dataset_name=args.dataset_name,
        **kwargs
    )
