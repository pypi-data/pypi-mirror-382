import pydantic
from typing import Awaitable, Callable, List, Optional
from fastapi import Request, Response


class LockFundsRequest(pydantic.BaseModel):
    user_id: str
    amount: float


class LockFundsResponse(pydantic.BaseModel):
    lock_id: str


class UnlockFundsRequest(pydantic.BaseModel):
    lock_id: str
    real_cost: float


class TopUpRequest(pydantic.BaseModel):
    user_id: str
    amount: float


class TopUpResponse(pydantic.BaseModel):
    user_id: str
    new_balance: float


class MeteringConfig(pydantic.BaseModel):
    user_id_extractor: Callable[[Request], Awaitable[str]]
    estimated_cost: float
    cost_calculator: Optional[Callable[[Request, Response], Awaitable[float]]] = None


class User(pydantic.BaseModel):
    user_id: str
    balance: float


class Lock(pydantic.BaseModel):
    lock_id: str


class SummaryResponse(pydantic.BaseModel):
    users: List[User]
    locks: List[Lock]
