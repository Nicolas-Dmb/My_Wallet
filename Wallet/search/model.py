from enum import Enum
from uuid import UUID

type = Enum('crypto','bourse','immo','cash')

class SearchModel: 
    id: UUID
    type: type
    name: str
    key: str|None
    amount: float
    owned: bool
    other: str|None


