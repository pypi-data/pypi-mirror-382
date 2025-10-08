from fileformats.vendor.siemens.medimage import (
    SyngoMi_ListMode_Vr20b,
    SyngoMi_CountRate_Vr20b,
    SyngoMi_Sinogram_Vr20b,
    SyngoMi_DynamicSinogramSeries_Vr20b,
    SyngoMi_Normalisation_Vr20b,
    SyngoMi_Parameterisation_Vr20b,
    SyngoMi_CtSpl_Vr20b,
)


def test_siemens_pet_listmode_generator():
    img = SyngoMi_ListMode_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_countrate_generator():
    img = SyngoMi_CountRate_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_sinogram_generator():
    img = SyngoMi_Sinogram_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_dynamics_sino_generator():
    img = SyngoMi_DynamicSinogramSeries_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_normalisation_generator():
    img = SyngoMi_Normalisation_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_petct_spl_generator():
    img = SyngoMi_CtSpl_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_parameterisation_generator():
    img = SyngoMi_Parameterisation_Vr20b.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"
