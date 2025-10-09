import pytest
from compton import (
    # Consumer,
    Orchestrator,
    Reducer
)


def test_check():
    class A:
        pass

    with pytest.raises(
        ValueError,
        match='must be an instance of Reducer'
    ):
        Orchestrator([A()])  # type: ignore


def test_vectors():
    class ErrorVectorsReducer(Reducer):
        @property
        def vectors(self):
            return 1

        def merge(self, *args):
            pass

    with pytest.raises(
        ValueError,
        match='vectors of reducer<invalid> must be an iterable, but got `1`'
    ):
        Orchestrator([ErrorVectorsReducer()])
