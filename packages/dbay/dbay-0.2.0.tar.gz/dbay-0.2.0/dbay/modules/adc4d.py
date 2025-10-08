from __future__ import annotations

from typing import Optional
from dbay.http import Http
from dbay.direct import DeviceConnection

__all__ = ["ADC4D"]


class ADC4D:
    CORE_TYPE = "ADC4D"
    """Dual-mode ADC4D module.

    Direct commands:
      - read_diff(channel) -> "ADC4D VRD <slot> <channel>"

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

    def read_diff(self, channel: int):
        if not (0 <= channel <= 4):
            raise ValueError("channel must be 0..4")
        if self.mode == "gui":
            raise NotImplementedError("ADC4D.read_diff not implemented for GUI mode")
        assert self.connection is not None
        return self.connection.send(f"ADC4D VRD {self.slot} {channel}")

    # Alias for semantic clarity
    def read_differential(self, channel: int):
        return self.read_diff(channel)

    def __str__(self):  # pragma: no cover
        return f"ADC4D (Slot {self.slot}) [{'direct' if self.mode=='direct' else 'gui-unavail'}]"
