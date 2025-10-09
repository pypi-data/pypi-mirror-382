import pytest

from qupled.native import ESA, Rpa, Input


def test_esa_properties():
    scheme = ESA(Input())
    assert hasattr(scheme, "idr")
    assert hasattr(scheme, "sdr")
    assert hasattr(scheme, "lfc")
    assert hasattr(scheme, "ssf")
    with pytest.raises(RuntimeError) as excinfo:
        hasattr(scheme, "uint")
    assert excinfo.value.args[0] == "No data to compute the internal energy"
    assert hasattr(scheme, "wvg")


def test_esa_compute():
    inputs = Input()
    inputs.coupling = 1.0
    inputs.degeneracy = 1.0
    inputs.theory = "RPA"
    inputs.chemical_potential = [-10, 10]
    inputs.cutoff = 10.0
    inputs.matsubara = 128
    inputs.resolution = 0.1
    inputs.integral_error = 1.0e-5
    inputs.threads = 1
    scheme = ESA(inputs)
    scheme.compute()
    nx = scheme.wvg.size
    assert nx >= 3
    assert scheme.idr.shape[0] == nx
    assert scheme.idr.shape[1] == inputs.matsubara
    assert scheme.sdr.size == nx
    assert scheme.lfc.size == nx
    assert scheme.ssf.size == nx
