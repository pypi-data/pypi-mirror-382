"""Unified client supporting both GUI (HTTP/stateful) and direct (stateless) modes.

Use a simple string mode selector ("gui" or "direct"). The two operational
paths intentionally do not share an abstraction layer beyond this central
dispatch because their semantics differ (stateful vs stateless).
"""

from __future__ import annotations

from typing import List, Union, Optional, Type, TypeVar, overload

from dbay.modules.dac4d import dac4D
from dbay.modules.dac16d import dac16D
from dbay.modules.fafd import FAFD
from dbay.modules.hic4 import HIC4
from dbay.modules.adc4d import ADC4D
from dbay.modules.dac4eth import DAC4ETH
from dbay.modules.empty import Empty
from dbay.http import Http
from dbay.direct import DeviceConnection, DirectDeviceError

__all__ = ["DBayClient", "DBayError"]


class DBayError(Exception):
    pass


class DBayClient:
    """Primary entrypoint for interacting with DBay hardware.

    Parameters
    ----------
    mode: "gui" | "direct"
        Selects operational path.
    server_address, port: Used only in gui mode.
    direct_host, direct_port, direct_transport, serial_port, baudrate, timeout:
        Used only in direct mode.
    max_slots: Number of slots to track (GUI) or capacity for attachments (direct).
    """

    def __init__(
        self,
        *,
        mode: str = "gui",
        server_address: Optional[str] = None,
        port: int = 8345,
        direct_host: str = "192.168.0.108",
        direct_port: int = 8880,
        direct_transport: str = "udp",
        serial_port: Optional[str] = None,
        baudrate: int = 115200,
        timeout: float = 1.0,
        max_slots: int = 8,
        load_state: bool = True,
        retain_changes: bool = True,
    ):
        mode = mode.lower()
        if mode not in {"gui", "direct"}:
            raise ValueError("mode must be either 'gui' or 'direct'")
        self.mode = mode
        self.max_slots = max_slots
        self._http: Optional[Http] = None
        self._connection: Optional[DeviceConnection] = None
        self.retain_changes = retain_changes

        # slot -> module instance
        self._modules: List[Union[dac4D, dac16D, FAFD, HIC4, ADC4D, DAC4ETH, Empty, None]] = [None] * max_slots

        if self.mode == "gui" and load_state:
            if not server_address:
                raise ValueError("server_address is required in gui mode")
            self._http = Http(server_address, port)
            self._load_full_state()
        elif self.mode == "gui":
            if not server_address:
                raise ValueError("server_address is required in gui mode")
            self._http = Http(server_address, port)
            # intentionally skip loading state
        else:  # direct mode
            self._connection = DeviceConnection(
                mode=direct_transport,
                host=direct_host,
                port=direct_port,
                serial_port=serial_port,
                baudrate=baudrate,
                timeout=timeout,
            )

    # ------------------------------------------------------------------
    # GUI Mode State Loading
    # ------------------------------------------------------------------
    def _load_full_state(self):
        assert self._http is not None
        try:
            response = self._http.get("full-state")
        except Exception as exc:  # pragma: no cover - network dependency
            raise DBayError(f"Failed to load full state: {exc}") from exc
        self._instantiate_modules(response.get("data", []))

    def _instantiate_modules(self, module_data: list):
        for i, module_info in enumerate(module_data):
            if i >= self.max_slots:
                break
            raw_type = module_info.get("core", {}).get("type", "")
            module_type = raw_type.lower()
            if module_type == "dac4d":
                self._modules[i] = dac4D(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            elif module_type == "dac16d":
                self._modules[i] = dac16D(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            elif module_type == "fafd":
                self._modules[i] = FAFD(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            elif module_type == "hic4":
                self._modules[i] = HIC4(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            elif module_type == "adc4d":
                self._modules[i] = ADC4D(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            elif module_type == "dac4eth":
                self._modules[i] = DAC4ETH(module_info, http=self._http, mode="gui", retain_changes=self.retain_changes)
            else:
                self._modules[i] = Empty()

    # ------------------------------------------------------------------
    # Direct Mode Attachment
    # ------------------------------------------------------------------
    M = TypeVar("M", dac4D, dac16D, FAFD, HIC4, ADC4D, DAC4ETH)

    def attach_module(self, slot: int, module_cls: Type[M]) -> M:
        """Attach a module in direct mode using its class.

        Example:
            dac = client.attach_module(0, dac4D)

        The module class must expose a `CORE_TYPE` attribute matching the
        underlying hardware identifier (e.g. "dac4D").
        """
        if self.mode != "direct":
            raise ValueError("attach_module is only valid in direct mode")
        if not (0 <= slot < self.max_slots):
            raise ValueError("slot out of range")
        if self._connection is None:
            raise DBayError("Direct connection not initialized")
        core_type = getattr(module_cls, "CORE_TYPE", None)
        if not core_type:
            raise ValueError("Module class missing CORE_TYPE attribute")
        core_stub = {"core": {"slot": slot, "type": core_type, "name": core_type}}
        # Instantiate with connection + direct mode. Some classes may have different constructor signatures.
        mod: M = module_cls(core_stub, connection=self._connection, mode="direct", retain_changes=self.retain_changes)  # type: ignore[arg-type]
        self._modules[slot] = mod
        return mod

    # ------------------------------------------------------------------
    # Accessors / Listing
    # ------------------------------------------------------------------
    def module(self, slot: int, expected: Optional[str] = None):
        if not (0 <= slot < self.max_slots):
            raise ValueError("slot out of range")
        mod = self._modules[slot]
        if mod is None:
            return None
        if expected and hasattr(mod, "data"):
            mtype = getattr(mod.data.core, "type", None)
            if mtype != expected:
                raise DBayError(f"Module type mismatch at slot {slot}: {mtype} != {expected}")
        return mod

    def list_modules(self):  # pragma: no cover - printing convenience
        print("DBay Modules:")
        print("-------------")
        for i, module in enumerate(self._modules):
            print(f"Slot {i}: {module}")
        print("-------------")
        return self._modules

    # ------------------------------------------------------------------
    # Convenience wrappers for direct mode raw sending (advanced)
    # ------------------------------------------------------------------
    def direct_send(self, command: str) -> str:
        if self.mode != "direct":
            raise ValueError("direct_send only valid in direct mode")
        assert self._connection is not None
        try:
            return self._connection.send(command)
        except DirectDeviceError as exc:
            raise DBayError(str(exc)) from exc

    # Context management (mainly for serial) -------------------------
    def close(self):  # pragma: no cover - trivial
        if self._connection is not None:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

