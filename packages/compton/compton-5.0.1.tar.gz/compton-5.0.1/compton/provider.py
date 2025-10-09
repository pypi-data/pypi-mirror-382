from abc import ABC, abstractmethod
from functools import partialmethod
from typing import (
    Callable,
    Optional,
    Any
)

from .common import (
    v_stringify,
    check_vector,

    Vector,
    Symbol,
    Payload
)


Dispatcher = Callable[[Symbol, Payload], None]


class Provider(ABC):
    """
    Notice that self.dispatch should be called in a coroutine
    """

    _dispatch: Optional[Dispatcher]

    __str__ = partialmethod(v_stringify, 'provider')  # type: ignore
    # partialmethod is not supported by mypy,
    # https://github.com/python/mypy/issues/8619
    # so we just ignore it

    @staticmethod
    def check(provider: Any) -> None:
        if not isinstance(provider, Provider):
            raise ValueError(
                f'provider must be an instance of Provider, but got `{provider}`'  # noqa: E501
            )

        check_vector(provider.vector, provider)

    @property
    @abstractmethod
    def vector(self) -> Vector:  # pragma: no cover
        """A provider should only have one vector
        which means a provider should only handle a single type of message
        """
        ...

    @abstractmethod
    async def init(
        self,
        symbol: Symbol
    ) -> Optional[Payload]:  # pragma: no cover
        """Initialize the data for symbol `symbol` from the very beginning
        """
        ...

    @abstractmethod
    def remove(
        self,
        symbol: Symbol
    ) -> None:  # pragma: no cover
        """Discard the symbol, and do not receive further updates
        """
        ...

    def when_update(
        self,
        dispatch: Dispatcher
    ) -> None:  # pragma: no cover
        """Sets the receiver to receive update messages
        """

        # So that we can directly use `self.dispatch` in the provider,
        # However, we could override this method in the provider
        #   to do something else
        self.dispatch = dispatch
