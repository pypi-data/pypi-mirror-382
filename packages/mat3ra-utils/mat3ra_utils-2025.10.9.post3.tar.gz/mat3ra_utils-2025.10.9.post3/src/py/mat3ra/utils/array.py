from typing import Any, List, Optional, Union


def filter_by_slice_or_index_or_indices(
    array: List, slice_or_index_or_indices: Optional[Union[slice, int, List[int]]] = None
):
    if isinstance(slice_or_index_or_indices, list):
        return list(map(lambda x: array[x], slice_or_index_or_indices))
    if isinstance(slice_or_index_or_indices, slice):
        return array[slice_or_index_or_indices]
    if isinstance(slice_or_index_or_indices, int):
        return [array[slice_or_index_or_indices]]
    return array


def convert_to_array_if_not(array_or_item: Union[List, Any]):
    return array_or_item if isinstance(array_or_item, list) else [array_or_item]
