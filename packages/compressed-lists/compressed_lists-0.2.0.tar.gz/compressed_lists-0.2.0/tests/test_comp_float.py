import pytest
from biocutils.FloatList import FloatList

from compressed_lists import CompressedFloatList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def float_data():
    return [[1.1, 1.2], [2.1, 2.2, 2.3], [3]]


@pytest.fixture
def float_list(float_data):
    names = ["fruits1", "fruits2", "fruits3"]
    return CompressedFloatList.from_list(float_data, names)


def test_creation(float_data):
    float_list = CompressedFloatList.from_list(float_data)

    assert len(float_list) == 3
    assert isinstance(float_list.unlist_data, FloatList)
    assert list(float_list.get_unlist_data()) == [1.1, 1.2, 2.1, 2.2, 2.3, 3.0]
    assert list(float_list.get_element_lengths()) == [2, 3, 1]


def test_getitem(float_list):
    assert list(float_list[0]) == [1.1, 1.2]
    assert list(float_list["fruits2"]) == [2.1, 2.2, 2.3]
