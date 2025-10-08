"""Utility module for helpful functions."""

import logging
import zipfile
from pathlib import Path

from fw_file.dicom import DICOMCollection, get_config
from fw_file.dicom.utils import sniff_dcm

from .fixers import is_dcm

log = logging.getLogger(__name__)


def calculate_decompressed_size(dicom_path: str) -> int:
    """Estimate size of the decompressed file.

    Assists in calculating whether the container has enough memory available
    to successfully decompress without running afoul of the OOM killer.

    Args:
        dicom_path: Path to directory containing dicom files

    Returns:
        int: Estimated size of decompressed file in bytes
    """
    single_dcm = sniff_dcm(dicom_path)
    is_zip = zipfile.is_zipfile(str(dicom_path))
    if not single_dcm and not is_zip:
        raise RuntimeError(
            "Invalid file type passed in, not a DICOM nor a Zip Archive."
        )

    config = get_config()
    original_validation_mode = config.reading_validation_mode
    try:
        config.reading_validation_mode = 1
        # We're only loading in to check a handful of tags here,
        # so strict-validation can be off momentarily.
        if single_dcm:
            dcms = DICOMCollection(dicom_path, filter_fn=is_dcm, force=True)
        else:  # is_zip
            dcms = DICOMCollection.from_zip(dicom_path, filter_fn=is_dcm, force=True)
        config.reading_validation_mode = original_validation_mode
    except:  # noqa
        log.warning(
            "Unable to estimate size of decompressed file before fixes are run. Continuing."
        )
        # Make doubly sure this gets reset
        config.reading_validation_mode = original_validation_mode
        return 0

    if len(dcms) > 1:
        frames = len(dcms)
    elif len(dcms) == 1:
        frames = dcms.get("NumberOfFrames")
        if not frames:
            try:
                frames = len(dcms.get("PerFrameFunctionalGroupsSequence"))
            except TypeError:
                frames = 1
    else:  # len(dcms) == 0:
        # No valid dicoms is handled later on in dicom-fixer,
        # so for now, we're logging and moving on.
        log.warning(
            "Unable to estimate size of decompressed file; no valid dicoms found."
        )
        return 0

    rows = dcms.bulk_get("Rows")
    cols = dcms.bulk_get("Columns")
    samples = dcms.bulk_get("SamplesPerPixel")
    allocated = dcms.bulk_get("BitsAllocated")

    try:
        max_rows = float(max([i for i in rows if i is not None]))
        max_cols = float(max([i for i in cols if i is not None]))
        max_samples = float(max([i for i in samples if i is not None]))
        max_allocated = float(max([i for i in allocated if i is not None]))

    except ValueError:
        # If above max + list comprehension raises a ValueError, then
        # all values in one or more utilized tags is None
        log.warning(
            "Unable to estimate size of decompressed file due to missing tags. Continuing."
        )
        return 0

    total_bytes = (
        max_rows
        * max_cols
        * frames
        * max_samples
        * max_allocated
        / 8  # convert from bits to bytes
    )
    return total_bytes


def identity_instance_name_fn(dcm):
    """Return the original DICOM instance file name as-is.

    Args:
        dcm: A DICOM object or similar with a 'file' attribute.

    Returns:
        str: The file name without path components.
    """
    if isinstance(dcm.file, Path):
        return dcm.file.name
    elif isinstance(dcm.file, str):
        return Path(dcm.file).name
    else:
        return Path(dcm.file.file.name).name
