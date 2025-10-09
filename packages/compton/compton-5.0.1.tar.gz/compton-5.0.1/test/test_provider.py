import pytest
from compton import (
    Provider,
    Orchestrator
)

from .types import (
    SimpleReducer
)


def test_check():
    class A:
        pass

    with pytest.raises(
        ValueError,
        match='must be an instance of Provider'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(A())  # type: ignore


def test_str():
    class InvalidProvider(Provider):
        @property
        def vector(self):
            return 1

        def init(self):
            pass

        def remove(self):
            pass

    assert str(InvalidProvider()) == 'provider<invalid>'

    with pytest.raises(
        ValueError,
        match='vector of provider<invalid> must be a tuple, but got `1`'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(InvalidProvider())

    class ValidVectorProvider(Provider):
        @property
        def vector(self):
            return (1, 2)

        def init(self):
            pass

        def remove(self):
            pass

    assert str(ValidVectorProvider()) == 'provider<1,2>'


def test_vector_not_hashable():
    class VectorNotHashableProvider(Provider):
        @property
        def vector(self):
            return ({},)

        def init(self):
            pass

        def remove(self):
            pass

    with pytest.raises(
        ValueError,
        match='vector of provider<{}>'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(VectorNotHashableProvider())
