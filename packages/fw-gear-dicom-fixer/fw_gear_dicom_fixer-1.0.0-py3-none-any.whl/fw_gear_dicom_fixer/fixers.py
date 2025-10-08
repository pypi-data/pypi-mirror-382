"""DICOM fixer functions."""

import contextlib
import logging
import os
import typing as t
from difflib import get_close_matches
from warnings import warn

import numpy as np
from fw_file.dicom import DICOM, get_config
from fw_file.dicom.reader import ReplaceEvent
from pydicom import config as pydicom_config
from pydicom.charset import decode_element
from pydicom.datadict import tag_for_keyword
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset
from pydicom.pixels import apply_color_lut, convert_color_space
from pydicom.uid import ExplicitVRLittleEndian as standard

log = logging.getLogger(__name__)

LUT_TAGS = [
    "RedPaletteColorLookupTableDescriptor",
    "RedPaletteColorLookupTableData",
    "GreenPaletteColorLookupTableDescriptor",
    "GreenPaletteColorLookupTableData",
    "BluePaletteColorLookupTableDescriptor",
    "BluePaletteColorLookupTableData",
]

# Black likes to format this with one entry on each line...
# fmt: off
MODALITIES = [
    "ANN", "AR", "ASMT", "AU", "BDUS", "BI", "BMD", "CR", "CT", "CTPROTOCOL",
    "DMS", "DG", "DOC", "DX", "ECG", "EEG", "EMG", "EOG", "EPS", "ES", "FID",
    "GM", "HC", "HD", "IO", "IOL", "IVOCT", "IVUS", "KER", "KO", "LEN", "LS",
    "MG", "MR", "M3D", "NM", "OAM", "OCT", "OP", "OPM", "OPT", "OPTBSV",
    "OPTENF", "OPV", "OSS", "OT", "PLAN", "Note", "POS", "PR", "PT", "PX",
    "REG", "RESP", "RF", "RG", "RTDOSE", "RTIMAGE", "RTINTENT", "RTPLAN",
    "RTRAD", "RTRECORD", "RTSEGANN", "RTSTRUCT", "RWV", "SEG", "SM", "SMR",
    "SR", "SRF", "STAIN", "TEXTUREMAP", "TG", "US", "VA", "XA", "XAPROTOCOL",
    "XC",
]
# fmt: on

# Type 1 file-meta tags
# https://dicom.nema.org/dicom/2013/output/chtml/part10/chapter_7.html#table_7.1-1
FILE_META_TAGS = {
    "FileMetaInformationGroupLength",
    "FileMetaInformationVersion",
    "TransferSyntaxUID",
    "MediaStorageSOPClassUID",
    "MediaStorageSOPInstanceUID",
    "ImplementationClassUID",
}


def is_dcm(dcm: DICOM) -> bool:
    """Look at a potential dicom and see whether it actually is a dicom.

    Must have all file-meta tags to be considered an actual dicom.

    Args:
        dcm (DICOM): DICOM

    Returns:
        bool: True if it probably is a dicom, False if not
    """
    file_meta = dcm.dataset.raw.file_meta
    file_meta_present = {tag for tag in FILE_META_TAGS if tag in file_meta}
    f_name = os.path.basename(dcm.localpath) if dcm.localpath else ""
    if len(file_meta_present) != len(FILE_META_TAGS):
        diff = FILE_META_TAGS - file_meta_present
        sop_class_uid = dcm.dataset.raw.get("SOPClassUID")
        if sop_class_uid:
            log.debug(f"{f_name}: Missing file-meta tags {diff}")
            return True
        log.warning(
            f"Removing {f_name}: Missing file-meta tags {diff}, and no SOP UIDs"
        )
        return False
    return True


def fix_patient_sex(dcm: DICOM) -> t.Optional[ReplaceEvent]:
    """Fix PatientSex attribute on a dicom.

    Returns:
        ReplaceEvent or None
    """
    if hasattr(dcm, "PatientSex"):
        sex = dcm.PatientSex
        if sex in ["M", "O", "F", ""]:
            return None
        match = get_close_matches(sex.lower(), ["male", "female", "other"], n=1)
        if match:
            if match[0] == "male":
                dcm.PatientSex = "M"
            elif match[0] == "female":
                dcm.PatientSex = "F"
            else:
                dcm.PatientSex = "O"
        else:
            warn(f"Could not find match for PatientSex '{sex}' Setting as empty")
            dcm.PatientSex = ""
        return ReplaceEvent("PatientSex", sex, dcm.PatientSex)
    return None


def fix_incorrect_units(dcm: DICOM) -> t.Optional[ReplaceEvent]:
    """Fix known incorrect units.

    Returns:
        ReplaceEvent or None
    """
    # MagneticFieldStrength should be in Tesla, if larger than 30, it's
    # probably milli-Tesla, so divide by 1000 to put in Tesla
    if hasattr(dcm, "MagneticFieldStrength"):
        mfs = dcm.MagneticFieldStrength
        if mfs:
            if mfs > 30:
                dcm.MagneticFieldStrength = mfs / 1000
                return ReplaceEvent(
                    "MagneticFieldStrength", mfs, dcm.MagneticFieldStrength
                )
    return None


def fix_invalid_modality(dcm: DICOM) -> t.Optional[ReplaceEvent]:
    """Fix invalid Modality field."""
    if hasattr(dcm, "Modality"):
        existing_modality = dcm.Modality
        if existing_modality is None:
            dcm.Modality = "OT"
        elif existing_modality not in MODALITIES:
            # Search for close matches, return at most 1
            match = get_close_matches(existing_modality, MODALITIES, n=1)
            # If there is a match, use that, otherwise set to OT for other.
            if match:
                dcm.Modality = match[0]
            else:
                dcm.Modality = "OT"
        else:
            return None
        return ReplaceEvent("Modality", existing_modality, dcm.Modality)
    dcm.Modality = "OT"
    return ReplaceEvent("Modality", None, dcm.Modality)


def apply_fixers(dcm: DICOM) -> t.List[ReplaceEvent]:
    """Apply all post-decoding fixers to a DICOM.

    Return a list of ReplaceEvent's for anything that was changed/fixed.
    """
    evts: t.List[ReplaceEvent] = []
    fixers = [fix_patient_sex, fix_incorrect_units, fix_invalid_modality]
    for fixer in fixers:
        evt = fixer(dcm)
        if evt:
            evts.append(evt)
    return evts


def decode_dcm(dcm: DICOM) -> None:
    """Decode dicom.

       Mirrors pydicom.dataset.Dataset.decode, except it ignores decoding the
       OriginalAttributesSequence tag.

    Args:
        dcm (DICOM): dicom file.
    """
    dicom_character_set = dcm.dataset.raw._character_set

    def decode(dataset: Dataset, data_element: DataElement) -> None:
        """Callback to decode data element, but ignore OriginalAttributesSequence."""
        if data_element.VR == "SQ":
            if data_element.tag == tag_for_keyword("OriginalAttributesSequence"):
                return

            # In pydicom 2.4.1, parent_dataset is not set when decoding from a
            # sequence of undefined length, whereas it is when reading from a
            # defined length sequence

            # The reason for this is that the parent_dataset is set in the
            # DataElement constructor and when reading from undefined length
            # sequence, the data_element_generator yields a RawDataElement
            # instead of a DataElement, for probably necessary reasons

            # As of pydicom 2.4.3 this is fixed, but it is fixed to just ignore
            # this error, here we explicitely set the parent dataset and parent
            # sequences to ensure they are present.

            # Note that the setter for these values handles turns the passed
            # value into a weakref
            data_element.value.parent_dataset = dataset
            for dset in data_element.value:
                dset.parent_seq = data_element.value
                dset._parent_encoding = dicom_character_set
                dset.decode()
        else:
            decode_element(data_element, dicom_character_set)

    # Walk through file meta dataset as well as main.
    dcm.dataset.raw.file_meta.walk(decode, recursive=False)
    dcm.walk(decode, recursive=False)


@contextlib.contextmanager
def no_dataelem_fixes():
    """Context manager that empties callbacks/fixers."""
    config = get_config()
    orig_raw_VR_fixers = config.raw_VR_fixers
    orig_raw_value_fixers = config.raw_value_fixers
    config.raw_VR_fixers = []
    config.raw_value_fixers = []
    orig_wrong_len = pydicom_config.convert_wrong_length_to_UN
    orig_vr_from_un = pydicom_config.replace_un_with_known_vr
    # NOTE: Ensure there is no VR inference or fixes applied
    # when testing if a DataElement can be written as is.
    pydicom_config.replace_un_with_known_vr = False
    pydicom_config.convert_wrong_length_to_UN = False
    try:
        yield
    finally:
        config.raw_VR_fixers = orig_raw_VR_fixers
        config.raw_value_fixers = orig_raw_value_fixers
        pydicom_config.replace_un_with_known_vr = orig_vr_from_un
        pydicom_config.convert_wrong_length_to_UN = orig_wrong_len


def convert_color_space_fixer(  # noqa: PLR0912
    dcm: DICOM, convert_palette=False
) -> str:  # pragma: no cover
    """Convert image color space to RGB."""
    p_i = dcm.get("PhotometricInterpretation")
    modality = dcm.get("Modality")
    bits_allocated = dcm.get("BitsAllocated")

    if not p_i or p_i == "RGB":
        return

    if p_i in ["PALETTE COLOR"]:
        if convert_palette:
            converted = apply_color_lut(dcm.dataset.raw.pixel_array, dcm)
            # Going from a single sample per pixel (palette) to RGB
            dcm.SamplesPerPixel = 3
            dcm.PhotometricInterpretation = "RGB"
            # Additionally need planar configuration of samples per pixel
            # if > 1
            dcm.PlanarConfiguration = 0
            if converted.dtype == "uint16":
                if modality in ["US", "IVUS"]:
                    log.info("Converting 16-bit RGB to 8-bit.")
                    # If the modality is US or IVUS, the pixel data should be
                    # first normalized to 8-bit values
                    converted = (
                        (converted - converted.min()) / (np.ptp(converted))
                    ) * 255
                    # Convert the normalized pixel array to an 8-bit array
                    converted = converted.astype(np.uint8)
                    # Update the DICOM header with the new pixel data
                    dcm.BitsAllocated = 8
                    dcm.BitsStored = 8
                    dcm.HighBit = 7
                elif dcm.BitsAllocated == 8 and modality not in ["US", "IVUS"]:
                    log.warning(
                        "[Palette Color] Changing Bits Allocated from 8-bit to 16-bit "
                        "Please make sure this is valid for this modality, if it is not"
                        ", set `convert_palette` to False in the gear config."
                    )
                    # If output is a 16 bit array, need to update the bits stored/allocated
                    dcm.BitsAllocated = 16
                    dcm.BitsStored = 16
                    dcm.HighBit = 15
            # Remove now unneeded lookup table tags
            for tag in LUT_TAGS:
                try:
                    del dcm[tag]
                except KeyError:
                    continue
            dcm.PixelData = converted.tobytes()
        else:
            log.info("Found Palette Color but Palette Color conversion not specified.")
    elif p_i in ["MONOCHROME1", "MONOCHROME2"]:
        log.debug("No colorspace to convert for grayscale image.")
    elif bits_allocated > 8:
        raise ValueError(
            f"Color space conversion not supported for {bits_allocated}-bit images with PhotometricInterpretation of {p_i}."
        )
    elif p_i in ["YBR_FULL_422", "YBR_FULL"]:
        converted = convert_color_space(dcm.dataset.raw.pixel_array, p_i, "RGB")
        dcm.PhotometricInterpretation = "RGB"
        dcm.PixelData = converted.tobytes()
    elif p_i == "YBR_RCT":
        converted = convert_color_space(dcm.dataset.raw.pixel_array, "YBR_FULL", "RGB")
        dcm.PhotometricInterpretation = "RGB"
        dcm.PixelData = converted.tobytes()
    else:
        raise ValueError(
            f"PhotometricInterpretation {p_i} not supported. "
            "Please email support@flywheel.io with a copy of "
            "your file if possible."
        )
    new_color = (
        f"Replace {p_i} -> {dcm.PhotometricInterpretation} {dcm.BitsAllocated}-bit"
    )
    return new_color


def standardize_transfer_syntax(
    dcm: DICOM, convert_palette=True
) -> str:  # pragma: no cover
    """Set TransferSyntaxUID to ExplicitVRLittleEndian.

    Args:
        dcm (DICOM): dicom file.

    Returns:
        from_to (str): Event or empty string
        new_color (str): Event or empty string
    """
    # Attempt to decompress dicom PixelData with GDCM if compressed
    found_ts = dcm.dataset.raw.file_meta.TransferSyntaxUID
    found_name = getattr(found_ts, "name", found_ts)
    if "JPEG" in found_name:
        # JPEG PlanarConfiguration always 0, fix before decompression
        dcm.PlanarConfiguration = 0
    f_name = os.path.basename(dcm.localpath) if dcm.localpath else ""
    if found_ts == standard:
        log.debug(
            f"{f_name}: Found {found_name} TransferSyntax. No conversion necessary."
        )
    else:
        from_to = f"Replace {found_name} -> {standard.name}"
        log.debug(f"{f_name}: Converting TransferSyntax: {from_to}")
        # NOTE: Decompression is only for encapsulated pixel data which only
        # applies to `PixelData`, not `FloatPixelData` or `DoubleFloatPixelData`:
        #   https://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_A.4
        if found_ts.is_compressed and "PixelData" in dcm:
            log.debug(f"{f_name}: Decompressing")
            try:
                # NOTE: GDCM is the first handler that is tried when none is
                # explicitly specified. Ideally we could use pylibjpeg as a
                # handler here, however it doesn't seem to handle as much as
                # GDCM does.
                #
                # The problem with GDCM is that when it does run into an error,
                # it just logs to stderr without our being able to intercept the
                # error. The workaround is checking for "empty" pixel data after
                # conversion (max value is 0).
                dcm.dataset.raw.decompress(as_rgb=True)
            except (RuntimeError, ValueError) as exc:
                log.error(
                    f"Could not decompress {f_name} ({found_name}). Error: {exc.args}"
                )
                raise
            except AttributeError as exc:
                log.error(
                    f"Could not decompress {f_name} ({found_name}). Error: {exc.args}"
                    "This may be caused by the size of the file being too large to decompress."
                )
                raise
        new_color = convert_color_space_fixer(dcm, convert_palette)
        dcm.dataset.raw.file_meta.TransferSyntaxUID = standard
        return from_to, new_color
    return "", ""
