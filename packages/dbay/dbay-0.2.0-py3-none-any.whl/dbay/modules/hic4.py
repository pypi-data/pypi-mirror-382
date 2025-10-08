from __future__ import annotations

from typing import Optional
from dbay.http import Http
from dbay.direct import DeviceConnection

__all__ = ["HIC4"]


class HIC4:
    CORE_TYPE = "HIC4"
    """Dual-mode HIC4 module.

    Direct commands:
      - set_voltage(channel, value) -> "HIC4 VS <slot> <channel> <value>"

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
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0..3")
        if self.mode == "gui":
            raise NotImplementedError("HIC4.set_voltage not implemented for GUI mode")
        assert self.connection is not None
        self.connection.send(f"HIC4 VS {self.slot} {channel} {value}")

    def __str__(self):  # pragma: no cover
        return f"HIC4 (Slot {self.slot}) [{'direct' if self.mode=='direct' else 'gui-unavail'}]"
