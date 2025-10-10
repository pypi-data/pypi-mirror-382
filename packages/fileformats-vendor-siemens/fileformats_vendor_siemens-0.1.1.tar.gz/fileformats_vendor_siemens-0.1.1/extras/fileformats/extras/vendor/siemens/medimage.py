import typing as ty
from pathlib import Path
import pydicom
import sys
from collections import Counter
from fileformats.core import SampleFileGenerator
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_listmode import (
    get_data as get_pet_listmode_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_countrate import (
    get_data as get_pet_countrate_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_em_sino import (
    get_data as get_pet_sinogram_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_calibration import (
    get_data as get_pet_calibration_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_dynamics_sino import (
    get_data as get_pet_dynamics_sino_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_replay_param import (
    get_data as get_pet_replay_param_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.petct_spl import (
    get_data as get_petct_spl_data,
)
from fileformats.core import extra_implementation, FileSet
from fileformats.medimage.dicom import DicomImage
from fileformats.vendor.siemens.medimage import (
    SyngoMi_RawData_Vr20b,
    SyngoMi_LargeRawData_Vr20b,
    SyngoMi_ListMode_Vr20b,
    SyngoMi_Sinogram_Vr20b,
    SyngoMi_DynamicSinogramSeries_Vr20b,
    SyngoMi_CountRate_Vr20b,
    SyngoMi_Normalisation_Vr20b,
    SyngoMi_Parameterisation_Vr20b,
    SyngoMi_CtSpl_Vr20b,
)
from fileformats.core.io import BinaryIOWindow

if sys.version_info >= (3, 9):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

TagListType: TypeAlias = ty.Union[
    ty.List[int],
    ty.List[str],
    ty.List[ty.Tuple[int, int]],
    ty.List[pydicom.tag.BaseTag],
]


@extra_implementation(FileSet.read_metadata)
def siemens_pet_raw_data_read_metadata(
    pet_raw_data: SyngoMi_LargeRawData_Vr20b,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            pet_raw_data.dicom_header_offset,
            pet_raw_data.dcm_hdr_size_int_offset,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return DicomImage.pydicom_to_dict(dcm)


@extra_implementation(SyngoMi_RawData_Vr20b.load_pydicom)
def siemens_pet_raw_data_load_pydicom(
    pet_raw_data: SyngoMi_LargeRawData_Vr20b,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> pydicom.Dataset:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            pet_raw_data.dicom_header_offset,
            pet_raw_data.dcm_hdr_size_int_offset,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return dcm


@extra_implementation(FileSet.read_metadata)
def siemens_petct_raw_data_read_metadata(
    pet_raw_data: SyngoMi_CtSpl_Vr20b,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            *pet_raw_data.dicom_header_limits,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return DicomImage.pydicom_to_dict(dcm)


@extra_implementation(SyngoMi_RawData_Vr20b.load_pydicom)
def siemens_petct_raw_data_load_pydicom(
    pet_raw_data: SyngoMi_CtSpl_Vr20b,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> pydicom.Dataset:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            *pet_raw_data.dicom_header_limits,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return dcm


@extra_implementation(FileSet.read_metadata)
def siemens_pet_dynamic_sinogram_series_read_metadata(
    pet_raw_data: SyngoMi_DynamicSinogramSeries_Vr20b,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:

    # Collated DICOM headers across series
    collated: ty.Dict[str, ty.Any] = {}
    key_repeats: ty.Counter[str] = Counter()
    varying_keys = set()
    # We use the "contents" property implementation in TypeSet instead of the overload
    # in DicomCollection because we don't want the metadata to be read ahead of the
    # the `select_metadata` call below

    for ptd in pet_raw_data.contents:
        for key, val in ptd.metadata.items():
            try:
                prev_val = collated[key]
            except KeyError:
                collated[key] = (
                    val  # Insert initial value (should only happen on first iter)
                )
                key_repeats.update([key])
            else:
                if key in varying_keys:
                    collated[key].append(val)
                # Check whether the value is the same as the values in the previous
                # images in the series
                elif val != prev_val:
                    collated[key] = [prev_val] * key_repeats[key] + [val]
                    varying_keys.add(key)
                else:
                    key_repeats.update([key])
    return collated


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_listmode_generate_sample_data(
    pet_raw_data: SyngoMi_ListMode_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_listmode_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_countrate_generate_sample_data(
    pet_raw_data: SyngoMi_CountRate_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_countrate_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_sinogram_generate_sample_data(
    pet_raw_data: SyngoMi_Sinogram_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_sinogram_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_dynamics_sino_generate_sample_data(
    pet_raw_data: SyngoMi_DynamicSinogramSeries_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_dynamics_sino_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_normalisation_generate_sample_data(
    pet_raw_data: SyngoMi_Normalisation_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_calibration_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_petct_spl_generate_sample_data(
    pet_raw_data: SyngoMi_CtSpl_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_petct_spl_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_parameterisation_generate_sample_data(
    pet_raw_data: SyngoMi_Parameterisation_Vr20b,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_replay_param_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]
