r"""
Broadcast functionality for time series
"""


#[

from __future__ import annotations

import numpy as _np
from .. import wrongdoings as _wrongdoings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Self

#]


def mixin(klass: type, ) -> type:
    r"""
    Inlay the broadcast methods in the class
    """
    #[
    klass.broadcast_variants = broadcast_variants
    return klass
    #]


#-------------------------------------------------------------------------------
# Functions to be used as methods in Series class
#-------------------------------------------------------------------------------


def broadcast_variants(self, num_variants, ) -> None:
    """
    Broadcast variants to match the specified number of variants
    """
    if self.data.shape[1] == num_variants:
        return
    if self.data.shape[1] == 1:
        self.data = _np.repeat(self.data, num_variants, axis=1, )
        return
    raise _wrongdoings.IrisPieError("Cannot broadcast variants")


#-------------------------------------------------------------------------------
# Standalone functions for use across modules
#-------------------------------------------------------------------------------


def broadcast_variants_if_needed(
    self: 'Series',
    other: 'Series',
) -> tuple['Series', 'Series']:
    """
    Broadcast variants between two Series objects if needed
    """
    #[
    if self.num_variants == other.num_variants:
        return self, other,
    #
    if self.num_variants == 1:
        return self.broadcast_variants(other.num_variants, ), other
    #
    if other.num_variants == 1:
        return self, other.broadcast_variants(self.num_variants, )
    #
    raise _wrongdoings.IrisPieError("Cannot broadcast time series variants")
    #]


#-------------------------------------------------------------------------------
