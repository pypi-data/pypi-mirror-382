import asyncio
import pytest

from compton import (
    Orchestrator
)

from .types import (
    SimpleProvider,
    SimpleProvider2,
    SimpleProvider5,
    SimpleReducer,
    SimpleReducer2,
    SimpleConsumer,
    SimpleConsumer2,
    SimpleConsumer4,
    SimpleConsumer5,
    symbol,
    vector,

    DataType
)


def test_no_concurrent_limit_and_outside_event_loop():
    loop = asyncio.new_event_loop()

    consumer = SimpleConsumer4()
    provider = SimpleProvider(
        has_init_delay=False
    )
    provider2 = SimpleProvider2(
        has_init_delay=False
    )

    orchestrator = Orchestrator(
        [SimpleReducer()],
        loop
    ).connect(
        provider
    ).connect(
        provider2
    ).subscribe(
        consumer
    )

    orchestrator.add(symbol).add(symbol)

    async def stop():
        await asyncio.sleep(2)

    loop.run_until_complete(stop())
    loop.stop()

    assert len(consumer.consumed) == 5
    assert list(orchestrator.added) == [symbol]

    orchestrator.remove(symbol).remove(symbol)
    assert not orchestrator.added

    loop.close()


@pytest.mark.asyncio
async def test_main():
    consumer = SimpleConsumer()
    consumer2 = SimpleConsumer2()
    provider = SimpleProvider().go()
    provider2 = SimpleProvider2().go()

    Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).connect(
        provider2
    ).subscribe(
        consumer
    ).subscribe(
        consumer2
    ).add(symbol)

    await asyncio.sleep(1)

    assert consumer.consumed == [0, 1, 2]
    assert consumer2.consumed == [
        (0, 0), (2, 2)
    ]


@pytest.mark.asyncio
async def test_partial_init():
    consumer = SimpleConsumer5()
    provider = SimpleProvider().go()
    provider2 = SimpleProvider2()

    Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).connect(
        provider2
    ).subscribe(
        consumer
    ).add(symbol)

    await asyncio.sleep(1)

    assert consumer.consumed == [
        (0, None), (1, None), (2, None)
    ]

    provider2.go()
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_no_concurrent_limit():
    consumer = SimpleConsumer4()
    provider = SimpleProvider().go()
    provider2 = SimpleProvider2().go()

    Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).connect(
        provider2
    ).subscribe(
        consumer
    ).add(symbol)

    await asyncio.sleep(1)

    assert len(consumer.consumed) == 5


@pytest.mark.asyncio
async def test_main_with_no_subscription():
    consumer = SimpleConsumer()
    provider = SimpleProvider()

    o = Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).add(symbol)

    await asyncio.sleep(1)
    provider.go()

    await asyncio.sleep(1)

    o.subscribe(consumer)

    assert not consumer.consumed


@pytest.mark.asyncio
async def test_main_remove():
    consumer = SimpleConsumer()
    provider = SimpleProvider5().go()

    o = Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).subscribe(consumer).add(symbol)

    await asyncio.sleep(.5)
    o.remove(symbol)
    consumed = list(consumer.consumed)
    await asyncio.sleep(.5)

    assert consumer.consumed == consumed


@pytest.mark.asyncio
async def test_main_with_deferred_init():
    consumer = SimpleConsumer()
    provider = SimpleProvider()

    Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).subscribe(
        consumer
    ).add(symbol)

    await asyncio.sleep(1)
    provider.go()

    await asyncio.sleep(1)
    assert consumer.consumed == [2]


@pytest.mark.asyncio
async def test_main_with_remove_immediately():
    consumer = SimpleConsumer()
    provider = SimpleProvider(
        update_immediately=False
    )

    Orchestrator(
        [SimpleReducer()]
    ).connect(
        provider
    ).subscribe(
        consumer
    ).add(symbol).remove(symbol)

    await asyncio.sleep(1)
    assert consumer.consumed == []


def test_reducer_exists():
    with pytest.raises(
        ValueError,
        match='reducer<DataType.KLINE> already exists'
    ):
        Orchestrator([
            SimpleReducer(),
            SimpleReducer()
        ])


def test_reducer_another_generic_exists():
    with pytest.raises(
        ValueError,
        match='reducer<DataType.KLINE> already exists'
    ):
        Orchestrator([
            SimpleReducer(),
            SimpleReducer2()
        ])


def test_connect_reducer_not_found():
    with pytest.raises(
        KeyError,
        match='reducer<DataType.KLINE,TimeSpan.DAY> must be defined'
    ):
        Orchestrator([]).connect(SimpleProvider())


def test_provider_exists():
    class MoreGenericProvider(SimpleProvider):
        @property
        def vector(self):
            return (DataType.KLINE,)

    with pytest.raises(
        KeyError,
        match='provider<DataType.KLINE,TimeSpan.DAY> exists'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(
            SimpleProvider()
        ).connect(
            SimpleProvider()
        )

    with pytest.raises(
        KeyError,
        match='provider<DataType.KLINE> exists'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(
            MoreGenericProvider()
        ).connect(
            SimpleProvider()
        )

    with pytest.raises(
        KeyError,
        match='provider<DataType.KLINE,TimeSpan.DAY> exists'
    ):
        Orchestrator([
            SimpleReducer()
        ]).connect(
            SimpleProvider()
        ).connect(
            MoreGenericProvider()
        )


def test_subscribe_provider_not_found():
    with pytest.raises(
        KeyError,
        match='provider<DataType.KLINE,TimeSpan.DAY> must be defined'
    ):
        Orchestrator([]).subscribe(
            SimpleConsumer()
        )


@pytest.mark.asyncio
async def test_dispatch_reducer_not_found():
    with pytest.raises(
        KeyError,
        match='reducer<DataType.KLINE,TimeSpan.DAY> is not found'
    ):
        Orchestrator([]).add(symbol)._dispatch(
            False,
            vector,
            symbol,
            {}
        )


def test_dispatch_in_non_coroutine():
    with pytest.raises(
        RuntimeError,
        match='should only be invoked in a coroutine'
    ):
        Orchestrator([]).dispatch(
            vector,
            symbol,
            {}
        )

@pytest.mark.asyncio
async def test_dispatch_with_provider_init_none_payload():
    class NoneProvider(SimpleProvider):
        async def init(self, symbol):
            return None

    consumer = SimpleConsumer()

    Orchestrator([SimpleReducer()]).connect(
        NoneProvider().go()
    ).subscribe(
        consumer
    ).add(symbol)

    await asyncio.sleep(1)

    assert not consumer.consumed
