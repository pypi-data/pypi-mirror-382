"""The fw_gear_dicom_qc package."""

from importlib.metadata import version

pkg_name = __package__
__version__ = "0.0.1"
try:
    __version__ = version(pkg_name.replace("_", "-"))
except:  # noqa: E722
    pass
