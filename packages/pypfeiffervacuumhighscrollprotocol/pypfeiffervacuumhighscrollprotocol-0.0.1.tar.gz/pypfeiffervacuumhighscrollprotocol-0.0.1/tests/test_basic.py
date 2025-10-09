import pypfeiffervacuumhighscrollprotocol as feiffer

def test_version():
    assert feiffer.__version__ == "0.0.1"
    assert isinstance(feiffer.__version__, str)
    assert len(feiffer.__version__) > 0


def test_import_function():
    assert hasattr(feiffer, "read_gauge_type")
