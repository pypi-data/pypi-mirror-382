from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class BaseStorage(ABC):
    @abstractmethod
    async def get_context(self, key: Union[int, str]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_state(self, key: Union[int, str]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set_state(self, key: Union[int, str], state: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def clear_state(self, key: Union[int, str]) -> None:
        pass

    @abstractmethod
    async def clear_data(self, key: Union[int, str]) -> None:
        pass

    @abstractmethod
    async def clear_all(self, key: Union[int, str]) -> None:
        pass

    @abstractmethod
    async def upsert_data(self, key: Union[int, str], **data: Any) -> None:
        pass

    @abstractmethod
    async def get_data(self, key: Union[int, str]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def upsert_context(self, key: Union[int, str], state: Optional[str] = None, **data) -> None:
        pass
