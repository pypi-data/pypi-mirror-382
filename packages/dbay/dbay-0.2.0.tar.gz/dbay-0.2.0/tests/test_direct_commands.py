from dbay import DBayClient, dac4D, dac16D

class SendRecorder:
    def __init__(self):
        self.commands = []
    def __call__(self, message: str):
        self.commands.append(message)
        return "+ok"


def test_dac4d_voltage_command(monkeypatch):
    client = DBayClient(mode="direct")
    recorder = SendRecorder()
    # Patch connection send
    monkeypatch.setattr(client._connection, "send", recorder)  # type: ignore[attr-defined]
    mod = client.attach_module(0, dac4D)
    mod.set_voltage(0, 5.0)
    assert recorder.commands[-1].startswith("DAC4D VS 0 0 5.0")


def test_dac16d_shared_and_bias(monkeypatch):
    client = DBayClient(mode="direct")
    recorder = SendRecorder()
    monkeypatch.setattr(client._connection, "send", recorder)  # type: ignore[attr-defined]
    mod = client.attach_module(1, dac16D)
    mod.set_voltage(3, -2.5)
    mod.set_bias(2.0)
    mod.set_voltage_shared(1.1, channels=[True]*16)
    # We expect at least 1 + 1 + 16 commands = 18 entries
    assert len(recorder.commands) >= 18
    assert any(cmd.startswith("DAC16D VSB 1 2.0") for cmd in recorder.commands)


def test_invalid_voltage_raises():
    client = DBayClient(mode="direct")
    mod = client.attach_module(0, dac4D)
    try:
        mod.set_voltage(0, 50)  # invalid
    except ValueError as e:
        assert "-10..10" in str(e)
    else:
        raise AssertionError("Expected ValueError for invalid voltage")
