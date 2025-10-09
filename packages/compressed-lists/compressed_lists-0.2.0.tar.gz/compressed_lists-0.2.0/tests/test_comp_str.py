import pytest
from biocutils.StringList import StringList

from compressed_lists import CompressedStringList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def char_data():
    return [["apple", "banana"], ["cherry", "date", "elderberry"], ["fig"]]


@pytest.fixture
def char_list(char_data):
    names = ["fruits1", "fruits2", "fruits3"]
    return CompressedStringList.from_list(char_data, names)


def test_creation(char_data):
    char_list = CompressedStringList.from_list(char_data)

    assert len(char_list) == 3
    assert isinstance(char_list.unlist_data, StringList)
    assert list(char_list.get_unlist_data()) == ["apple", "banana", "cherry", "date", "elderberry", "fig"]
    assert list(char_list.get_element_lengths()) == [2, 3, 1]


def test_getitem(char_list):
    assert list(char_list[0]) == ["apple", "banana"]
    assert list(char_list["fruits2"]) == ["cherry", "date", "elderberry"]


def test_lapply(char_list):
    uppercased = char_list.lapply(lambda x: [s.upper() for s in x])

    assert len(uppercased) == len(char_list)
    assert list(uppercased[0]) == ["APPLE", "BANANA"]
    assert list(uppercased[1]) == ["CHERRY", "DATE", "ELDERBERRY"]
    assert list(uppercased[2]) == ["FIG"]
