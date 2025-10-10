import pytest
from fileformats.core.exceptions import FileFormatsExtrasError
from fileformats.vendor.siemens.medimage import SyngoMi_Sinogram_Vr20b


def test_raw_pet_data_deidentify():
    raw_pet = SyngoMi_Sinogram_Vr20b.sample()
    with pytest.raises(FileFormatsExtrasError):
        raw_pet.deidentify()
