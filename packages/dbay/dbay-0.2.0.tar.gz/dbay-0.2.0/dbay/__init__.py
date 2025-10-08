"""DBay unified client package.

Exports the dual-mode `DBayClient` class. The legacy HTTP-only `DBay` entry has
been superseded.
"""

from .client import DBayClient, DBayError  # noqa: F401
from .modules.dac4d import dac4D  # noqa: F401
from .modules.dac16d import dac16D  # noqa: F401
from .modules.empty import Empty  # noqa: F401
from .modules.fafd import FAFD  # noqa: F401
from .modules.hic4 import HIC4  # noqa: F401
from .modules.adc4d import ADC4D  # noqa: F401
from .modules.dac4eth import DAC4ETH  # noqa: F401

__all__ = [
	"DBayClient",
	"DBayError",
	"dac4D",
	"dac16D",
	"Empty",
	"FAFD",
	"HIC4",
	"ADC4D",
	"DAC4ETH",
]
