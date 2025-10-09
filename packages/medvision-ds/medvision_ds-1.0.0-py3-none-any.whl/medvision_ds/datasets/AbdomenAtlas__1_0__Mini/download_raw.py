import os
import shutil
import argparse
import glob
import nibabel as nib
from tqdm import tqdm
from huggingface_hub import snapshot_download
from medvision_ds.utils.preprocess_utils import move_folder, _get_cgroup_limited_cpus
from medvision_ds.utils.data_conversion import convert_mask_to_uint16_per_dir, copy_img_header_to_mask
from medvision_ds.datasets.AbdomenAtlas__1_0__Mini.preprocess_segmentation import (
    benchmark_plan as AbdomenAtlas1_0_Mini_benchmark_plan,
)


# ====================================
# Dataset Info [!]
# ====================================
# Dataset: AbdomenAtlas1.0Mini
# Website: https://github.com/MrGiovanni/AbdomenAtlas
# Data: https://huggingface.co/datasets/AbdomenAtlas/AbdomenAtlas1.0Mini
# Format: nii.gz
# ====================================


def convert_masks_to_uint16(dataset_dir):
    mask_folders = _get_mask_folders(AbdomenAtlas1_0_Mini_benchmark_plan)
    for folder in mask_folders:
        mask_folder = os.path.join(dataset_dir, folder)
        available_cpus = _get_cgroup_limited_cpus()
        convert_mask_to_uint16_per_dir(mask_folder, workers_limit=available_cpus)



def wrapper_copy_img_header_to_mask(img_files, mask_dir):
    available_cpus = _get_cgroup_limited_cpus()
    copy_img_header_to_mask(img_files, mask_dir, workers_limit=available_cpus)


def _get_mask_folders(bm_plan):
    """Get unique mask folders from tasks"""
    mask_folders = []
    for task in bm_plan["tasks"]:
        mask_folders.append(task["mask_folder"])
    return list(set(mask_folders))


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
    dest_dir = "Images-raw"
    snapshot_download(
        repo_id="AbdomenAtlas/AbdomenAtlas1.0Mini",
        repo_type="dataset",
        local_dir=dest_dir,
        revision="4dff62f03f7e4f17cd8c62617bc75fde9893a1e9",  # commit hash on 2025-02-20
        max_workers=kwargs.get('max_workers', 1),
    )

    # Create Images and Masks directories
    os.makedirs("Images", exist_ok=True)
    os.makedirs("Masks", exist_ok=True)

    # Process each case folder
    for case_dir in glob.glob(os.path.join(dest_dir, "BDMAP*")):
        if os.path.isdir(case_dir):
            case_name = os.path.basename(case_dir)
            # Move CT images
            ct_src = os.path.join(case_dir, "ct.nii.gz")
            if os.path.exists(ct_src):
                shutil.move(ct_src, os.path.join("Images", f"{case_name}.nii.gz"))
            # Move mask files
            mask_src = os.path.join(case_dir, "combined_labels.nii.gz")
            if os.path.exists(mask_src):
                shutil.move(mask_src, os.path.join("Masks", f"{case_name}.nii.gz"))

    # Copy Nifti header of images to masks (Multiprocessing)
    print("Copying Nifti headers from images to masks...")
    img_files = list(glob.glob(os.path.join("Images", "*.nii.gz")))
    wrapper_copy_img_header_to_mask(img_files, "Masks")

    # Convert masks to uint16 (Multiprocessing)
    convert_masks_to_uint16(tmp_dir)

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
