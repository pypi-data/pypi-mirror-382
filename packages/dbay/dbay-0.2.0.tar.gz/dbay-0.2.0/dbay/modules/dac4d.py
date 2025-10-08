from dbay.http import Http
from dbay.addons.vsource import VsourceChange
from dbay.state import IModule, Core
from typing import Literal, Union, Optional
from dbay.addons.vsource import IVsourceAddon
from dbay.direct import DeviceConnection


class dac4D_spec(IModule):
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: Optional[IVsourceAddon] = None  # optional in direct mode


class dac4D:
    CORE_TYPE = "dac4D"
    """Dual-mode dac4D module wrapper.

    GUI mode expects full `data` including vsource. Direct mode can pass a
    minimal core structure: {"core": {"slot": int, "type": "dac4D", "name": str}}.
    """

    def __init__(
        self,
        data,
        *,
        http: Optional[Http] = None,
        connection: Optional[DeviceConnection] = None,
        mode: str = "gui",
        retain_changes: bool = True,
    ):
        self.mode = mode.lower()
        if self.mode not in {"gui", "direct"}:
            raise ValueError("mode must be 'gui' or 'direct'")
        self.http = http
        self.connection = connection
        self.retain_changes = retain_changes
        # In direct mode vsource may be absent; allow None
        self.data = dac4D_spec(**data)

    # ------------------------------------------------------------------
    # GUI-only cleanup (revert config). Direct mode does nothing.
    # ------------------------------------------------------------------
    def __del__(self):  # pragma: no cover - defensive cleanup
        if self.mode != "gui" or self.retain_changes:
            return
        if not self.data.vsource or not self.http:
            return
        try:
            for idx in range(min(4, len(self.data.vsource.channels))):
                ch = self.data.vsource.channels[idx]
                change = VsourceChange(
                    module_index=self.data.core.slot,
                    index=idx,
                    bias_voltage=ch.bias_voltage,
                    activated=ch.activated,
                    heading_text=ch.heading_text,
                    measuring=False,
                )
                self.http.put("dac4D/vsource/", data=change.model_dump())
        except Exception:
            # Avoid destructor exceptions
            pass

    # ------------------------------------------------------------------
    # Unified API
    # ------------------------------------------------------------------
    def set_voltage(self, index: int, voltage: float, activated: Union[bool, None] = None):
        if not (0 <= index <= 7):  # allow up to 7 for forward compatibility
            raise ValueError("channel index must be 0..7")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            if activated is None:
                activated = self.data.vsource.channels[index].activated  # type: ignore
            change = VsourceChange(
                module_index=self.data.core.slot,
                index=index,
                bias_voltage=voltage,
                activated=activated,
                heading_text=self.data.vsource.channels[index].heading_text,  # type: ignore
                measuring=True,
            )
            assert self.http is not None
            print("sending: ", change)
            self.http.put("dac4D/vsource/", data=change.model_dump())
        else:  # direct
            assert self.connection is not None
            self.connection.send(f"DAC4D VS {self.data.core.slot} {index} {voltage}")

    # Backwards compatibility alias (legacy name)
    def voltage_set(self, index: int, voltage: float, activated: Union[bool, None] = None):
        return self.set_voltage(index, voltage, activated=activated)

    def set_voltage_diff(self, index: int, voltage: float):
        if not (0 <= index <= 3):
            raise ValueError("differential channel index must be 0..3")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            # Placeholder: no HTTP endpoint currently defined
            raise NotImplementedError("Differential voltage not implemented in GUI mode")
        assert self.connection is not None
        self.connection.send(f"DAC4D VSD {self.data.core.slot} {index} {voltage}")

    def __str__(self):
        slot = self.data.core.slot
        if self.mode == "gui" and self.data.vsource:
            active_channels = sum(1 for ch in self.data.vsource.channels if ch.activated)
            return f"dac4D (Slot {slot}): {active_channels}/4 channels active"
        return f"dac4D (Slot {slot}) [direct]"

