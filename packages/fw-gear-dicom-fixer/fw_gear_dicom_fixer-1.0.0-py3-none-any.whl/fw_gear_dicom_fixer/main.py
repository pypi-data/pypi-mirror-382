"""Main module."""

import hashlib
import logging
import traceback
import typing as t
import warnings
import zipfile
from collections import defaultdict

from fw_file.dicom import DICOM, DICOMCollection, get_config
from fw_file.dicom.utils import get_instance_filename, sniff_dcm
from fw_file.dicom.validation import get_standard
from pydicom.datadict import keyword_for_tag

from .fixers import apply_fixers, decode_dcm, is_dcm, standardize_transfer_syntax
from .metadata import (
    add_missing_uid,
    generate_and_set_new_uid,
    update_modified_dicom_info,
)
from .parser import GearArgs
from .utils import identity_instance_name_fn

log = logging.getLogger(__name__)

# Suppress pydicom logging, added in 3.0.0. Duplicates log
logging.getLogger("pydicom").setLevel(logging.CRITICAL + 1)

# Constant for max length of the events for a given tag
MAX_EVENT_LENGTH = 10


def run(  # noqa: PLR0912 PLR0915
    gear_args: GearArgs,
    uid_seeds: t.Optional[dict] = None,
) -> t.Optional[t.Tuple[str, t.Dict[str, t.List[str]]]]:
    """Run dicom fixer.

    Args:
        gear_args: Dataclass of arguments to be used to configure gear run
        uid_seeds: If applicable, seeds for generating new UIDs

    Returns:
        out_name: Name of the output file. If None, indicates gear failure
        dict: Events dictionary with DICOM tags as keys, and sets of
            replace events as values. If None, indicates gear failure.
    """
    events: t.Dict[str, t.Set[str]] = defaultdict(set)
    log.info("Loading dicom")
    sops: t.Set[str] = set()
    hashes: t.Set[str] = set()
    to_del: t.List[int] = []
    updated_transfer_syntax = False
    updated_color = False
    # Reasons for both the gear to fail AND QC to be marked as fail
    # are accumulated in fail_reason.
    # Reasons for the gear to be marked as complete BUT QC to be marked as fail
    # are accumulated in qc_fail_reason.
    gear_fail = False
    fail_reason = []
    qc_fail = False
    qc_fail_reason = []

    # First check dicom signature since zip file signature is more likely to
    # have false positives [GEAR-2841]
    single_dcm = sniff_dcm(gear_args.dicom_path)
    is_zip = zipfile.is_zipfile(str(gear_args.dicom_path))
    if not single_dcm and not is_zip:
        raise RuntimeError(
            "Invalid file type passed in, not a DICOM nor a Zip Archive."
        )

    eof_fix = False
    config = get_config()
    original_validation_mode = config.reading_validation_mode
    # There are some fixes that pydicom seems to apply "quietly", and we want to catch them.
    # Known example: EOFError when delimiter (fffe, e0dd) not found.
    # Therefore, set reading_validation_mode to RAISE for first attempt.
    config.reading_validation_mode = 2
    try:
        if single_dcm:
            dcms = DICOMCollection(gear_args.dicom_path, filter_fn=is_dcm, force=True)
        else:  # is_zip
            dcms = DICOMCollection.from_zip(
                gear_args.dicom_path, filter_fn=is_dcm, force=True
            )
    except EOFError as e:
        log.warning(e)
        log.info("Attempting to read DICOM with validation set to warn...")
        # If EOFError is hit, save output, as pydicom quietly fixes error on write.
        eof_fix = True
        # Re-attempt DICOMCollection init with WARN, so the file can be parsed and fixed.
        config.reading_validation_mode = 1
        if single_dcm:
            dcms = DICOMCollection(gear_args.dicom_path, filter_fn=is_dcm, force=True)
        else:  # is_zip
            dcms = DICOMCollection.from_zip(
                gear_args.dicom_path, filter_fn=is_dcm, force=True
            )
        config.reading_validation_mode = original_validation_mode
    except Exception as e:
        # If another exception is hit, RAISE if original_validation_mode is 2
        if original_validation_mode == 2:
            log.error(e)
            raise
    # If strict-validation == True, results of reading in as RAISE should be kept.
    # Otherwise, we want to re-initialize the DICOMCollection with the user-chosen validation
    if original_validation_mode != config.reading_validation_mode:
        config.reading_validation_mode = original_validation_mode
        if single_dcm:
            dcms = DICOMCollection(gear_args.dicom_path, filter_fn=is_dcm, force=True)
        else:  # is_zip
            dcms = DICOMCollection.from_zip(
                gear_args.dicom_path, filter_fn=is_dcm, force=True
            )

    # Download and cache the DICOM standard as needed before we start reading
    # decoding dicoms.
    get_standard()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        coll_len = len(dcms)
        if not coll_len:
            log.info("No valid dicoms found, exiting.")
            return (None, [])
        decis = int(coll_len / 10) or 1
        log.info(f"Processing {coll_len} files in collection")
        for i, dcm in enumerate(dcms):
            if i % decis == 0:
                log.info(f"{i}/{coll_len} ({100 * i / coll_len:.2f}%)")
            filename = dcm.filepath.split("/")[-1]
            if gear_args.unique:
                dcm_hash, sop_instance = get_uniqueness(dcm)
                if dcm_hash in hashes or sop_instance in sops:
                    log.warning(f"Found duplicate dicom at {filename}")
                    to_del.append(i)
                    continue
                hashes.add(dcm_hash)
                sops.add(sop_instance)
            decode_dcm(dcm)
            if gear_args.transfer_syntax:
                try:
                    result = standardize_transfer_syntax(dcm, gear_args.convert_palette)
                    if not result:
                        updated_transfer_syntax, updated_color = False, False
                    else:
                        updated_transfer_syntax, updated_color = result
                except AttributeError:
                    gear_fail = True
                    fail_reason.append("Decompression failed due to large file size")
            if gear_args.pixel_data_check:
                pixel_data_exists = (
                    True
                    if (
                        dcm.get("FloatPixelData")
                        or dcm.get("DoubleFloatPixelData")
                        or dcm.get("PixelData")
                    )
                    else False
                )
                if pixel_data_exists:
                    try:
                        dcm.dataset.raw.pixel_array
                    except Exception as e:
                        log.warning(f"Unable to parse pixel data for {filename}: {e})")
                        gear_fail = True
                        fail_reason.append("Pixel data unparsable")
                else:
                    log.info(
                        f"No pixel data found for {filename}, pixel data check skipped."
                    )

            fix_evts = apply_fixers(dcm)
            # Handle post-decoding events from fixers (patient sex, incorrect
            # units, etc.)
            for fix in fix_evts:
                events[fix.field].add(repr(fix))

            # Before updating events from decoding, first get the list of events
            # before they go through fw-file's process_tracker(), which checks
            # whether a tag can be removed. If an element has events before
            # update_modified_dicom_info (which calls update_orig_attrs(), which calls
            # process_tracker()) but does not have events after, the original
            # tag value was restored because the tag is required.
            dcm.read_context.trim()
            expected_changed_elements = []
            for element in dcm.read_context.data_elements:
                if element.events:
                    expected_changed_elements.append(element.id_)

            update_modified_dicom_info(dcm, fix_evts)
            # Update events from decoding
            changed_elements = []
            for element in dcm.read_context.data_elements:
                if element.events:
                    changed_elements.append(element.id_)
                    tagname = str(element.tag).replace(",", "")
                    kw = keyword_for_tag(element.tag)
                    if kw:
                        tagname = kw
                    events[tagname].update([str(ev) for ev in element.events])
            reverted_elements = list(
                filter(lambda x: x not in changed_elements, expected_changed_elements)
            )
            if reverted_elements:
                qc_fail = True
                qc_fail_reason.append(
                    "One or more required tag values are invalid and could not be removed"
                )

    if gear_args.unique:
        if to_del:
            log.info(f"Removing {len(to_del)} duplicates")
            # Remove from the end to avoid shifting indexes on deletion
            for d in reversed(sorted(to_del)):
                del dcms[d]
        else:
            log.info("No duplicate frames found.")
    unique_warnings = handle_warnings(w)
    for msg, count in unique_warnings.items():
        log.warning(f"{msg} x {count} across archive")
    uid_modifications = add_missing_uid(dcms)

    # Create new UIDs if requested
    if gear_args.new_uids_needed:
        keys = ["sub.label", "ses.label", "acq.label"]
        new_uids = generate_and_set_new_uid(
            dcms, "SeriesInstanceUID", [uid_seeds[key] for key in keys]
        )
        uid_modifications.update(new_uids)
        keys = ["sub.label", "ses.label"]
        new_uids = generate_and_set_new_uid(
            dcms, "StudyInstanceUID", [uid_seeds[key] for key in keys]
        )
        uid_modifications.update(new_uids)

    # Add uid modifications to output events
    for uid, evts in uid_modifications.items():
        events[uid].update(evts)

    out_events = trim_events(events)
    out_name = get_output_filename(gear_args.dicom_path, dcms, gear_args.zip_single)

    fix_events = len(out_events) > 0
    removed_duplicates = gear_args.unique and len(to_del) > 0
    changed_file_name = out_name != gear_args.dicom_path.name

    if updated_transfer_syntax:
        out_events.append(
            {
                "tag": "TransferSyntaxUID",
                "event": f"Updated to {updated_transfer_syntax}",
            }
        )
    if updated_color:
        out_events.append(
            {"tag": "PhotometricInterpretation", "event": f"Updated to {updated_color}"}
        )
    if eof_fix:
        out_events.append(
            {
                "tag": "Sequence Delimiter",
                "event": "Missing delimiter (FFFE, E0DD) added.",
            }
        )
    if gear_fail:
        for reason in fail_reason:
            out_events.append({"tag": "Gear Fail", "event": reason})
    if qc_fail:
        for reason in qc_fail_reason:
            out_events.append({"tag": "QC Fail", "event": reason})
    write_criteria = [
        fix_events,
        bool(uid_modifications),
        updated_transfer_syntax,
        updated_color,
        removed_duplicates,
        changed_file_name,
        eof_fix,
    ]

    if any(write_criteria):
        msg = "Writing output because:"
        if fix_events:
            msg += "\n\tFixes applied"
        if uid_modifications:
            msg += "\n\tAdded UID(s)"
        if updated_transfer_syntax:
            msg += "\n\tUpdated transfer syntax"
        if updated_color:
            msg += "\n\tUpdated color space"
        if removed_duplicates:
            msg += "\n\tRemoved duplicate frames"
        if changed_file_name:
            msg += "\n\tChanged file name"
        if eof_fix:
            msg += "\n\tMissing delimiter fix applied"
        log.info(msg)
        try:
            # Remove zip suffix
            if out_name.endswith(".zip"):
                dcms.to_zip(
                    gear_args.output_dir / out_name,
                    instance_name_fn=get_instance_filename
                    if gear_args.rename_zip_members
                    else identity_instance_name_fn,
                )
            else:
                dcms[0].save(gear_args.output_dir / out_name)

            log.info(f"Wrote output to {gear_args.output_dir / out_name}")
        except Exception as exc:
            trace = traceback.format_exc()
            msg = f"Got exception saving dicom(s): {str(exc)}\n{trace}"
            # Ensure no output is uploaded
            (gear_args.output_dir / out_name).unlink(missing_ok=True)
            log.error(msg)
            return (None, None)

    return out_name, out_events


def get_output_filename(in_file, dcms, zip_single):
    """Write output file.

    Base on input and zip_single, will do one of the following:
        - always zip single dicoms (yes)
        - never zip single dicoms (no)
        - choose to zip single dicoms or not based on input (zip/dcm) (match)

    Args:
        in_file (Path): Path to input file.
        dcms (DICOMCollection): Input Dicom collection.
        zip_single (str): 'no', 'yes' or 'match', see description above.
    """
    # Remove zip suffix
    dest = in_file.name.replace(".zip", "")
    if zip_single == "yes":
        # Always zip
        dest += ".zip"
        return dest
    if zip_single == "no":
        if len(dcms) > 1:
            # Still zip if collection has more than 1 file
            dest += ".zip"
            return dest
        # Otherwise no zip
        return dest
    if len(dcms) > 1:
        # Still zip if collection has more than 1 file
        dest += ".zip"
        return dest
    # Match
    return in_file.name


def handle_warnings(
    warning_list: t.List[warnings.WarningMessage],
) -> t.Dict[t.Union[Warning, str], int]:
    """Find unique warnings and their counts from a list of warnings.

    Returns:
        Dictionary of warnings/str as key and int counts as value
    """
    warnings_dict: t.Dict[t.Union[Warning, str], int] = {}
    for warning in warning_list:
        msg = str(warning.message)
        if msg in warnings_dict:
            warnings_dict[msg] += 1
        else:
            warnings_dict[msg] = 1
    return warnings_dict


def get_uniqueness(dcm: DICOM) -> t.Tuple[str, str]:
    """Get uniqueness of a dicom by InstanceNumber and hash of file.

    Args:
        dcm (DICOM): _description_

    Returns:
        t.Tuple[str, int]: _description_
    """
    path = dcm.filepath
    digest = ""
    with open(path, "rb") as fp:
        md5Hash = hashlib.md5(fp.read())
        digest = md5Hash.hexdigest()
    return digest, dcm.get("SOPInstanceUID", "")


def trim_events(events: t.Dict[str, t.Set[str]]) -> t.List[dict]:
    """Convert and trim events into a list of dictionaries.

    Args:
        events (dict): Dictionary of events with tags as keys.

    Returns:
        list: List of dictionaries in the format {"tag": ..., "event": ...}.
    """
    trimmed_events = []
    for tag, evts in events.items():
        sorted_evts = sorted(list(evts))
        num_evts = len(sorted_evts)
        if num_evts > MAX_EVENT_LENGTH:
            # Trimming events to display a summary
            top_n = int(MAX_EVENT_LENGTH / 2)
            evts = [
                *sorted_evts[:top_n],
                f"...{num_evts - MAX_EVENT_LENGTH} more items...",
                *sorted_evts[(num_evts - top_n) :],
            ]
        # Create a list of dictionaries with "tag" and "event" keys
        for event in evts:
            trimmed_events.append({"tag": tag, "event": event})
    return trimmed_events
