import asyncio


def running_asyncio_loop() -> asyncio.AbstractEventLoop | None:
    """Returns the asyncio event loop if it exists."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return loop
        else:
            return None
    except RuntimeError:
        return None
