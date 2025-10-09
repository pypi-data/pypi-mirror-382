import pytest

from qupled.hf import DatabaseInfo
from qupled.native import Qstls, QstlsIet, QstlsIetInput


@pytest.fixture
def database_info():
    dbInfo = DatabaseInfo()
    dbInfo.run_id = 1
    return dbInfo.to_native()


def test_qstls_properties():
    scheme = QstlsIet(QstlsIetInput())
    assert hasattr(scheme, "idr")
    assert hasattr(scheme, "sdr")
    assert hasattr(scheme, "lfc")
    assert hasattr(scheme, "ssf")
    with pytest.raises(RuntimeError) as excinfo:
        hasattr(scheme, "uint")
    assert excinfo.value.args[0] == "No data to compute the internal energy"
    assert hasattr(scheme, "wvg")
    assert hasattr(scheme, "error")
    assert hasattr(scheme, "bf")


def test_qstls_iet_compute(database_info):
    iet_schemes = {"QSTLS-HNC", "QSTLS-IOI", "QSTLS-LCT"}
    for scheme_name in iet_schemes:
        inputs = QstlsIetInput()
        inputs.coupling = 10.0
        inputs.degeneracy = 1.0
        inputs.theory = scheme_name
        inputs.chemical_potential = [-10, 10]
        inputs.cutoff = 5.0
        inputs.matsubara = 16
        inputs.resolution = 0.1
        inputs.integral_error = 1.0e-5
        inputs.threads = 16
        inputs.error = 1.0e-5
        inputs.mixing = 0.5
        inputs.iterations = 1000
        inputs.database_info = database_info
        scheme = QstlsIet(inputs)
        scheme.compute()
        nx = scheme.wvg.size
        assert nx >= 3
        assert scheme.lfc.shape[0] == nx
        assert scheme.lfc.shape[1] == inputs.matsubara
        assert scheme.idr.shape[0] == nx
        assert scheme.idr.shape[1] == inputs.matsubara
        assert scheme.sdr.size == nx
        assert scheme.ssf.size == nx
        assert scheme.bf.size == nx
