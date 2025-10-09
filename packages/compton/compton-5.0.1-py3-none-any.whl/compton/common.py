from typing import (
    Any,
    Optional,
    Tuple,
    Hashable,
    TypeVar,
    Dict,
    Union,
    Iterable
)


Symbol = str
Payload = object
Vector = Tuple[Hashable, ...]

T = TypeVar('T')

HierarchicalDict = Dict[Hashable, Union[T, 'HierarchicalDict[T]']]
HierarchicalDictV = Union[T, 'HierarchicalDict[T]']


def match_vector(
    vector: Vector,
    target: Vector
) -> bool:
    """Returns `True` if `vector` matches `target`

    If two vectors has a common sub vector at the beginning, then
    the shorter one matches the longer one
    """

    if vector == target:
        return True

    len_v = len(vector)
    len_t = len(target)

    if len_v > len_t:
        return False

    sub_target = target[:len_v]

    return vector == sub_target


def set_hierarchical(
    target: HierarchicalDict[T],
    vector: Vector,
    value: T,
    loose: bool,
    context: Iterable[Hashable] = []
) -> Tuple[bool, Iterable[Hashable]]:
    """Set the value to a dict hirachically

    Args:
        vector (tuple): the length of vector must be larger than 0
        loose (bool): If `False`, if the target already exists,
        it will treat it as a failure

    Returns:
        tuple:
            - bool: whether the value is set
            - list: the context of the value
    """

    first = vector[0]
    current_context = [*context, first]


    if len(vector) == 1:
        # The last item
        if loose or first not in target:
            # Which means it is the last item of the vector,
            # we just set the value
            target[first] = value
            return True, current_context
        else:
            return False, current_context

    if first in target:
        current = target[first]

        if not isinstance(current, dict):
            # There is a conflict
            return False, current_context
    else:
        # The next level does not exists, we just create it
        current = {}
        target[first] = current

    return set_hierarchical(
        current,
        vector[1:],
        value,
        loose,
        current_context
    )


def get_hierarchical(
    target: HierarchicalDict[T],
    vector: Vector
) -> Optional[Union[T, HierarchicalDict[T]]]:
    """Get a property from a hierarchical dict

    Args:
        target (dict): the dict
        vector (tuple):
    """

    current: HierarchicalDictV[T] = target

    for key in vector:
        if not isinstance(current, dict) or key not in current:
            return None

        current = current[key]

    return current


def get_partial_hierarchical(
    target: HierarchicalDict[T],
    vector: Vector
) -> Optional[T]:
    """Get a property from a hierarchical dict, it will
    return the first non-dict object
    """

    current: HierarchicalDictV[T] = target

    for key in vector:
        if not isinstance(current, dict):
            return current

        if key not in current:
            return None

        current = current[key]

    return None if isinstance(current, dict) else current


VECTOR_SEPARATOR = ','


def stringify_vector(list_like: Iterable[Hashable]) -> str:
    return f'<{VECTOR_SEPARATOR.join([str(x) for x in list_like])}>'


def v_stringify(self, name: str) -> str:
    try:
        vector_str = stringify_vector(self.vector)
    except Exception:
        return f'{name}<invalid>'

    return name + vector_str


def vs_stringify(self, name: str) -> str:
    try:
        vectors = stringify_vector([
            stringify_vector(vector)
            for vector in self.vectors
        ])
    except Exception:
        return f'{name}<invalid>'

    return name + vectors


def is_hashable(subject: Any) -> bool:
    try:
        hash(subject)
        return True
    except Exception:
        return False


def check_vectors(vectors: Any, target):
    if not isinstance(vectors, Iterable):
        raise ValueError(
            f'vectors of {target} must be an iterable, but got `{vectors}`'
        )

    for vector in vectors:
        check_vector(vector, target)


def check_vector(vector, target):
    if not isinstance(vector, tuple):
        raise ValueError(
            f'vector of {target} must be a tuple, but got `{vector}`'
        )

    if not is_hashable(vector):
        raise ValueError(f'vector of {target} is not hashable')
