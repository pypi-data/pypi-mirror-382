from typing import TYPE_CHECKING
from . import beepper as _beepper

beep = _beepper.beep

if TYPE_CHECKING:
    from .beepper import beep as beep

__all__ = ["beep"]
