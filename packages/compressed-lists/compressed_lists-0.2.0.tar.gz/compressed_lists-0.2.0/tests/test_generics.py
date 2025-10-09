import biocutils as ut

from compressed_lists import CompressedFloatList, CompressedIntegerList, Partitioning, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def test_groups():
    float_vec = ut.FloatList([1.1, 1.2, 2.1, 2.2, 2.3, 3.0])
    groups = [1, 2, 3, 1, 2, 3]

    clist = splitAsCompressedList(float_vec, groups_or_partitions=groups)

    assert isinstance(clist, CompressedFloatList)


def test_partitions():
    int_list = splitAsCompressedList(
        ut.IntegerList([1, 2, 3, 4, 5, 6, 7, 8, 9]), groups_or_partitions=Partitioning(ends=[3, 5, 9])
    )

    assert isinstance(int_list, CompressedIntegerList)
