"""Tests for the async timer functionality in bear_epoch_time."""

import asyncio

from bear_epoch_time.timer import async_timer, create_async_timer

from .conftest import DummyConsole


def test_async_timer_context_manager(dummy_console: DummyConsole) -> None:
    async def inner() -> None:
        """Inner function to test the async timer context manager."""
        async with async_timer(name="custom_async", console=True, print_func=dummy_console) as data:
            assert data.name == "custom_async"
            assert data.console is True
            assert data.print_func is dummy_console
            await asyncio.sleep(0)

    asyncio.run(inner())
    assert len(dummy_console.messages) == 1
    assert "custom_async" in dummy_console.messages[0]


def test_create_async_timer_decorator(dummy_console: DummyConsole) -> None:
    """Test the create_async_timer decorator."""

    @create_async_timer(console=True, print_func=dummy_console)
    async def decorated() -> str:
        """Decorated async function to test the timer."""
        await asyncio.sleep(0)
        return "done"

    result: str = asyncio.run(decorated())
    assert result == "done"
    assert len(dummy_console.messages) == 1
    assert "decorated" in dummy_console.messages[0]
