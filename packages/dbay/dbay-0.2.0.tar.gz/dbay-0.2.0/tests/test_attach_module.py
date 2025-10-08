from dbay import DBayClient, dac4D, dac16D


def test_attach_module_returns_correct_type():
    client = DBayClient(mode="direct")
    mod4 = client.attach_module(0, dac4D)
    assert isinstance(mod4, dac4D)
    mod16 = client.attach_module(1, dac16D)
    assert isinstance(mod16, dac16D)


def test_attach_module_requires_direct_mode():
    client = DBayClient(mode="gui", server_address="127.0.0.1", load_state=False)
    try:
        client.attach_module(0, dac4D)  # type: ignore[arg-type]
    except ValueError as e:
        assert "only valid in direct mode" in str(e)
    else:
        raise AssertionError("Expected ValueError for GUI mode attach_module")
