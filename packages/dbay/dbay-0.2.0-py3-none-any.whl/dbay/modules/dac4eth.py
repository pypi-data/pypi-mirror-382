from __future__ import annotations

from typing import Optional
from dbay.http import Http
from dbay.direct import DeviceConnection

__all__ = ["DAC4ETH"]


class DAC4ETH:
    CORE_TYPE = "DAC4ETH"
    """Dual-mode DAC4ETH module.

    Direct commands:
      - set_voltage(channel, value) -> "DAC4ETH VS <slot> <channel> <value>"
      - set_voltage_diff(channel, value) -> "DAC4ETH VSD <slot> <channel> <value>"

    GUI mode not implemented.
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
        self.slot = data.get("core", {}).get("slot", 0)
        self.retain_changes = retain_changes

    def set_voltage(self, channel: int, value: float):
        if not (0 <= channel <= 31):
            raise ValueError("channel must be 0..31")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            raise NotImplementedError("DAC4ETH.set_voltage not implemented for GUI mode")
        assert self.connection is not None
        self.connection.send(f"DAC4ETH VS {self.slot} {channel} {value}")

    def set_voltage_diff(self, channel: int, value: float):
        if not (0 <= channel <= 15):
            raise ValueError("differential channel must be 0..15")
        if not (-10 <= value <= 10):
            raise ValueError("voltage must be -10..10 V")
        if self.mode == "gui":
            raise NotImplementedError("DAC4ETH.set_voltage_diff not implemented for GUI mode")
        assert self.connection is not None
        self.connection.send(f"DAC4ETH VSD {self.slot} {channel} {value}")

    def __str__(self):  # pragma: no cover
        return f"DAC4ETH (Slot {self.slot}) [{'direct' if self.mode=='direct' else 'gui-unavail'}]"
