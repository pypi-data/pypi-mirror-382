from typing import Optional, Sequence, Union
from warnings import warn

import biocutils as ut

from .base import CompressedList
from .partition import Partitioning
from .split_generic import _generic_register_helper, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedIntegerList(CompressedList):
    """CompressedList implementation for lists of integers."""

    def __init__(
        self,
        unlist_data: ut.IntegerList,
        partitioning: Partitioning,
        element_metadata: Optional[dict] = None,
        metadata: Optional[dict] = None,
        **kwargs,
    ):
        """Initialize a CompressedIntegerList.

        Args:
            unlist_data:
                List of integers.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """

        if not isinstance(unlist_data, ut.IntegerList):
            try:
                warn("trying to coerce 'unlist_data' to `IntegerList`..")
                unlist_data = ut.IntegerList(unlist_data)
            except Exception as e:
                raise TypeError("'unlist_data' must be an `IntegerList`, provided ", type(unlist_data)) from e

        super().__init__(
            unlist_data, partitioning, element_type=ut.IntegerList, element_metadata=element_metadata, metadata=metadata
        )


@splitAsCompressedList.register
def _(
    data: ut.IntegerList,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Sequence[str]] = None,
    metadata: Optional[dict] = None,
) -> CompressedIntegerList:
    """Handle lists of integers."""

    partitioned_data, groups_or_partitions = _generic_register_helper(
        data=data, groups_or_partitions=groups_or_partitions, names=names
    )

    if not isinstance(partitioned_data, ut.IntegerList):
        partitioned_data = ut.combine_sequences(*partitioned_data)

    return CompressedIntegerList(unlist_data=partitioned_data, partitioning=groups_or_partitions, metadata=metadata)
