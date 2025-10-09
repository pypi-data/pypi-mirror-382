import pytest
from compton import (
    Consumer,
    Orchestrator
)

from .types import (
    SimpleReducer,
    SimpleProvider
)


def test_check():
    class A:
        pass

    with pytest.raises(
        ValueError,
        match='must be an instance of Consumer'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(
            SimpleProvider()
        ).subscribe(A())  # type: ignore


def test_str():
    class InvalidConsumer(Consumer):
        @property
        def vectors(self):
            return 1

        def process(self):
            pass

    assert str(InvalidConsumer()) == 'consumer<invalid>'

    class ValidVectorsConsumer(Consumer):
        @property
        def vectors(self):
            return [(1,), (2,)]

        def process(self):
            pass

    assert str(ValidVectorsConsumer()) == 'consumer<<1>,<2>>'
