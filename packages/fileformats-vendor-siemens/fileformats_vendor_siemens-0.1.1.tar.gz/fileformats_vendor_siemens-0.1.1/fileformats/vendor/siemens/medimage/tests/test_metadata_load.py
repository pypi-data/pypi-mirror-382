from fileformats.vendor.siemens.medimage import SyngoMi_Sinogram_Vr20b


def test_siemens_load_pydicom():

    sino = SyngoMi_Sinogram_Vr20b.sample()
    assert sino.metadata["PatientName"] == "FirstName^LastName"
