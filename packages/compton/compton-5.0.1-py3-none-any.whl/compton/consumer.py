import logging
from abc import ABC, abstractmethod
from functools import partialmethod
from typing import (
    List,
    Optional,
    Iterable,
    Dict,
    Set
)

from .common import (
    check_vectors,
    vs_stringify,

    Payload,
    Vector,
    Symbol
)


class Consumer(ABC):
    @staticmethod
    def check(consumer) -> None:
        if not isinstance(consumer, Consumer):
            raise ValueError(
                f'consumer must be an instance of Consumer, but got `{consumer}`'  # noqa: E501
            )

        check_vectors(consumer.vectors, consumer)

    __str__ = partialmethod(vs_stringify, 'consumer')  # type: ignore

    @property
    @abstractmethod
    def vectors(self) -> Iterable[Vector]:  # pragma: no cover
        ...

    @property
    def all(self) -> bool:
        return False

    @property
    def concurrency(self) -> int:
        """
        Concurrency limit for method `process`
        """
        return 0

    def should_process(
        self,
        symbol: Symbol,
        *payloads: Optional[Payload]
    ) -> bool:
        return True

    @abstractmethod
    async def process(
        self,
        symbol: Symbol,
        *payloads: Optional[Payload]
    ) -> None:  # pragma: no cover
        ...


logger = logging.getLogger(__name__)


class ConsumerSentinel:
    _changed: Dict[Symbol, Set[Vector]]

    def __init__(
        self,
        consumer: Consumer
    ):
        Consumer.check(consumer)

        self._consumer = consumer
        self._vectors = set(consumer.vectors)
        self._need_all_changes = bool(consumer.all)

        self._changed = {}
        self._processing = 0

        concurrency = consumer.concurrency

        self._max_processing = int(concurrency) if concurrency else 0

    @property
    def vectors(self):
        return self._consumer.vectors

    def satisfy(self, symbol, vector) -> bool:
        if self._need_all_changes:
            # If the consumer requires change for every vector

            if symbol in self._changed:
                changed = self._changed[symbol]
            else:
                changed = set()
                self._changed[symbol] = changed

            changed.add(vector)

            if changed != self._vectors:
                return False

        # No concurrency limit
        # Or does not reach the limit
        return (
            self._max_processing == 0
            or self._processing < self._max_processing
        )

    def process(self, symbol, payloads: List[Payload], loop):
        # We need to try-catch this method,
        # because it won't be raised to the outside and interrupt the program.
        # Otherwise it will hard to debug
        try:
            if not self._consumer.should_process(symbol, *payloads):
                return
        except Exception as e:
            logger.error('consumer should_process error: %s', e)
            return

        if self._need_all_changes:
            # Only if we start to process, then we clear changed
            self._changed[symbol].clear()

        self._processing += 1

        task = loop.create_task(self._consumer.process(symbol, *payloads))
        task.add_done_callback(self._on_process_done)

    def _on_process_done(self, task):
        """Handle task completion and cleanup"""
        # Check if task completed with an exception
        if task.exception() is not None:
            logger.error('consumer process error: %s', task.exception())

        self._processing -= 1
