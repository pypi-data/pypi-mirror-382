import asyncio

class TaskCompletionSource:
    def __init__(self):
        self._future = None

    def set_result(self, result):
        if not self._future.done():
            self._future.set_result(result)
        else:
            raise RuntimeError("Result already set")

    def set_exception(self, exception):
        if not self._future.done():
            self._future.set_exception(exception)
        else:
            raise RuntimeError("Exception already set")

    def is_done(self) -> bool:
        return self._future.done()

    async def get_future(self):
        if self._future is None:
            self._future = asyncio.get_event_loop().create_future()
        return await self._future
