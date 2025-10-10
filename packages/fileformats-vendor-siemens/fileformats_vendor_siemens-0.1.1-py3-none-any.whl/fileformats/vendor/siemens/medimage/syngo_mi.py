import io
import typing as ty
from collections import defaultdict
import sys
from pathlib import Path
from fileformats.generic import TypedSet
from fileformats.core import mtime_cached_property, validated_property, extra
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core.mixin import WithMagicNumber
from fileformats.medimage.dicom import get_dicom_tag
from fileformats.core.io import BinaryIOWindow
from fileformats.medimage.raw.pet.base import (
    PetRawData,
    PetPhysio,
    PetListMode,
    PetSinogram,
    PetCountRate,
    PetNormalisation,
    PetParameterisation,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if ty.TYPE_CHECKING:
    import pydicom


class SyngoMi_RawData_Vr20b(PetRawData):
    """PET raw data format as produced by Siemens Biograph 128 Vision. It is used to
    store a range of raw PET data such as list-mode, calibration and sinogram files.

    Consists of a block of raw data, followed by a DICOM header, an int4 containing
    the size of the DICOM header, and then the number b'LARGE_PET_LM_RAWDATA'.
    """

    ext = ".ptd"
    expected_image_type: str = ""  # For sub-classes to specify the expected image tag
    IMAGE_TYPE_TAG = (0x0008, 0x0008)

    def read_tag(self, tag: ty.Tuple[int, int]) -> ty.Union[str, bytes, None]:
        with self.open() as f:
            window = BinaryIOWindow(
                f,  # type: ignore[arg-type]
                *self.dicom_header_limits,
            )
            value = get_dicom_tag(window, tag)
        return value

    @validated_property
    def image_type(self) -> str:
        image_type_seq: ty.List[str] = self._image_type_seq
        if self.expected_image_type:
            if (
                not isinstance(image_type_seq, list)
                or len(image_type_seq) < 3
                or image_type_seq[:2] != ["ORIGINAL", "PRIMARY"]
            ):
                raise FormatMismatchError(
                    f"Image type of {self} ({image_type_seq!r}) does not match expected "
                    f"form ['ORIGINAL', 'PRIMARY', *]"
                )
            image_type = image_type_seq[2]
            if self.expected_image_type != image_type:
                raise FormatMismatchError(
                    f"Image type of {self} ({image_type!r}) does not match expected "
                    f"({self.expected_image_type!r})"
                )
            return image_type
        assert isinstance(self._image_type_seq[-1], str)
        return self._image_type_seq[-1]

    @mtime_cached_property
    def _image_type_seq(self) -> ty.List[str]:
        value = self.read_tag(self.IMAGE_TYPE_TAG)
        assert isinstance(value, str)
        return value.split("\\")

    @mtime_cached_property
    def dicom_header_limits(self) -> ty.Tuple[int, int]:
        """Try either method to determine the dicom header limits. If both fail, raise an error"""
        try:
            return SyngoMi_LargeRawData_Vr20b(self.fspaths).dicom_header_limits
        except FormatMismatchError:
            try:
                return SyngoMi_CtSpl_Vr20b(self.fspaths).dicom_header_limits
            except FormatMismatchError:
                raise FormatMismatchError(
                    f"File {self.fspath!r} does not contain a valid DICOM header"
                ) from None

    @extra
    def load_pydicom(self, **kwargs: ty.Any) -> "pydicom.Dataset":
        """Reads any metadata associated with the fileset and returns it as a dict

        Parameters
        ----------
        **kwargs : Any
            any format-specific keyword arguments to pass to the metadata reader

        Returns
        -------
        pydicom.Dataset
            the DICOM dataset containing the metadata loaded by PyDICOM
        """
        raise NotImplementedError


class SyngoMi_LargeRawData_Vr20b(WithMagicNumber, SyngoMi_RawData_Vr20b):
    """PET raw data format as produced by Siemens Biograph 128 Vision. It is used to
    store a range of raw PET data such as list-mode, calibration and sinogram files.

    Consists of a block of raw data, followed by a DICOM header, an int4 containing
    the size of the DICOM header, and then the number b'LARGE_PET_LM_RAWDATA'.
    """

    ext = ".ptd"
    magic_number = b"LARGE_PET_LM_RAWDATA"
    magic_number_offset = -len(magic_number)  # magic number is at end of file

    # Size in bytes of the integer that defines the size of the dicom header
    sizeof_dcm_hdr_size_int: int = 4
    # Offset from the end of the file where the magic number and header size integer
    dcm_hdr_size_int_offset: int = magic_number_offset - sizeof_dcm_hdr_size_int

    @mtime_cached_property
    def dicom_header_size(self) -> int:
        with self.open() as f:
            f.seek(self.dcm_hdr_size_int_offset, io.SEEK_END)
            dcm_hdr_size_bytes: bytes = f.read(self.sizeof_dcm_hdr_size_int)
            return int.from_bytes(dcm_hdr_size_bytes, "little")

    @validated_property
    def dicom_header_offset(self) -> int:
        dcm_hdr_size: int = self.dicom_header_size
        return -dcm_hdr_size + self.dcm_hdr_size_int_offset

    @property
    def dicom_header_limits(self) -> ty.Tuple[int, int]:  # type: ignore[override]
        """Returns the start and end of the DICOM header in the file"""
        return (
            self.dicom_header_offset,
            self.dicom_header_offset + self.dicom_header_size,
        )


class SyngoMi_ListMode_Vr20b(SyngoMi_LargeRawData_Vr20b, PetListMode):
    expected_image_type = "PET_LISTMODE"


class SyngoMi_Sinogram_Vr20b(SyngoMi_LargeRawData_Vr20b, PetSinogram):
    "histogrammed projection data in a reconstruction-friendly format"

    expected_image_type = "PET_EM_SINOGRAM"


class SyngoMi_DynamicSinogram_Vr20b(SyngoMi_LargeRawData_Vr20b, PetSinogram):
    "histogrammed projection data in a reconstruction-friendly format"

    expected_image_type = "PET_SINO_DYNAMIC"


class SyngoMi_CountRate_Vr20b(SyngoMi_LargeRawData_Vr20b, PetCountRate):
    "number of prompt/random/single events per unit time"

    expected_image_type = "PET_COUNTRATE"


class SyngoMi_Parameterisation_Vr20b(SyngoMi_LargeRawData_Vr20b, PetParameterisation):
    "number of prompt/random/single events per unit time"

    expected_image_type = "PET_REPLAY_PARAM"


class SyngoMi_Normalisation_Vr20b(SyngoMi_LargeRawData_Vr20b, PetNormalisation):
    "normalisation scan or the current cross calibration factor"

    expected_image_type = "PET_CALIBRATION"


class SyngoMi_Physio_Vr20b(SyngoMi_LargeRawData_Vr20b, PetPhysio):
    "normalisation scan or the current cross calibration factor"

    expected_image_type = "PET_PHYSIO"


class SyngoMi_DynamicSinogramSeries_Vr20b(TypedSet):
    "Series of sinogram images"

    content_types = (SyngoMi_DynamicSinogram_Vr20b,)

    @classmethod
    def from_paths(
        cls,
        fspaths: ty.Iterable[Path],
        common_ok: bool = False,
        **kwargs: ty.Any,
    ) -> ty.Tuple[ty.Set[Self], ty.Set[Path]]:
        """Separates a list of DICOM files into separate series from the file-system
        paths

        Parameters
        ----------
        fspaths : ty.Iterable[Path]
            the fspaths pointing to the DICOM files
        common_ok : bool, optional
            included to match the signature of the overridden method, but ignored as each
            dicom should belong to only one series.
        specific_tags : ty.Optional[TagListType], optional
            the DICOM tags to read from the files. If None, the default tags will be
            read
        **kwargs : ty.Any
            additional keyword arguments to passed through to the DicomImage constructor

        Returns
        -------
        tuple[set[DicomSeries], set[Path]]
            the found dicom series objects and any unrecognised file paths
        """
        (
            sinograms,
            remaining,
        ) = SyngoMi_DynamicSinogram_Vr20b.from_paths(
            fspaths, common_ok=common_ok, **kwargs
        )
        series_dict = defaultdict(list)
        for sinogram in sinograms:
            series_dict[tuple(sinogram.read_tag(t) for t in cls.ID_TAGS)].append(
                sinogram
            )
        return set([cls(d.fspath for d in s) for s in series_dict.values()]), remaining

    @mtime_cached_property
    def contents(self) -> ty.List[SyngoMi_Sinogram_Vr20b]:
        return sorted(TypedSet.contents.__get__(self), key=pet_rd_sort_key)

    ID_TAGS = (
        (0x0020, 0x000D),
        (0x0020, 0x0011),
    )  # "StudyInstanceUID", "SeriesNumber"


def pet_rd_sort_key(ptd: SyngoMi_RawData_Vr20b) -> str:
    """Sorts DICOM objects by SOPInstanceUID"""
    acquisition_time = ptd.read_tag((0x0008, 0x0032))
    assert isinstance(acquisition_time, str)
    return acquisition_time


class SyngoMi_CtSpl_Vr20b(WithMagicNumber, SyngoMi_RawData_Vr20b):
    """PET CT raw data format as produced by Siemens Biograph 128 Vision. It is used to
    store a range PETCT_SPL type files

    Consists of a block of dummy, followed by a DICOM header.
    """

    ext = ".ptd"
    magic_number = b"dummy data"
    expected_image_type: str = "PETCT_SPL"

    magic_dicom_end = b"END!"

    @validated_property
    def dicom_header_limits(self) -> ty.Tuple[int, int]:  # type: ignore[override]
        """Returns the start and end indices of the DICOM data embedded within the
        file. The DICOM data starts immediately after the magic number and is delimited
        by a magic sequence 'END!'"""
        start = len(self.magic_number)
        end = None
        with self.open() as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                offset = chunk.find(self.magic_dicom_end)
                if offset != -1:
                    end = f.tell() - len(chunk) + offset
                    return (start, end)
        raise FormatMismatchError(
            f"Magic sequence {self.magic_dicom_end!r} delimiting DICOM data "
            f"not found in file PETCT SPL({str(self)!r})"
        )
