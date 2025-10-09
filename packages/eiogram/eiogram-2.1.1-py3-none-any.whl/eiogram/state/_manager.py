from typing import Optional, Union, Any, Dict
from .storage import BaseStorage, MemoryStorage
from ._state import State


class StateManager:
    def __init__(self, key: Union[int, str], storage: BaseStorage = MemoryStorage()):
        self.storage = storage
        self.key = key

    async def set_state(self, state: State, **kwargs: Any) -> None:
        await self.storage.set_state(self.key, state=state.name, **kwargs)

    async def get_context(self, **kwargs: Any) -> Dict[str, Any]:
        full_data = await self.storage.get_context(self.key, **kwargs)
        return {"state": full_data.get("state"), "data": full_data.get("data", {})}

    async def upsert_context(self, state: Optional[State] = None, **kwargs: Any) -> None:
        state_name = state.name if state is not None else None
        await self.storage.upsert_context(key=self.key, state=state_name, **kwargs)

    async def get_state(self, **kwargs: Any) -> Optional[State]:
        return await self.storage.get_state(self.key, **kwargs)

    async def upsert_data(self, **kwargs: Any) -> None:
        return await self.storage.upsert_data(self.key, **kwargs)

    async def get_data(self, **kwargs: Any) -> Dict[str, Any]:
        return await self.storage.get_data(self.key, **kwargs)

    async def clear_all(self, **kwargs: Any) -> None:
        await self.storage.clear_all(self.key, **kwargs)

    async def clear_state(self, **kwargs: Any) -> None:
        await self.storage.clear_state(self.key, **kwargs)

    async def clear_data(self, **kwargs: Any) -> None:
        await self.storage.clear_data(self.key, **kwargs)
