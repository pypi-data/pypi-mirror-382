import os
import argparse
from medvision_ds.utils.preprocess_utils import _get_cgroup_limited_cpus
from medvision_ds.utils.benchmark_planner import MedVision_BenchmarkPlannerBiometry


# ====================================
# Dataset Info [!]
# Do not change keys in
#  - benchmark_plan
# ====================================
dataset_info = {
    "dataset": "FeTA24",
    "dataset_website": "https://fetachallenge.github.io",
    "dataset_data": [
        "https://www.synapse.org/Synapse:syn25649159/wiki/610007",
    ],
    "license": [""],
    "paper": ["https://zenodo.org/records/10986046"],
}

landmarks_map = {
    "P1": "most anterior point of corpus callosum",
    "P2": "most posterior point of corpus callosum",
    "P3": "most superior point of vermis",
    "P4": "most inferior point of vermis",
    "P5": "right parietal eminence ",
    "P6": "left parietal eminence",
    "P7": "right skull parietal eminence",
    "P8": "left skull parietal eminence",
    "P9": "most right point of cerebellar hemisphere",
    "P10": "most left point of cerebellar hemisphere",
}

lines_map = {
    "L-1-2": {
        "name": "length of corpus callosum",
        "element_keys": ["P1", "P2"],
        "element_map_name": "landmarks_map",
    },
    "L-3-4": {
        "name": "height of vermis",
        "element_keys": ["P3", "P4"],
        "element_map_name": "landmarks_map",
    },
    "L-5-6": {
        "name": "brain biparietal diameter",
        "element_keys": ["P5", "P6"],
        "element_map_name": "landmarks_map",
    },
    "L-7-8": {
        "name": "skull biparietal diameter",
        "element_keys": ["P7", "P8"],
        "element_map_name": "landmarks_map",
    },
    "L-9-10": {
        "name": "transverse cerebellar diameter",
        "element_keys": ["P9", "P10"],
        "element_map_name": "landmarks_map",
    },
}

angles_map = {}

biometrics_map = [
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-1-2",
        "slice_dim": 0,
    },
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-3-4",
        "slice_dim": 0,
    },
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-5-6",
        "slice_dim": 2,
    },
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-7-8",
        "slice_dim": 2,
    },
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-9-10",
        "slice_dim": 1,
    },
]


# ------------
# Task-specific benchmark planning configuration
# ------------
# - dataset_info: Dictionary containing dataset metadata
# - tasks: List of task configurations where each task contains:
#   - image_modality: Type of medical imaging (e.g., "CT", "MRI")
#   - image_description: Description of image, used in text prompts
#   - image_folder: Directory for .nii.gz image files
#   - landmark_folder: Directory for landmark files
#   - image_prefix: Filename part before case ID for images
#   - image_suffix: Filename part after case ID for images
#   - landmark_prefix: Filename part before case ID for landmarks
#   - landmark_suffix: Filename part after case ID for landmarks
#   - landmarks_map: Dictionary mapping landmarks to their descriptions
# NOTE:
# - These keys should match the variable names:
#        "landmarks_map": landmarks_map,
#         "lines_map": lines_map,
#         "angles_map": angles_map,
#         "biometrics_map": biometrics_map,
# ------------
benchmark_plan = {
    "dataset_info": dataset_info,
    "tasks": [
        {
            "image_modality": "",
            "image_description": "",
            "image_folder": "Images-reoriented",
            "landmark_folder": "Landmarks",
            "image_prefix": "",
            "image_suffix": "_T2w.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
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
):
    # Create dataset directory
    dataset_dir = os.path.join(dir_datasets_data, dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)

    # Change to dataset directory
    os.chdir(dataset_dir)

    # Process dataset for segmentation task
    planner = MedVision_BenchmarkPlannerBiometry(
        dataset_dir=dataset_dir,
        bm_plan=benchmark_plan,
        dataset_name=dataset_name,
        seed=random_seed,
        split_ratio=split_ratio,
        num_proc=_get_cgroup_limited_cpus(),
    )
    planner.process()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate benchmark planner for biometric measurement task."
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
    args = parser.parse_args()

    main(
        benchmark_plan=benchmark_plan,  # global variable
        dir_datasets_data=args.dir_datasets_data,
        dataset_name=args.dataset_name,
        random_seed=args.random_seed,
        split_ratio=args.split_ratio,
    )
