from abc import ABC, abstractmethod
from typing import List

class Source(ABC):
    @abstractmethod
    async def fetch_data(self) -> List[str]:
        pass