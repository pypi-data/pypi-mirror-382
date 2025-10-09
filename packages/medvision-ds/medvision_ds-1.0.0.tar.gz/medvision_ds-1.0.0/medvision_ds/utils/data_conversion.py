import SimpleITK as sitk
import os
import glob
import nrrd
import nibabel as nib
import numpy as np
import cv2
import traceback
import psutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def _reorient_niigz_RASplus(nifti_path, output_path):
    """
    Load a NIfTI file, reorient it to RAS+ (right-anterior-superior) using as_closest_canonical,
    and save the result while preserving the original data type.
    """
    # Load the image
    img = nib.load(nifti_path)
    # Get original data type
    original_dtype = img.get_fdata().dtype
    # Check current orientation
    current_orientation = nib.aff2axcodes(img.affine)
    if current_orientation == ("R", "A", "S"):
        msg = f"{nifti_path} is already in RAS+ orientation.\n"
        if nifti_path != output_path:
            nib.save(img, output_path)
        return msg
    # Convert to RAS+ orientation
    canonical_img = nib.as_closest_canonical(img)
    # Create new image with original dtype
    reoriented_data = canonical_img.get_fdata().astype(original_dtype)
    new_img = nib.Nifti1Image(reoriented_data, canonical_img.affine, header=img.header)
    # Preserve original header information where possible
    new_img.header.set_data_dtype(original_dtype)
    # Save the reoriented image
    nib.save(new_img, output_path)
    msg = f"Converted {nifti_path} to RAS+ orientation and saved as {output_path}.\n"
    return msg


def reorient_niigz_RASplus_batch_inplace(dataset_dir, workers_limit=1):
    """
    Reorient all NIfTI files in a directory and its subdirectories to RAS+ orientation in place.
    This function modifies the original files rather than creating new ones.

    Args:
        dataset_dir (str): Directory containing .nii.gz files
        workers_limit (int): Maximum number of worker processes. Defaults to 1.
    """
    # Find all .nii.gz files recursively in directory
    nii_files = list(glob.glob(f"{dataset_dir}/**/*.nii.gz", recursive=True))
    total_files = len(nii_files)
    num_workers = min(workers_limit, total_files) if workers_limit > 0 else 1
    print(f"Reorienting {total_files} files to RAS+ orientation...\n")

    # Multi-process dataset reorientation
    preprocessed_files_count = 0
    failed_cases = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(_reorient_niigz_RASplus, nii_file, nii_file): nii_file
            for nii_file in nii_files
        }

        for fut in as_completed(futures):
            nii_file = futures[fut]
            try:
                msg = fut.result()
                preprocessed_files_count += 1
                print(
                    f"✓ Reoriented {os.path.basename(nii_file)}: ({preprocessed_files_count}/{total_files})"
                )
                print(f" - {msg}")

                mem = psutil.virtual_memory().percent
                if mem > 80:
                    print(f"⚠️  High memory usage: {mem}%")

            except Exception:
                err = traceback.format_exc()
                print(
                    f"❌ Reorienting {os.path.basename(nii_file)} generated an exception:\n{err}"
                )
                failed_cases.append((nii_file, err))

    if failed_cases:
        print(f"❌ Failed to reorient {len(failed_cases)} files:")
        for nii_file, e in failed_cases:
            print(f"  - {os.path.basename(nii_file)}: {e.splitlines()[-1]}")
        raise RuntimeError("Some tasks failed to reorient. See logs above.")


def convert_nrrd_to_nifti(input_dir, output_dir, recursive=False):
    """
    Convert all .nrrd files in input_dir to .nii.gz files in output_dir

    Args:
        input_dir (str): Directory containing .nrrd files
        output_dir (str): Directory to save .nii.gz files
        recursive (bool): If True, search for .nrrd files in subdirectories
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all .nrrd files in input directory
    pattern = "**/*.nrrd" if recursive else "*.nrrd"
    nrrd_files = list(Path(input_dir).glob(pattern))

    print(f"Found {len(nrrd_files)} .nrrd files")

    for nrrd_file in nrrd_files:
        try:
            print(f"Converting {nrrd_file.name}")

            # Read NRRD file
            data, header = nrrd.read(str(nrrd_file))

            # Get spacing (voxel size)
            space_directions = header.get("space directions")
            if space_directions is not None:
                voxel_size = np.array(
                    [np.linalg.norm(dir) for dir in space_directions if dir is not None]
                )
                print("Voxel dimensions calculated from spatial direction matrix")
            else:
                raise ValueError(
                    "No space directions found in NRRD header. Cannot determine voxel size."
                )

            # Get origin
            origin = header.get("space origin", [0.0, 0.0, 0.0])

            # Create affine matrix
            affine = np.eye(4)
            if space_directions is not None:
                affine[:3, :3] = np.array(
                    [dir if dir is not None else [0, 0, 0] for dir in space_directions]
                )
            else:
                affine[:3, :3] = np.diag(voxel_size)
            affine[:3, 3] = origin

            # Create NIfTI image
            nifti_img = nib.Nifti1Image(data, affine)

            # Set additional header information
            nifti_header = nifti_img.header
            nifti_header.set_zooms(voxel_size)

            # Create output filename
            output_file = Path(output_dir) / f"{nrrd_file.stem}.nii.gz"

            # Save NIfTI file
            nib.save(nifti_img, str(output_file))
            print(f"Saved to {output_file}")

        except Exception as e:
            print(f"Error converting {nrrd_file.name}: {e}")


def convert_mha_to_nifti(input_dir, output_dir, recursive=False):
    """
    Convert all .mha files in input_dir to .nii.gz files in output_dir

    Args:
        input_dir (str): Directory containing .mha files
        output_dir (str): Directory to save .nii.gz files
        recursive (bool): If True, search for .mha files in subdirectories
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all .mha files in input directory
    pattern = "**/*.mha" if recursive else "*.mha"
    mha_files = list(Path(input_dir).glob(pattern))

    print(f"Found {len(mha_files)} .mha files")

    for mha_file in mha_files:
        try:
            # Read .mha file
            print(f"Converting {mha_file.name}")
            image = sitk.ReadImage(str(mha_file))

            # Create output filename
            output_file = Path(output_dir) / f"{mha_file.stem}.nii.gz"

            # Write as .nii.gz
            sitk.WriteImage(image, str(output_file))
            print(f"Saved to {output_file}")

        except Exception as e:
            print(f"Error converting {mha_file.name}: {e}")


def convert_nii_to_niigz(input_dir, output_dir, recursive=False):
    """
    Convert all .nii files in input_dir to .nii.gz files in output_dir

    Args:
        input_dir (str): Directory containing .nii files
        output_dir (str): Directory to save .nii.gz files
        recursive (bool): If True, search for .nii files in subdirectories
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all .nii files in input directory
    pattern = "**/*.nii" if recursive else "*.nii"
    nii_files = list(Path(input_dir).glob(pattern))

    print(f"Found {len(nii_files)} .nii files")

    for nii_file in nii_files:
        try:
            # Read .nii file
            print(f"Converting {nii_file.name}")
            image = sitk.ReadImage(str(nii_file))

            # Create output filename
            output_file = Path(output_dir) / f"{nii_file.stem}.nii.gz"

            # Write as .nii.gz
            sitk.WriteImage(image, str(output_file))
            print(f"Saved to {output_file}")

        except Exception as e:
            print(f"Error converting {nii_file.name}: {e}")


def _convert_mask_to_uint16(mask_path):
    # Load nii
    nii = nib.load(mask_path)
    hdr = nii.header.copy()

    # Convert data to uint16 type
    # NOTE: When you cast to uint16 in NumPy, it truncates toward zero, it does not round
    # e.g., 1.99995422.astype(np.uint16) → 1
    data = np.rint(nii.get_fdata()).astype(np.uint16)

    # Force header consistency
    if hdr.get_data_dtype() != np.dtype("uint16"):
        hdr.set_data_dtype(np.uint16)

    # Force no scaling
    slope, inter = hdr.get_slope_inter()
    # NOTE: In NIfTI headers, scl_slope and scl_inter can be stored as NaN to mean "no scaling", i.e., both (1, 0) or (NaN, NaN) mean "no scaling"
    # Check if slope and inter are numeric before using np.isfinite
    slope_valid = slope is not None and np.isfinite(slope) and slope == 1
    inter_valid = inter is not None and np.isfinite(inter) and inter == 0
    if not (slope_valid and inter_valid):
        hdr.set_slope_inter(1.0, 0.0)

    out = nib.Nifti1Image(data, nii.affine, hdr)
    nib.save(out, mask_path)


def convert_mask_to_uint16_per_dir(mask_folder, workers_limit=1):
    """
    Convert all .nii.gz mask files in a folder to uint16 data type with proper header settings.
    This is useful for segmentation masks where we want integer labels without scaling.

    Args:
        mask_folder (str): Path to folder containing mask files
    """
    # List all .nii.gz files in the mask folder
    mask_files = [f for f in os.listdir(mask_folder) if f.endswith(".nii.gz")]
    total_files = len(mask_files)
    num_workers = min(workers_limit, total_files) if workers_limit > 0 else 1
    print(f"Found {total_files} .nii.gz mask files to convert")

    # Multi-process dataset concatenation
    preprocessed_files_count = 0
    failed_cases = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                _convert_mask_to_uint16, os.path.join(mask_folder, mask_file)
            ): mask_file
            for mask_file in mask_files
        }

        for fut in as_completed(futures):
            mask_file = futures[fut]
            try:
                fut.result()
                preprocessed_files_count += 1
                print(
                    f"✓ Converted {mask_file}: ({preprocessed_files_count}/{total_files})"
                )

                mem = psutil.virtual_memory().percent
                if mem > 80:
                    print(f"⚠️  High memory usage: {mem}%")

            except Exception:
                err = traceback.format_exc()
                print(f"❌ Converting {mask_file} generated an exception:\n{err}")
                failed_cases.append((mask_file, err))
    if failed_cases:
        print(f"❌ Failed to preprocessed {len(failed_cases)} files:")
        for mask_file, e in failed_cases:
            print(f"  - {mask_file}: {e.splitlines()[-1]}")
        raise RuntimeError("Some tasks failed to load. See logs above.")


def _copy_img_header_to_mask(img_file, mask_dir):
    base_name = os.path.basename(img_file)
    mask_file = os.path.join(mask_dir, base_name)
    if os.path.exists(mask_file):
        img = nib.load(img_file)
        mask = nib.load(mask_file)
        new_mask = nib.Nifti1Image(mask.get_fdata(), img.affine)
        nib.save(new_mask, mask_file)
    return mask_file


def copy_img_header_to_mask(img_files, mask_dir, workers_limit=1):
    assert os.path.exists(mask_dir), "mask_dir must exist"
    total_files = len(img_files)
    num_workers = min(workers_limit, total_files) if workers_limit > 0 else 1
    print(f"Found {total_files} .nii.gz mask files to convert")

    # Multi-process dataset concatenation
    preprocessed_files_count = 0
    failed_cases = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(_copy_img_header_to_mask, img_file, mask_dir): img_file
            for img_file in img_files
        }

        for fut in as_completed(futures):
            img_file = futures[fut]
            try:
                mask_file = fut.result()
                preprocessed_files_count += 1
                print(
                    f"✓ Converted {mask_file}: ({preprocessed_files_count}/{total_files})"
                )

                mem = psutil.virtual_memory().percent
                if mem > 80:
                    print(f"⚠️  High memory usage: {mem}%")

            except Exception:
                err = traceback.format_exc()
                print(
                    f"❌ Copying header from {img_file} generated an exception:\n{err}"
                )
                failed_cases.append((img_file, err))
    if failed_cases:
        print(f"❌ Failed to preprocessed {len(failed_cases)} files:")
        for img_file, e in failed_cases:
            print(f"  - {img_file}: {e.splitlines()[-1]}")
        raise RuntimeError("Some tasks failed to load. See logs above.")


def convert_bmp_to_niigz(
    bmp_dir,
    niigz_dir,
    slice_dim_type,
    pseudo_voxel_size,
    flip_dim0=False,
    flip_dim1=False,
    swap_dim01=False,
):
    """
    Convert BMP image files to NIfTI (.nii.gz) format.
    This function converts 2D BMP images to 3D NIfTI volumes with specified slice orientation.
    The output NIfTI files will have RAS+ orientation with specified voxel size.
    Args:
        bmp_dir (str): Input directory containing BMP files to convert
        niigz_dir (str): Output directory where NIfTI files will be saved
        slice_dim_type (int): Slice dimension/orientation type:
            0: Sagittal (YZ plane)
            1: Coronal (XZ plane)
            2: Axial (XY plane)
        pseudo_voxel_size (list): List of 3 floats specifying voxel dimensions in mm [x,y,z]
        flip_dim0 (bool, optional): If True, flip image along dimension 0. Defaults to False.
        flip_dim1 (bool, optional): If True, flip image along dimension 1. Defaults to False.
        swap_dim01 (bool, optional): If True, swap dimensions 0 and 1. Defaults to False.
    Returns:
        tuple: Original image dimensions (height, width) of the first converted BMP
    """

    # Validate slice_dim_type
    if slice_dim_type not in [0, 1, 2]:
        raise ValueError("slice_dim_type must be 0, 1, or 2")

    # Convert pseudo_voxel_size to list if it's not already
    pseudo_voxel_size = list(pseudo_voxel_size)

    # Create output directory
    Path(niigz_dir).mkdir(parents=True, exist_ok=True)

    # Get all BMP files
    bmp_files = list(Path(bmp_dir).glob("*.bmp"))
    print(f"Found {len(bmp_files)} .bmp files")

    for bmp_file in bmp_files:
        try:
            print(f"Converting {bmp_file.name}")

            # Read BMP image
            img_2d = cv2.imread(str(bmp_file), cv2.IMREAD_GRAYSCALE)
            img_size_dim0, img_size_dim1 = img_2d.shape

            # Note: this is definitely correct, DO NOT SWAP the order of transformations
            if flip_dim0:
                img_2d = cv2.flip(img_2d, 0)  # 0 means flip vertically
            if flip_dim1:
                img_2d = cv2.flip(img_2d, 1)  # 1 means flip horizontally
            if swap_dim01:  # this line should be AFTER slip_x and slip_y
                img_2d = np.swapaxes(img_2d, 0, 1)

            # Create 3D array based on slice_dim_type
            if slice_dim_type == 0:  # Sagittal (YZ plane)
                img_3d = np.zeros(
                    (1, img_2d.shape[0], img_2d.shape[1]), dtype=img_2d.dtype
                )
                img_3d[0, :, :] = img_2d
            elif slice_dim_type == 1:  # Coronal (XZ plane)
                img_3d = np.zeros(
                    (img_2d.shape[0], 1, img_2d.shape[1]), dtype=img_2d.dtype
                )
                img_3d[:, 0, :] = img_2d
            else:  # Axial (XY plane)
                img_3d = np.zeros(
                    (img_2d.shape[0], img_2d.shape[1], 1), dtype=img_2d.dtype
                )
                img_3d[:, :, 0] = img_2d

            # Create affine matrix for RAS+ orientation
            # Set voxel size to 0.1mm in all dimensions
            affine = np.diag(pseudo_voxel_size + [1])

            # Create NIfTI image
            nii_img = nib.Nifti1Image(img_3d, affine)

            # Set header information
            nii_img.header.set_zooms(pseudo_voxel_size)

            # Save as NIfTI file
            output_file = Path(niigz_dir) / f"{bmp_file.stem}.nii.gz"
            nib.save(nii_img, str(output_file))
            print(f"Saved to {output_file}")

        except Exception as e:
            print(f"Error converting {bmp_file.name}: {e}")

    return img_size_dim0, img_size_dim1


def convert_jpg_to_niigz(
    jpg_dir,
    niigz_dir,
    slice_dim_type,
    pseudo_voxel_size,
    flip_dim0=False,
    flip_dim1=False,
    swap_dim01=False,
):
    """
    Convert JPG image files to NIfTI (.nii.gz) format.
    This function converts 2D JPG images to 3D NIfTI volumes with specified slice orientation.
    The output NIfTI files will have RAS+ orientation with specified voxel size.
    Args:
        jpg_dir (str): Input directory containing JPG files to convert
        niigz_dir (str): Output directory where NIfTI files will be saved
        slice_dim_type (int): Slice dimension/orientation type:
            0: Sagittal (YZ plane)
            1: Coronal (XZ plane)
            2: Axial (XY plane)
        pseudo_voxel_size (list): List of 3 floats specifying voxel dimensions in mm [x,y,z]
        flip_dim0 (bool, optional): If True, flip image along dimension 0. Defaults to False.
        flip_dim1 (bool, optional): If True, flip image along dimension 1. Defaults to False.
        swap_dim01 (bool, optional): If True, swap dimensions 0 and 1. Defaults to False.
    Returns:
        tuple: Original image dimensions (height, width) of the first converted JPG
    """

    # Validate slice_dim_type
    if slice_dim_type not in [0, 1, 2]:
        raise ValueError("slice_dim_type must be 0, 1, or 2")

    # Convert pseudo_voxel_size to list if it's not already
    pseudo_voxel_size = list(pseudo_voxel_size)

    # Create output directory
    Path(niigz_dir).mkdir(parents=True, exist_ok=True)

    # Get all JPG files
    jpg_files = list(Path(jpg_dir).glob("*.jpg"))
    print(f"Found {len(jpg_files)} .jpg files")

    for jpg_file in jpg_files:
        try:
            print(f"Converting {jpg_file.name}")

            # Read JPG image
            img_2d = cv2.imread(str(jpg_file), cv2.IMREAD_GRAYSCALE)
            img_size_dim0, img_size_dim1 = img_2d.shape

            # Note: this is definitely correct, DO NOT SWAP the order of transformations
            if flip_dim0:
                img_2d = cv2.flip(img_2d, 0)  # 0 means flip vertically
            if flip_dim1:
                img_2d = cv2.flip(img_2d, 1)  # 1 means flip horizontally
            if swap_dim01:  # this line should be AFTER flip_dim0 and flip_dim1
                img_2d = np.swapaxes(img_2d, 0, 1)

            # Create 3D array based on slice_dim_type
            if slice_dim_type == 0:  # Sagittal (YZ plane)
                img_3d = np.zeros(
                    (1, img_2d.shape[0], img_2d.shape[1]), dtype=img_2d.dtype
                )
                img_3d[0, :, :] = img_2d
            elif slice_dim_type == 1:  # Coronal (XZ plane)
                img_3d = np.zeros(
                    (img_2d.shape[0], 1, img_2d.shape[1]), dtype=img_2d.dtype
                )
                img_3d[:, 0, :] = img_2d
            else:  # Axial (XY plane)
                img_3d = np.zeros(
                    (img_2d.shape[0], img_2d.shape[1], 1), dtype=img_2d.dtype
                )
                img_3d[:, :, 0] = img_2d

            # Create affine matrix for RAS+ orientation
            # Set voxel size to 0.1mm in all dimensions
            affine = np.diag(pseudo_voxel_size + [1])

            # Create NIfTI image
            nii_img = nib.Nifti1Image(img_3d, affine)

            # Set header information
            nii_img.header.set_zooms(pseudo_voxel_size)

            # Save as NIfTI file
            output_file = Path(niigz_dir) / f"{jpg_file.stem}.nii.gz"
            nib.save(nii_img, str(output_file))
            print(f"Saved to {output_file}")

        except Exception as e:
            print(f"Error converting {jpg_file.name}: {e}")

    return img_size_dim0, img_size_dim1
