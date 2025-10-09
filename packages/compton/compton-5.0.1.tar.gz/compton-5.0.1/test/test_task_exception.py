import asyncio
import pytest

from compton import (
    Orchestrator
)

from .types import (
    SimpleProvider,
    SimpleProvider3,
    SimpleReducer,
    SimpleReducer3,
    SimpleConsumer3,
    SimpleConsumer6,
    symbol
)


@pytest.mark.asyncio
async def test_process_error(caplog):
    Orchestrator(
        [SimpleReducer()]
    ).connect(
        SimpleProvider().go()
    ).subscribe(
        SimpleConsumer3()
    ).add(symbol)

    await asyncio.sleep(1)

    assert caplog.text.count('you got me') == 3


@pytest.mark.asyncio
async def test_process_error_delayed_update(caplog):
    Orchestrator(
        [SimpleReducer()]
    ).connect(
        SimpleProvider(update_delay=1).go()
    ).subscribe(
        SimpleConsumer3()
    ).add(symbol)

    await asyncio.sleep(2)

    assert caplog.text.count('you got me') == 3


@pytest.mark.asyncio
async def test_should_process_error(caplog):
    Orchestrator(
        [SimpleReducer()]
    ).connect(
        SimpleProvider().go()
    ).subscribe(
        SimpleConsumer6()
    ).add(symbol)

    await asyncio.sleep(1)

    assert caplog.text.count('you got me') == 3


@pytest.mark.asyncio
async def test_reducer_reduce_error(caplog):
    Orchestrator(
        [SimpleReducer3()]
    ).connect(
        SimpleProvider().go()
    ).subscribe(
        SimpleConsumer6()
    ).add(symbol)

    await asyncio.sleep(1)

    assert caplog.text.count('you got me') == 2


@pytest.mark.asyncio
async def test_provider_init_error(caplog):
    Orchestrator(
        [SimpleReducer()]
    ).connect(
        SimpleProvider3().go()
    ).add(symbol)

    await asyncio.sleep(1)

    assert caplog.text.count('you got me') == 4
    assert caplog.text.count('give up') == 1
