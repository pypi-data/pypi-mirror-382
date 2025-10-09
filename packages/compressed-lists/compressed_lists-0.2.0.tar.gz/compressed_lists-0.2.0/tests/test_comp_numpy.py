import numpy as np
import pytest

from compressed_lists import CompressedNumpyList, Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def numpy_data():
    return [np.array([1, 2, 3]), np.array([4, 5]), np.array([6, 7, 8, 9])]


@pytest.fixture
def numpy_list(numpy_data):
    names = ["A", "B", "C"]
    return CompressedNumpyList.from_list(numpy_data, names)


def test_creation(numpy_data):
    numpy_list = CompressedNumpyList.from_list(numpy_data)

    assert len(numpy_list) == 3
    assert isinstance(numpy_list.unlist_data, np.ndarray)
    assert list(numpy_list.get_unlist_data()) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(numpy_list.get_element_lengths()) == [3, 2, 4]


def test_creation_from_parts():
    numpy_list = CompressedNumpyList(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]), Partitioning(ends=[3, 5, 9]))

    assert len(numpy_list) == 3
    assert isinstance(numpy_list.unlist_data, np.ndarray)
    assert list(numpy_list.get_unlist_data()) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(numpy_list.get_element_lengths()) == [3, 2, 4]


def test_creation_with_names(numpy_data):
    names = ["A", "B", "C"]
    numpy_list = CompressedNumpyList.from_list(numpy_data, names)

    assert list(numpy_list.names) == names


def test_validation():
    data = np.array([1, 2, 3, 4, 5])
    partitioning = Partitioning([2, 4, 7])

    with pytest.raises(ValueError):
        CompressedNumpyList(data, partitioning)


def test_getitem_by_index(numpy_list):
    assert np.allclose(numpy_list[0], [1, 2, 3])
    assert np.allclose(numpy_list[1], [4, 5])
    assert np.allclose(numpy_list[2], [6, 7, 8, 9])
    assert np.allclose(numpy_list[-1], [6, 7, 8, 9])

    with pytest.raises(IndexError):
        numpy_list[3]


def test_getitem_by_name(numpy_list):
    assert np.allclose(numpy_list["A"], [1, 2, 3])
    assert np.allclose(numpy_list["B"], [4, 5])
    assert np.allclose(numpy_list["C"], [6, 7, 8, 9])

    with pytest.raises(KeyError):
        numpy_list["D"]


def test_getitem_by_slice(numpy_list):
    sliced = numpy_list[1:3]

    assert len(sliced) == 2
    assert np.allclose(sliced[0], [4, 5])
    assert np.allclose(sliced[1], [6, 7, 8, 9])
    assert list(sliced.names) == ["B", "C"]

    # Empty slice
    empty = numpy_list[3:4]
    assert len(empty) == 0


def test_iteration(numpy_list, numpy_data):
    items = list(numpy_list)
    for i, lst in enumerate(items):
        assert np.allclose(lst, numpy_data[i])


def test_to_list(numpy_list, numpy_data):
    regular_list = numpy_list.to_list()
    for i, lst in enumerate(regular_list):
        assert np.allclose(list(lst), numpy_data[i])


def test_unlist(numpy_list):
    unlisted = numpy_list.unlist()
    assert isinstance(unlisted, np.ndarray)
    assert np.allclose(unlisted, [1, 2, 3, 4, 5, 6, 7, 8, 9])
