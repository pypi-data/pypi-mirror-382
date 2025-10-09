from typing import List, Optional, Sequence, Union

import biocutils as ut
from biocframe import BiocFrame

from .base import CompressedList
from .partition import Partitioning
from .split_generic import _generic_register_helper, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedBiocFrameList(CompressedList):
    """CompressedList for BiocFrames."""

    def __init__(
        self,
        unlist_data: BiocFrame,
        partitioning: Partitioning,
        element_metadata: Optional[dict] = None,
        metadata: Optional[dict] = None,
        **kwargs,
    ):
        """Initialize a CompressedBiocFrameList.

        Args:
            unlist_data:
                BiocFrame object.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """
        if not isinstance(unlist_data, BiocFrame):
            raise TypeError("'unlist_data' is not a `BiocFrame` object.")

        super().__init__(
            unlist_data, partitioning, element_type="BiocFrame", element_metadata=element_metadata, metadata=metadata
        )

    @classmethod
    def from_list(
        cls, lst: List[BiocFrame], names: Optional[Sequence[str]] = None, metadata: Optional[dict] = None
    ) -> "CompressedBiocFrameList":
        """Create a `CompressedBiocFrameList` from a regular list.

        This concatenates the list of `BiocFrame` objects.

        Args:
            lst:
                List of `BiocFrame` objects.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedList`.
        """
        unlist_data = ut.relaxed_combine_rows(*lst)
        partitioning = Partitioning.from_list(lst, names)
        return cls(unlist_data, partitioning, metadata=metadata)

    def __getitem__(self, key: Union[int, str, slice]):
        """Override to handle column extraction using `splitAsCompressedList`."""
        if isinstance(key, str):
            column_data = self._unlist_data.get_column(key)
            return splitAsCompressedList(
                column_data, groups_or_partitions=self._partitioning, names=self.names, metadata=self.metadata
            )
        else:
            return super().__getitem__(key)

    def extract_range(self, start: int, end: int) -> BiocFrame:
        """Extract a range from `unlist_data`.

        This method must be implemented by subclasses to handle
        type-specific extraction from `unlist_data`.

        Args:
            start:
                Start index (inclusive).

            end:
                End index (exclusive).

        Returns:
            Extracted element.
        """
        try:
            return self._unlist_data[start:end, :]
        except Exception as e:
            raise NotImplementedError(
                "Custom classes should implement their own `extract_range` method for slice operations"
            ) from e


@splitAsCompressedList.register
def _(
    data: BiocFrame,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Sequence[str]] = None,
    metadata: Optional[dict] = None,
) -> CompressedBiocFrameList:
    """Handle lists of BiocFrame objects."""

    partitioned_data, groups_or_partitions = _generic_register_helper(
        data=data, groups_or_partitions=groups_or_partitions, names=names
    )

    if not isinstance(partitioned_data, BiocFrame):
        partitioned_data = ut.relaxed_combine_rows(*partitioned_data)

    return CompressedBiocFrameList(unlist_data=partitioned_data, partitioning=groups_or_partitions, metadata=metadata)
