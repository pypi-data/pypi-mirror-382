import os
import argparse
from medvision_ds.utils.preprocess_utils import _get_cgroup_limited_cpus
from medvision_ds.utils.benchmark_planner import MedVision_BenchmarkPlannerDetection

# ====================================
# Dataset Info [!]
# Do not change keys in
#  - benchmark_plan
#  - labels_map
# ====================================
dataset_info = {
    "dataset": "ToothFairy2",
    "dataset_website": "https://toothfairy2.grand-challenge.org",
    "dataset_data": [
        "https://ditto.ing.unimore.it/toothfairy2/",
    ],
    "license": ["CC BY-SA"],
    "paper": [
        "https://doi.org/10.1109/TMI.2024.3523096",
        "https://doi.org/10.1109/ACCESS.2024.3408629",
        "https://doi.org/10.1109/CVPR52688.2022.02046",
    ],
}

labels_map = {
    "1": "lower jawbone",
    "2": "upper jawbone",
    "3": "left inferior alveolar canal",
    "4": "right inferior alveolar canal",
    "5": "left maxillary sinus",
    "6": "right maxillary sinus",
    "7": "pharynx",
    "8": "bridge",
    "9": "crown",
    "10": "implant",
    "11": "upper right central incisor",
    "12": "upper right lateral incisor",
    "13": "upper right canine",
    "14": "upper right first premolar",
    "15": "upper right second premolar",
    "16": "upper right first molar",
    "17": "upper right second molar",
    "18": "upper right third molar (wisdom tooth)",
    "21": "upper left central incisor",
    "22": "upper left lateral incisor",
    "23": "upper left canine",
    "24": "upper left first premolar",
    "25": "upper left second premolar",
    "26": "upper left first molar",
    "27": "upper left second molar",
    "28": "upper left third molar (wisdom tooth)",
    "31": "lower left central incisor",
    "32": "lower left lateral incisor",
    "33": "lower left canine",
    "34": "lower left first premolar",
    "35": "lower left second premolar",
    "36": "lower left first molar",
    "37": "lower left second molar",
    "38": "lower left third molar (wisdom tooth)",
    "40": "na",
    "41": "lower right central incisor",
    "42": "lower right lateral incisor",
    "43": "lower right canine",
    "44": "lower right first premolar",
    "45": "lower right second premolar",
    "46": "lower right first molar",
    "47": "lower right second molar",
    "48": "lower right third molar (wisdom tooth)",
}

benchmark_plan = {
    "dataset_info": dataset_info,
    "tasks": [
        {
            "image_modality": "CT",
            "image_description": "cone beam computed tomography (CT) scan",
            "image_folder": "Images",
            "mask_folder": "Masks",
            "image_prefix": "",
            "image_suffix": "_0000.nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map,
        },
    ],
}
# ====================================


def main(
    dir_datasets_data,
    dataset_name,
    benchmark_plan=benchmark_plan,
    random_seed=1024,
    split_ratio=0.7,
    force_uint16_mask=False,
    reorient2RAS=False,
):
    # Create dataset directory
    dataset_dir = os.path.join(dir_datasets_data, dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)

    # Change to dataset directory
    os.chdir(dataset_dir)

    # Process dataset for detection task
    planner = MedVision_BenchmarkPlannerDetection(
        dataset_dir=dataset_dir,
        bm_plan=benchmark_plan,
        dataset_name=dataset_name,
        seed=random_seed,
        split_ratio=split_ratio,
        force_uint16_mask=force_uint16_mask,
        reorient2RAS=reorient2RAS,
        num_proc=_get_cgroup_limited_cpus(),
    )
    planner.process()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate benchmark planner for detection task."
    )
    parser.add_argument(
        "-d",
        "--dir_datasets_data",
        type=str,
        help="Directory path where datasets will be stored",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--dataset_name",
        type=str,
        help="Name of the dataset",
        required=True,
    )
    parser.add_argument(
        "--random_seed",
        type=int,
        default=1024,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--split_ratio",
        type=float,
        default=0.7,
        help="Train/test split ratio (0-1)",
    )
    parser.add_argument(
        "--force_uint16_mask",
        action="store_true",
        help="Force mask to be uint16",
    )
    parser.add_argument(
        "--reorient2RAS",
        action="store_true",
        help="Reorient images and masks to RAS orientation",
    )

    args = parser.parse_args()

    main(
        benchmark_plan=benchmark_plan,  # global variable
        dir_datasets_data=args.dir_datasets_data,
        dataset_name=args.dataset_name,
        random_seed=args.random_seed,
        split_ratio=args.split_ratio,
        force_uint16_mask=args.force_uint16_mask,
        reorient2RAS=args.reorient2RAS,
    )
