from mat3ra.utils import array as utils

REFERENCE_ARRAY = [1, 2, 3, 4, 5]
SLICE = slice(1, 4)
REFERENCE_ARRAY_SLICE = [2, 3, 4]
INDEX = 2
REFERENCE_ARRAY_INDEX = [3]
INDICES = [0, 2, 3]
REFERENCE_ARRAY_INDICES = [1, 3, 4]


def test_filter_by_slice_or_index_or_indices():
    filtered_by_slice = utils.filter_by_slice_or_index_or_indices(REFERENCE_ARRAY, SLICE)
    assert filtered_by_slice == REFERENCE_ARRAY_SLICE
    filtered_by_index = utils.filter_by_slice_or_index_or_indices(REFERENCE_ARRAY, INDEX)
    assert filtered_by_index == REFERENCE_ARRAY_INDEX
    filtered_by_indices = utils.filter_by_slice_or_index_or_indices(REFERENCE_ARRAY, INDICES)
    assert filtered_by_indices == REFERENCE_ARRAY_INDICES
    filtered_by_none = utils.filter_by_slice_or_index_or_indices(REFERENCE_ARRAY)
    assert filtered_by_none == REFERENCE_ARRAY


def test_convert_to_array_if_not():
    array = utils.convert_to_array_if_not(REFERENCE_ARRAY)
    assert array == REFERENCE_ARRAY
    item = utils.convert_to_array_if_not(REFERENCE_ARRAY[0])
    assert item == [REFERENCE_ARRAY[0]]
