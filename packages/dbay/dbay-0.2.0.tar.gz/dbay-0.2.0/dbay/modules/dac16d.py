from dbay.http import Http
from dbay.addons.vsource import VsourceChange, SharedVsourceChange
from dbay.state import IModule, Core
from typing import Literal, Union, List, Optional
from dbay.addons.vsource import IVsourceAddon
from dbay.direct import DeviceConnection


class dac16D_spec(IModule):
    module_type: Literal["dac16D"] = "dac16D"
    core: Core
    vsource: Optional[IVsourceAddon] = None  # optional in direct mode
    vsb: Optional[dict] = None
    vr: Optional[dict] = None


class dac16D:
    CORE_TYPE = "dac16D"
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
        self.data = dac16D_spec(**data)

    def __del__(self):  # pragma: no cover
        if self.mode != "gui" or self.retain_changes:
            return
        if not self.data.vsource or not self.http:
            return
        try:
            for idx in range(min(16, len(self.data.vsource.channels))):
                ch = self.data.vsource.channels[idx]
                change = VsourceChange(
                    module_index=self.data.core.slot,
                    index=idx,
                    bias_voltage=ch.bias_voltage,
                    activated=ch.activated,
                    heading_text=ch.heading_text,
                    measuring=False,
                )
                self.http.put("dac16D/vsource/", data=change.model_dump())
        except Exception:
            pass

    def set_voltage(self, index: int, voltage: float, activated: Union[bool, None] = None):
        if not (0 <= index <= 31):  # full hardware range in direct mode
            raise ValueError("channel index must be 0..31")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            if index >= len(self.data.vsource.channels):  # type: ignore
                raise ValueError("channel index exceeds GUI state channels")
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
            self.http.put("dac16D/vsource/", data=change.model_dump())
        else:
            assert self.connection is not None
            self.connection.send(f"DAC16D VS {self.data.core.slot} {index} {voltage}")

    def voltage_set(self, index: int, voltage: float, activated: Union[bool, None] = None):
        return self.set_voltage(index, voltage, activated=activated)

    def set_voltage_diff(self, index: int, voltage: float):
        if not (-3 <= index <= 15):  # as per reference implementation
            raise ValueError("differential channel index must be -3..15")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            raise NotImplementedError("Differential voltage not implemented in GUI mode")
        assert self.connection is not None
        self.connection.send(f"DAC16D VSD {self.data.core.slot} {index} {voltage}")

    def set_voltage_shared(self, voltage: float, activated: bool = True, channels: Union[List[bool], None] = None):
        if channels is None:
            channels = [True] * 16
        if len(channels) != 16:
            raise ValueError("channels list must have length 16")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            change = VsourceChange(
                module_index=self.data.core.slot,
                index=0,
                bias_voltage=voltage,
                activated=activated,
                heading_text=self.data.vsource.channels[0].heading_text,  # type: ignore
                measuring=True,
            )
            shared_change = SharedVsourceChange(change=change, link_enabled=channels)
            assert self.http is not None
            self.http.put("dac16D/vsource_shared/", data=shared_change.model_dump())
        else:
            # Iterate each channel for now (could optimize later if protocol adds batch)
            assert self.connection is not None
            for idx, enabled in enumerate(channels):
                if enabled:
                    self.connection.send(f"DAC16D VS {self.data.core.slot} {idx} {voltage}")

    def set_bias(self, voltage: float):
        if not (0 <= voltage <= 8):
            raise ValueError("bias voltage must be 0..8 V")
        if self.mode == "gui":
            change = VsourceChange(
                module_index=self.data.core.slot,
                index=0,
                bias_voltage=voltage,
                activated=True,
                heading_text="VSB",
                measuring=True,
            )
            assert self.http is not None
            self.http.put("dac16D/vsb/", data=change.model_dump())
        else:
            assert self.connection is not None
            self.connection.send(f"DAC16D VSB {self.data.core.slot} {voltage}")

    def read(self):
        if self.mode == "gui":
            raise NotImplementedError("read() not implemented for GUI mode")
        assert self.connection is not None
        return self.connection.send(f"DAC16D VR {self.data.core.slot}")

    def __str__(self):
        slot = self.data.core.slot
        if self.mode == "gui" and self.data.vsource:
            active_channels = sum(1 for ch in self.data.vsource.channels if ch.activated)
            return f"dac16D (Slot {slot}): {active_channels}/16 channels active"
        return f"dac16D (Slot {slot}) [direct]"
