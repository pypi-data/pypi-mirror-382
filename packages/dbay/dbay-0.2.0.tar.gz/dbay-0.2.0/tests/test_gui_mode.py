from dbay import DBayClient, dac4D

class PutRecorder:
    def __init__(self):
        self.calls = []
    def __call__(self, endpoint: str, data: dict):  # mimic Http.put signature
        self.calls.append((endpoint, data))
        return {"status": "ok"}


def minimal_dac4d_state(slot: int = 0):
    return {
        "core": {"slot": slot, "type": "dac4D", "name": "dac4D"},
        "vsource": {"channels": [
            {"index": i, "bias_voltage": 0.0, "activated": False, "heading_text": f"CH{i}", "measuring": False}
            for i in range(4)
        ]},
    }


def test_gui_set_voltage(monkeypatch):
    # Build client with fake http that returns our injected full-state
    client = DBayClient(mode="gui", server_address="127.0.0.1", load_state=False)
    # Directly replace first module with a constructed dac4D using gui path
    state = minimal_dac4d_state(0)
    rec = PutRecorder()
    # Monkeypatch the client's http put
    monkeypatch.setattr(client._http, "put", rec)  # type: ignore[attr-defined]
    mod = dac4D(state, http=client._http, mode="gui")
    client._modules[0] = mod  # inject
    mod.set_voltage(0, 1.25, activated=True)
    assert rec.calls, "Expected at least one PUT call"
    endpoint, payload = rec.calls[-1]
    assert endpoint == "dac4D/vsource/"
    assert payload["bias_voltage"] == 1.25
