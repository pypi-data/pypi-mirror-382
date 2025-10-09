from typing import List, Optional, Sequence, Union
from warnings import warn

import biocutils as ut
import numpy as np

from .base import CompressedList
from .partition import Partitioning
from .split_generic import _generic_register_helper, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedNumpyList(CompressedList):
    """CompressedList implementation for lists of NumPy vectors."""

    def __init__(
        self,
        unlist_data: np.ndarray,
        partitioning: Partitioning,
        element_metadata: Optional[dict] = None,
        metadata: Optional[dict] = None,
        **kwargs,
    ):
        """Initialize a CompressedNumpyList.

        Args:
            unlist_data:
                List of NumPy vectors.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """

        if not isinstance(unlist_data, np.ndarray):
            try:
                warn("trying to concatenate/coerce 'unlist_data' to a `np.ndarray`..")
                unlist_data = np.concatenate(unlist_data)
            except Exception as e:
                raise TypeError("'unlist_data' must be an `np.ndarray`, provided ", type(unlist_data)) from e

        super().__init__(
            unlist_data, partitioning, element_type=np.ndarray, element_metadata=element_metadata, metadata=metadata
        )

    @classmethod
    def from_list(
        cls, lst: List[np.ndarray], names: Optional[Sequence[str]] = None, metadata: Optional[dict] = None
    ) -> "CompressedNumpyList":
        """
        Create a `CompressedNumpyList` from a list of NumPy vectors.

        Args:
            lst:
                List of NumPy vectors.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedNumpyList`.
        """
        partitioning = Partitioning.from_list(lst, names)

        if len(lst) == 0:
            unlist_data = np.array([])
        else:
            unlist_data = np.concatenate(lst)

        return cls(unlist_data, partitioning, metadata=metadata)


@splitAsCompressedList.register
def _(
    data: np.ndarray,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Sequence[str]] = None,
    metadata: Optional[dict] = None,
) -> CompressedNumpyList:
    """Handle NumPy arrays."""

    partitioned_data, groups_or_partitions = _generic_register_helper(
        data=data, groups_or_partitions=groups_or_partitions, names=names
    )

    if not isinstance(partitioned_data, np.ndarray):
        partitioned_data = ut.combine_sequences(*partitioned_data)

    return CompressedNumpyList(unlist_data=partitioned_data, partitioning=groups_or_partitions, metadata=metadata)
