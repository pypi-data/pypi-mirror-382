import os
import argparse
from medvision_ds.utils.preprocess_utils import _get_cgroup_limited_cpus
from medvision_ds.utils.benchmark_planner import MedVision_BenchmarkPlannerSegmentation


# ====================================
# Dataset Info [!]
# Do not change keys in
#  - benchmark_plan
#  - labels_map
# ====================================
dataset_info = {
    "dataset": "MSD",
    "dataset_website": "http://medicaldecathlon.com/dataaws/",
    "dataset_data": [
        "http://medicaldecathlon.com/dataaws/",
    ],
    "license": ["CC BY-SA 4.0"],
    "paper": ["https://doi.org/10.1038/s41467-022-30695-9"],
}

labels_map_BrainTumour = {
    "1": "edema of brain",
    "2": "non-enhancing brain tumor",
    "3": "enhancing brain tumor",
}

labels_map_Colon = {"1": "colon cancer primaries"}

labels_map_Heart = {"1": "left atrium of heart"}

labels_map_HepaticVessel = {"1": "liver vessel", "2": "liver tumor"}

labels_map_Hippocampus = {"1": "anterior hippocampus", "2": "posterior hippocampus"}

labels_map_Liver = {"1": "liver", "2": "liver cancer"}

labels_map_Lung = {
    "1": "lung cancer",
}

labels_map_Pancreas = {"1": "pancreas", "2": "pancreas cancer"}

labels_map_Prostate = {
    "1": "peripheral zone of prostate",
    "2": "transition zone of prostate",
}

labels_map_Spleen = {"1": "spleen"}

benchmark_plan = {
    "dataset_info": dataset_info,
    "tasks": [
        {
            "image_modality": "MRI",
            "image_description": "fluid-attenuated inversion recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-BrainTumour/Images-FLAIR",
            "mask_folder": "MSD-BrainTumour/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_BrainTumour,
        },
        {
            "image_modality": "MRI",
            "image_description": "T1 weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-BrainTumour/Images-T1w",
            "mask_folder": "MSD-BrainTumour/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_BrainTumour,
        },
        {
            "image_modality": "MRI",
            "image_description": "gadolinium-enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-BrainTumour/Images-T1gd",
            "mask_folder": "MSD-BrainTumour/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_BrainTumour,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-BrainTumour/Images-T2w",
            "mask_folder": "MSD-BrainTumour/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_BrainTumour,
        },
        {
            "image_modality": "CT",
            "image_description": "abdominal computed tomography (CT) scan",
            "image_folder": "MSD-Colon/Images",
            "mask_folder": "MSD-Colon/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Colon,
        },
        {
            "image_modality": "MRI",
            "image_description": "cardiac magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-Heart/Images",
            "mask_folder": "MSD-Heart/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Heart,
        },
        {
            "image_modality": "CT",
            "image_description": "abdominal computed tomography (CT) scan",
            "image_folder": "MSD-HepaticVessel/Images",
            "mask_folder": "MSD-HepaticVessel/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_HepaticVessel,
        },
        {
            "image_modality": "MRI",
            "image_description": "hippocampus magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-Hippocampus/Images",
            "mask_folder": "MSD-Hippocampus/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Hippocampus,
        },
        {
            "image_modality": "CT",
            "image_description": "abdominal computed tomography (CT) scan",
            "image_folder": "MSD-Liver/Images",
            "mask_folder": "MSD-Liver/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Liver,
        },
        {
            "image_modality": "CT",
            "image_description": "chest computed tomography (CT) scan",
            "image_folder": "MSD-Lung/Images",
            "mask_folder": "MSD-Lung/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Lung,
        },
        {
            "image_modality": "CT",
            "image_description": "abdominal computed tomography (CT) scan",
            "image_folder": "MSD-Pancreas/Images",
            "mask_folder": "MSD-Pancreas/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Pancreas,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2-weighted prostate magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-Prostate/Images-T2w",
            "mask_folder": "MSD-Prostate/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Prostate,
        },
        {
            "image_modality": "MRI",
            "image_description": "appearance diffusion coefficient (ADC) map of prostate magnetic resonance imaging (MRI) scan",
            "image_folder": "MSD-Prostate/Images-ADC",
            "mask_folder": "MSD-Prostate/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Prostate,
        },
        {
            "image_modality": "CT",
            "image_description": "abdominal computed tomography (CT) scan",
            "image_folder": "MSD-Spleen/Images",
            "mask_folder": "MSD-Spleen/Masks",
            "image_prefix": "",
            "image_suffix": ".nii.gz",
            "mask_prefix": "",
            "mask_suffix": ".nii.gz",
            "labels_map": labels_map_Spleen,
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

    # Process dataset for segmentation task
    planner = MedVision_BenchmarkPlannerSegmentation(
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
        description="Generate benchmark planner for segmentation task."
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
