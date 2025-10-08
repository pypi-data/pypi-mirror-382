"""Parser module to parse gear config.json."""

import logging
import typing as t
from dataclasses import dataclass
from pathlib import Path

import psutil
from flywheel_gear_toolkit import GearToolkitContext
from fw_file.dicom import get_config
from humanize import naturalsize

from fw_gear_dicom_fixer.utils import calculate_decompressed_size

log = logging.getLogger(__name__)


@dataclass
class GearArgs:
    """Arguments to be used for dicom-fixer processing.

    dicom_path: Path to DICOM input
    output_dir: Path to output directory
    transfer_syntax: Whether to standardize transfer syntax
    unique: Whether to remove duplicates
    zip_single: Whether to zip single DICOM output
    new_uids_needed: Whether new UIDS are needed
    convert_palette: Whether to convert palette color images to RGB
    pixel_data_check: Whether to check if pixel data is valid
    rename_zip_members: Whether to rename members of zip archive
    """

    dicom_path: Path
    output_dir: Path
    transfer_syntax: bool
    unique: bool
    zip_single: str
    new_uids_needed: bool
    convert_palette: bool
    pixel_data_check: bool
    rename_zip_members: bool


def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[GearArgs, bool]:
    """Parse config.json and return relevant inputs and options.

    Args:
        gear_context (GearToolkitContext): Gear context object.

    Returns:
        GearArgs: dataclass of argument values to be used by the gear
        bool: Fail status, Whether gear should fail due to OOM
    """
    # Set config
    config = get_config()
    config.reading_validation_mode = (
        "2" if gear_context.config.get("strict-validation", True) else "1"
    )
    if gear_context.config.get("dicom-standard", "local") == "current":
        config.standard_rev = "current"
    if not gear_context.config.get("fix-uids", True):
        config.fix_uids = False

    # Check memory availability and filesize to catch potential OOM kill
    # on decompression if transfer_syntax == True
    input_path = Path(gear_context.get_input_path("dicom")).resolve()
    transfer_syntax = gear_context.config.get("standardize-transfer-syntax", False)
    force_decompress = gear_context.config.get("force-decompress")

    fail_status = False
    if transfer_syntax:
        current_memory = psutil.virtual_memory().used
        decompressed_size = calculate_decompressed_size(input_path)
        total_memory = psutil.virtual_memory().total
        if (current_memory + decompressed_size) > (0.7 * total_memory):
            if force_decompress is True:
                log.warning(
                    "DICOM file may be too large for decompression:\n"
                    f"\tEstimated decompressed size: {naturalsize(decompressed_size)}\n"
                    f"\tCurrent memory usage: {naturalsize(current_memory)}\n"
                    f"\tTotal memory: {naturalsize(total_memory)}\n"
                    "force-decompress is set to True, continuing as configured."
                )
            else:
                log.warning(
                    "DICOM file may be too large for decompression:\n"
                    f"\tEstimated decompressed size: {naturalsize(decompressed_size)}\n"
                    f"\tCurrent memory usage: {naturalsize(current_memory)}\n"
                    f"\tTotal memory: {naturalsize(total_memory)}\n"
                    "To avoid gear failure due to OOM, standardize-transfer-syntax "
                    "will be switched to False and the DICOM will not be decompressed. "
                    "To force decompression, re-run gear with `force-decompress=True`."
                )
                transfer_syntax = False
                fail_status = True

    # If modality is set as RTSTRUCT, skip pixel data check
    input_modality = gear_context.get_input_file_object_value("dicom", "modality")
    if input_modality == "RTSTRUCT":
        log.info("File modality is RTSTRUCT; pixel data check will not be performed.")
        pixel_data_check = False
    else:
        pixel_data_check = gear_context.config.get("pixel-data-check", True)

    gear_args = GearArgs(
        dicom_path=input_path,
        output_dir=gear_context.output_dir,
        transfer_syntax=transfer_syntax,
        unique=gear_context.config.get("unique", False),
        zip_single=gear_context.config.get("zip-single-dicom", "match"),
        new_uids_needed=gear_context.config.get("new-uids-needed", False),
        convert_palette=gear_context.config.get("convert-palette", True),
        pixel_data_check=pixel_data_check,
        rename_zip_members=gear_context.config.get("rename-zip-members", True),
    )

    return gear_args, fail_status
