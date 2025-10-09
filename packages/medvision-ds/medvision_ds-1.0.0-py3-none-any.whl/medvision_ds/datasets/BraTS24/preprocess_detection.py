import os
import argparse
from medvision_ds.utils.preprocess_utils import _get_cgroup_limited_cpus
from medvision_ds.utils.benchmark_planner import MedVision_BenchmarkPlannerDetection


# ====================================
# Dataset Info [!]
# Do not change keys in
#  - benchmark_plan
# ====================================
dataset_info = {
    "dataset": "",
    "dataset_website": "https://www.synapse.org/Synapse:syn53708249/wiki/",
    "dataset_data": [
        "https://www.synapse.org/Synapse:syn59059776",  # GLI
        "https://www.synapse.org/Synapse:syn59059764",  # MET
        "https://www.synapse.org/Synapse:syn59059779",  # MEN-RT
        "https://www.synapse.org/Synapse:syn58894466",  # PED
    ],
    "license": [""],
    "paper": [
        "https://doi.org/10.48550/arXiv.2405.18368",  # GLI
        "",  # MET
        "https://doi.org/10.48550/arXiv.2405.18383",  # MEN-RT
        "https://doi.org/10.48550/arXiv.2404.15009",  # PED
    ],
}

labels_map_GLI = {
    "1": "non-enhancing brain tumor core",
    "2": "surrounding non-enhancing flair hyperintensity of brain",
    "3": "enhancing brain tumor tissue",
    "4": "resection cavity of brain",
}

labels_map_MET = {
    "1": "non-enhancing brain tumor core",
    "2": "surrounding non-enhancing flair hyperintensity of brain",
    "3": "enhancing brain tumor tissue",
}

labels_map_MEN_RT = {"1": "gross tumor volume of brain"}

labels_map_PED = {
    "1": "enhancing brain tumor",
    "2": "non-enhancing brain tumor",
    "3": "cystic component of brain",
    "4": "peritumoral edema of brain",
}

benchmark_plan = {
    "dataset_info": dataset_info,
    "tasks": [
        {
            "image_modality": "MRI",
            "image_description": "gadolinium-enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t1c",
            "mask_folder": "BraTS24-GLI/Masks",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_GLI,
        },
        {
            "image_modality": "MRI",
            "image_description": "non-contrast T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t1n",
            "mask_folder": "BraTS24-GLI/Masks",
            "image_prefix": "",
            "image_suffix": "-t1n.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_GLI,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2f",
            "mask_folder": "BraTS24-GLI/Masks",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_GLI,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2w",
            "mask_folder": "BraTS24-GLI/Masks",
            "image_prefix": "",
            "image_suffix": "-t2w.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_GLI,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MEN-RT/Images-t1c",
            "mask_folder": "BraTS24-MEN-RT/Masks",
            "image_prefix": "",
            "image_suffix": "_t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "_gtv.nii.gz",
            "labels_map": labels_map_MEN_RT,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t1c",
            "mask_folder": "BraTS24-MET/Masks",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_MET,
        },
        {
            "image_modality": "MRI",
            "image_description": "non-contrast T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t1n",
            "mask_folder": "BraTS24-MET/Masks",
            "image_prefix": "",
            "image_suffix": "-t1n.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_MET,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t2f",
            "mask_folder": "BraTS24-MET/Masks",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_MET,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t2w",
            "mask_folder": "BraTS24-MET/Masks",
            "image_prefix": "",
            "image_suffix": "-t2w.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_MET,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1c",
            "mask_folder": "BraTS24-PED/Masks",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_PED,
        },
        {
            "image_modality": "MRI",
            "image_description": "non-contrast T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1n",
            "mask_folder": "BraTS24-PED/Masks",
            "image_prefix": "",
            "image_suffix": "-t1n.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_PED,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t2f",
            "mask_folder": "BraTS24-PED/Masks",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_PED,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t2w",
            "mask_folder": "BraTS24-PED/Masks",
            "image_prefix": "",
            "image_suffix": "-t2w.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "labels_map": labels_map_PED,
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
