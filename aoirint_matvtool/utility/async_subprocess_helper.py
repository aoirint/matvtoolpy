import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


async def _consume_stream(
    stream: asyncio.StreamReader | None,
    log_callback: Callable[[str], None | Awaitable[None]] | None,
) -> None:
    if stream is None:
        return

    while True:
        line_bytes = await stream.readline()
        if not line_bytes:
            break

        line = line_bytes.decode().strip()
        if not line:
            break

        if asyncio.iscoroutinefunction(log_callback):
            await log_callback(line)
        elif callable(log_callback):
            log_callback(line)


async def wait_process(
    process: asyncio.subprocess.Process,
    stdout_callback: Callable[[str], None | Awaitable[None]] | None = None,
    stderr_callback: Callable[[str], None | Awaitable[None]] | None = None,
) -> int:
    coros: list[Awaitable[Any]] = []
    if process.stdout:
        coros.append(_consume_stream(process.stdout, stdout_callback))
    if process.stderr:
        coros.append(_consume_stream(process.stderr, stderr_callback))

    await asyncio.gather(*coros)

    return await process.wait()
