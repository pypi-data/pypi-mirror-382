import os
import argparse
from medvision_ds.utils.preprocess_utils import _get_cgroup_limited_cpus
from medvision_ds.utils.benchmark_planner import MedVision_BenchmarkPlannerBiometry_fromSeg


# ====================================
# Dataset Info [!]
# Do not change keys in
#  - benchmark_plan
# ====================================
CLUSTER_SIZE_THRESHOLD = 200

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
# ====================================


# ===============
# DO NOT CHANGE
# ===============
landmarks_map = {
    "P1": "most right/anterior/superior endpoint of the major axis",
    "P2": "most left/superior/inferior endpoint of the major axis",
    "P3": "most right/anterior/superior endpoint of the minor axis",
    "P4": "most left/superior/inferior endpoint of the minor axis",
}

lines_map = {
    "L-1-2": {
        "name": "marjor axis of the fitted ellipse",
        "element_keys": ["P1", "P2"],
        "element_map_name": "landmarks_map",
    },
    "L-3-4": {
        "name": "minor axis of the fitted ellipse",
        "element_keys": ["P3", "P4"],
        "element_map_name": "landmarks_map",
    },
}

angles_map = {}

biometrics_map = [
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-1-2",
    },
    {
        "metric_type": "distance",
        "metric_map_name": "lines_map",
        "metric_key": "L-3-4",
    },
]
# ===============


benchmark_plan = {
    "dataset_info": dataset_info,
    "tasks": [
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2f",
            "mask_folder": "BraTS24-GLI/Masks",
            "landmark_folder": "BraTS24-GLI/Landmarks-Label1",
            "landmark_figure_folder": "BraTS24-GLI/Landmarks-Label1-fig",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_GLI,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 1,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2f",
            "mask_folder": "BraTS24-GLI/Masks",
            "landmark_folder": "BraTS24-GLI/Landmarks-Label2",
            "landmark_figure_folder": "BraTS24-GLI/Landmarks-Label2-fig",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_GLI,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 2,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2f",
            "mask_folder": "BraTS24-GLI/Masks",
            "landmark_folder": "BraTS24-GLI/Landmarks-Label3",
            "landmark_figure_folder": "BraTS24-GLI/Landmarks-Label3-fig",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_GLI,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 3,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "T2 Fluid Attenuated Inversion Recovery (FLAIR) brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-GLI/Images-t2f",
            "mask_folder": "BraTS24-GLI/Masks",
            "landmark_folder": "BraTS24-GLI/Landmarks-Label4",
            "landmark_figure_folder": "BraTS24-GLI/Landmarks-Label4-fig",
            "image_prefix": "",
            "image_suffix": "-t2f.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_GLI,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 4,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MEN-RT/Images-t1c",
            "mask_folder": "BraTS24-MEN-RT/Masks",
            "landmark_folder": "BraTS24-MEN-RT/Landmarks-Label1",
            "landmark_figure_folder": "BraTS24-MEN-RT/Landmarks-Label1-fig",
            "image_prefix": "",
            "image_suffix": "_t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "_gtv.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_MEN_RT,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 1,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t1c",
            "mask_folder": "BraTS24-MET/Masks",
            "landmark_folder": "BraTS24-MET/Landmarks-Label1",
            "landmark_figure_folder": "BraTS24-MET/Landmarks-Label1-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_MET,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 1,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t1c",
            "mask_folder": "BraTS24-MET/Masks",
            "landmark_folder": "BraTS24-MET/Landmarks-Label2",
            "landmark_figure_folder": "BraTS24-MET/Landmarks-Label2-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_MET,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 2,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-MET/Images-t1c",
            "mask_folder": "BraTS24-MET/Masks",
            "landmark_folder": "BraTS24-MET/Landmarks-Label3",
            "landmark_figure_folder": "BraTS24-MET/Landmarks-Label3-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_MET,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 3,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1c",
            "mask_folder": "BraTS24-PED/Masks",
            "landmark_folder": "BraTS24-PED/Landmarks-Label1",
            "landmark_figure_folder": "BraTS24-PED/Landmarks-Label1-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_PED,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 1,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1c",
            "mask_folder": "BraTS24-PED/Masks",
            "landmark_folder": "BraTS24-PED/Landmarks-Label2",
            "landmark_figure_folder": "BraTS24-PED/Landmarks-Label2-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_PED,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 2,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1c",
            "mask_folder": "BraTS24-PED/Masks",
            "landmark_folder": "BraTS24-PED/Landmarks-Label3",
            "landmark_figure_folder": "BraTS24-PED/Landmarks-Label3-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_PED,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 3,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
        },
        {
            "image_modality": "MRI",
            "image_description": "contrast enhanced T1-weighted brain magnetic resonance imaging (MRI) scan",
            "image_folder": "BraTS24-PED/Images-t1c",
            "mask_folder": "BraTS24-PED/Masks",
            "landmark_folder": "BraTS24-PED/Landmarks-Label4",
            "landmark_figure_folder": "BraTS24-PED/Landmarks-Label4-fig",
            "image_prefix": "",
            "image_suffix": "-t1c.nii.gz",
            "mask_prefix": "",
            "mask_suffix": "-seg.nii.gz",
            "landmark_prefix": "",
            "landmark_suffix": ".json.gz",
            "labels_map": labels_map_PED,
            "landmarks_map": landmarks_map,
            "lines_map": lines_map,
            "angles_map": angles_map,
            "biometrics_map": biometrics_map,
            "target_label": 4,
            "cluster_size_threshold": CLUSTER_SIZE_THRESHOLD,
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
    shrunken_bbox_scale=0.9,
    enlarged_bbox_scale=1.1,
    force_uint16_mask=False,
    reorient2RAS=False,
    visualization=False,
):
    # Create dataset directory
    dataset_dir = os.path.join(dir_datasets_data, dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)

    # Change to dataset directory
    os.chdir(dataset_dir)

    # Process dataset for segmentation task
    planner = MedVision_BenchmarkPlannerBiometry_fromSeg(
        dataset_dir=dataset_dir,
        bm_plan=benchmark_plan,
        dataset_name=dataset_name,
        seed=random_seed,
        split_ratio=split_ratio,
        shrunk_bbox_scale=shrunken_bbox_scale,
        enlarged_bbox_scale=enlarged_bbox_scale,
        force_uint16_mask=force_uint16_mask,
        reorient2RAS=reorient2RAS,
        visualization=visualization,
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
    parser.add_argument(
        "--shrunken_bbox_scale",
        type=float,
        default=0.9,
        help="Scale factor for shrunken bounding box",
    )
    parser.add_argument(
        "--enlarged_bbox_scale",
        type=float,
        default=1.1,
        help="Scale factor for enlarged bounding box",
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
    parser.add_argument(
        "--visualization",
        action="store_true",
        help="Enable visualization of the dataset processing",
    )
    args = parser.parse_args()

    main(
        benchmark_plan=benchmark_plan,  # global variable
        dir_datasets_data=args.dir_datasets_data,
        dataset_name=args.dataset_name,
        random_seed=args.random_seed,
        split_ratio=args.split_ratio,
        shrunken_bbox_scale=args.shrunken_bbox_scale,
        enlarged_bbox_scale=args.enlarged_bbox_scale,
        force_uint16_mask=args.force_uint16_mask,
        reorient2RAS=args.reorient2RAS,
        visualization=args.visualization,
    )
