from collections import defaultdict
from functools import singledispatch
from typing import Any, List, Optional, Sequence, Tuple, Union

import numpy as np

from .base import CompressedList
from .partition import Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def groups_to_partition(
    data: Any, groups: list, names: Optional[Sequence[str]] = None
) -> Tuple[List[Any], Partitioning]:
    """Convert group membership vector to partitioned data and Partitioning object.

    Args:
        data:
            The data to be split (flat vector-like object).

        groups:
            Group membership vector, same length as data.

        names:
            Optional names for groups.

    Returns:
        Tuple of (partitioned_data_list, partitioning_object)
    """
    if len(data) != len(groups):
        raise ValueError(f"Length of data ({len(data)}) must match length of groups ({len(groups)})")

    group_dict = defaultdict(list)
    for item, group in zip(data, groups):
        group_dict[group].append(item)

    sorted_groups = sorted(group_dict.keys())
    partitioned_data = [group_dict[group] for group in sorted_groups]

    if names is None:
        group_names = [str(group) for group in sorted_groups]
    else:
        if len(names) != len(sorted_groups):
            raise ValueError(
                f"Length of names ({len(names)}) must match number of unique groups ({len(sorted_groups)})"
            )
        group_names = names

    partitioning = Partitioning.from_list(partitioned_data, group_names)

    return partitioned_data, partitioning


@singledispatch
def splitAsCompressedList(
    data: Any,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Sequence[str]] = None,
    metadata: Optional[dict] = None,
) -> CompressedList:
    """Generic function to split data into an appropriate `CompressedList` subclass.

    This function can work in two modes:
    1. Group-based splitting where a flat vector is split according to group membership.
    2. Partition-based splitting where a flat vector is split according to explicit partitions.

    Args:
        data:
            The data to split into a `CompressedList`.

        groups_or_partitions:
            Optional group membership vector (same length as data) or
            explicit partitioning object.

        names:
            Optional names for the list elements.

        metadata:
            Optional metadata for the `CompressedList`.

    Returns:
        An appropriate `CompressedList` subclass instance.
    """
    element_type = type(data)
    raise NotImplementedError(f"No `splitAsCompressedList` dispatcher found for element type {element_type}")


def _generic_register_helper(data, groups_or_partitions, names=None):
    if groups_or_partitions is None:
        raise ValueError("'groups_or_paritions' cannot be 'None'.")

    if not data:
        raise ValueError("'data' cannot be empty.")

    if isinstance(groups_or_partitions, Partitioning):
        if names is not None:
            groups_or_partitions = groups_or_partitions.set_names(names, in_place=False)

        # TODO: probably not necessary to split when groups is a partition object.
        # unless ordering matters
        # partitioned_data = []
        # for i in range(len(groups_or_partitions)):
        #     start, end = groups_or_partitions.get_partition_range(i)
        #     partitioned_data.append(data[start:end])
        partitioned_data = data
    elif isinstance(groups_or_partitions, (list, np.ndarray)):
        partitioned_data, groups_or_partitions = groups_to_partition(data, groups=groups_or_partitions, names=names)

        if len(partitioned_data) == 0:
            raise ValueError("No data after grouping")
    else:
        raise ValueError("'groups_or_paritions' must be a group vector or a Partition object.")

    return partitioned_data, groups_or_partitions
