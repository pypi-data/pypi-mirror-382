import pytest
from biocutils.BooleanList import BooleanList

from compressed_lists import CompressedBooleanList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def bool_data():
    return [[True, False], [False, True, False], [False]]


@pytest.fixture
def bool_list(bool_data):
    names = ["fruits1", "fruits2", "fruits3"]
    return CompressedBooleanList.from_list(bool_data, names)


def test_creation(bool_data):
    bool_list = CompressedBooleanList.from_list(bool_data)

    assert len(bool_list) == 3
    assert isinstance(bool_list.unlist_data, BooleanList)
    assert list(bool_list.get_unlist_data()) == [True, False, False, True, False, False]
    assert list(bool_list.get_element_lengths()) == [2, 3, 1]


def test_getitem(bool_list):
    assert list(bool_list[0]) == [True, False]
    assert list(bool_list["fruits2"]) == [False, True, False]
