from typing import Optional, Sequence, Union
from warnings import warn

import biocutils as ut

from .base import CompressedList
from .partition import Partitioning
from .split_generic import _generic_register_helper, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedStringList(CompressedList):
    """CompressedList implementation for lists of strings."""

    def __init__(
        self,
        unlist_data: ut.StringList,
        partitioning: Partitioning,
        element_metadata: Optional[dict] = None,
        metadata: Optional[dict] = None,
        **kwargs,
    ):
        """Initialize a CompressedStringList.

        Args:
            unlist_data:
                List of strings.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """
        if not isinstance(unlist_data, ut.StringList):
            try:
                warn("trying to coerce 'unlist_data' to `StringList`..")
                unlist_data = ut.StringList(unlist_data)
            except Exception as e:
                raise TypeError("'unlist_data' must be an `StringList`, provided ", type(unlist_data)) from e

        super().__init__(
            unlist_data, partitioning, element_type=ut.StringList, element_metadata=element_metadata, metadata=metadata
        )


class CompressedCharacterList(CompressedStringList):
    pass


@splitAsCompressedList.register
def _(
    data: ut.StringList,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Sequence[str]] = None,
    metadata: Optional[dict] = None,
) -> CompressedStringList:
    """Handle lists of floats."""

    partitioned_data, groups_or_partitions = _generic_register_helper(
        data=data, groups_or_partitions=groups_or_partitions, names=names
    )

    if not isinstance(partitioned_data, ut.StringList):
        partitioned_data = ut.combine_sequences(*partitioned_data)

    return CompressedStringList(unlist_data=partitioned_data, partitioning=groups_or_partitions, metadata=metadata)
