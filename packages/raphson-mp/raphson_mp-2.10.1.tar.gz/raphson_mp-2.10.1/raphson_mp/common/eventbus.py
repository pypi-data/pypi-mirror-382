from __future__ import annotations

import asyncio
from abc import ABC
from collections.abc import Awaitable, Callable
from typing import TypeVar, cast

from multidict import MultiDict

_HANDLERS: MultiDict[Callable[[Event], Awaitable[None]]] = MultiDict()


class Event(ABC):
    pass


async def fire(event: Event):
    key = type(event).__name__
    await asyncio.gather(*[func(event) for func in _HANDLERS.getall(key, [])])


T_event = TypeVar("T_event", bound=Event)


def subscribe(event_type: type[T_event], handler: Callable[[T_event], Awaitable[None]]):
    key = event_type.__name__

    async def generic_handler(event: Event):
        await handler(cast(T_event, event))

    _HANDLERS.add(key, generic_handler)
