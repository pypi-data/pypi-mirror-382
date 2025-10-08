# dbay-client/README.md

# DBay Client (Unified Dual-Mode)

DBay provides a unified Python client (`DBayClient`) for interacting with DBay hardware in two distinct ways:

1. **GUI (stateful) mode** – Talks to the DBay GUI backend over HTTP, pulling a full system state (modules, channels) and pushing configuration updates.
2. **Direct (stateless) mode** – Sends low-level ASCII commands directly to the mainframe over UDP or Serial without maintaining any shadow state.

Both modes share the same object model and method names where feasible. You choose the mode once at construction via a simple string: `mode="gui"` or `mode="direct"`.

## Installation

Install from PyPI (package name placeholder shown below; adjust if different):

```bash
pip install dbay
```

Or install from source (editable):

```bash
git clone <repository-url>
cd dbay/device-bay-client
pip install -e .
```

## Quick Start

### GUI Mode (Stateful)

```python
from dbay import DBayClient

client = DBayClient(mode="gui", server_address="192.168.0.50", port=8345)
client.list_modules()

dac16 = client.module(1, expected="dac16D")
dac16.set_voltage(0, 1.2, activated=True)
dac16.set_voltage_shared(0.5)  # sets all channels to 0.5 V
dac16.set_bias(2.0)
```

### Direct Mode (UDP)

```python
from dbay import DBayClient, dac4D, dac16D

client = DBayClient(mode="direct", direct_host="192.168.0.108", direct_port=8880)

# Direct mode requires explicit attachment (no discovery)
dac4 = client.attach_module(0, dac4D)
dac4.set_voltage(0, 5.0)
dac4.set_voltage_diff(1, -2.0)

dac16 = client.attach_module(1, dac16D)
dac16.set_voltage(10, -1.25)
dac16.set_bias(3.0)
print("Raw read: ", dac16.read())
```

### Direct Mode (Serial)

```python
from dbay import DBayClient, HIC4, ADC4D

client = DBayClient(
	mode="direct",
	direct_transport="serial",
	serial_port="/dev/ttyUSB0",
	baudrate=115200,
	timeout=1.0,
)
h = client.attach_module(2, HIC4)
h.set_voltage(0, 0.75)
```

### Raw Command (Direct Only)

```python
client.direct_send("DAC16D VS 1 5 2.5")
```

## Module Methods (Summary)

| Module  | Methods (Common)                                                  | GUI Support                  | Direct Support |
| ------- | ----------------------------------------------------------------- | ---------------------------- | -------------- |
| dac4D   | set_voltage, set_voltage_diff                                     | voltage only (diff TBD)      | yes            |
| dac16D  | set_voltage, set_voltage_diff, set_voltage_shared, set_bias, read | shared, bias (diff/read TBD) | yes            |
| FAFD    | set_voltage, read                                                 | pending                      | yes            |
| HIC4    | set_voltage                                                       | pending                      | yes            |
| ADC4D   | read_diff                                                         | pending                      | yes            |
| DAC4ETH | set_voltage, set_voltage_diff                                     | pending                      | yes            |
| Empty   | placeholder                                                       | n/a                          | n/a            |

GUI “pending” indicates the HTTP backend and data models are not yet implemented; calls will raise `NotImplementedError`.

## Migration from Legacy `DBay`

Old (HTTP-only):

```python
from dbay.client import DBay
client = DBay("192.168.0.50")
client.modules[0].voltage_set(0, 1.0)
```

New unified API:

```python
from dbay import DBayClient
client = DBayClient(mode="gui", server_address="192.168.0.50")
mod = client.module(0, expected="dac4D")
mod.set_voltage(0, 1.0)
```

Key changes:

- Class name changed to `DBayClient`.
- Methods standardized to `set_voltage` (legacy `voltage_set` still available as alias).
- Access modules via `client.module(slot)` instead of `client.modules[index]`.
- Direct mode now uses class-based `attach_module(slot, ModuleClass)` for better type checking.

## Design Notes

- GUI mode uses Pydantic models. By default (now the naive / persistent behavior) module changes are retained (`retain_changes=True`). Opt out with `retain_changes=False` if you want automatic revert for supported modules.
- Direct mode is intentionally stateless: it sends commands and returns raw responses (no caching). Activation flags are ignored in direct mode.
- Differential and sense features may be absent in GUI until backend endpoints are added.
- Class-based attachment uses each module's `CORE_TYPE` attribute to set hardware identity.
- New modules (FAFD, HIC4, ADC4D, DAC4ETH) raise `NotImplementedError` for GUI operations for now.

## State Retention & Optional Reversion (`retain_changes`)

Default behavior now: hardware settings you apply in GUI mode remain in effect after your script ends. This matches the intuitive expectation that "what I last set is what the GUI (and hardware) keeps". The flag `retain_changes` therefore defaults to `True`.

If you prefer a session-style workflow where temporary changes are rolled back automatically for supported modules (currently the DAC family), start the client with `retain_changes=False`:

```python
from dbay import DBayClient

client = DBayClient(
    mode="gui",
    server_address="192.168.0.50",
    retain_changes=False,   # auto-revert DAC channels on cleanup
)
```

Behavior matrix:

| Mode   | retain_changes | Cleanup action | Notes                                                |
| ------ | -------------- | -------------- | ---------------------------------------------------- |
| GUI    | True (default) | No revert      | Final commanded values persist in GUI                |
| GUI    | False          | Revert (DACs)  | Attempts to restore initial snapshot for DAC modules |
| Direct | (any)          | No revert      | Direct mode never auto-reverts; flag currently inert |

Details & caveats:

- Reversion relies on destructor timing; abrupt termination (e.g. `kill -9`) skips cleanup.
- Only modules that captured an initial state support revert (DAC family). Others have nothing to restore.
- A future enhancement may add an explicit `revert_all()` to avoid relying on GC.

Recommendation: leave the default (`True`) for user-facing or interactive tooling; use `False` in automated measurement scripts that must leave hardware in a known pre-run state.

## Limitations / Not Implemented Yet

- Differential voltage setting in GUI mode.
- Reading values (e.g., `read`, `read_diff`) in GUI mode.
- Batch / shared voltage command optimization in direct mode (currently sequential sends).
- Websocket streaming for sense channels (explicitly out of scope for now).

## Contributing

Contributions are welcome! Feel free to open issues or PRs for:

- Adding GUI endpoints/models for the new modules.
- Extending test coverage for direct command generation.
- Documentation improvements.

## License

MIT License. See `LICENSE`.
