import secrets
from unittest.mock import AsyncMock, Mock

from raphson_mp.common import eventbus
from raphson_mp.server import events


async def test_events():
    # subscribe
    handler = AsyncMock()
    eventbus.subscribe(events.StoppedPlayingEvent, handler)

    # handler should not be called when other event is fired
    other_event = events.FileChangeEvent(Mock(), Mock(), None)
    await eventbus.fire(other_event)
    handler.assert_not_called()

    # handler should now be called
    player_id = secrets.token_urlsafe()
    correct_event = events.StoppedPlayingEvent(player_id)
    await eventbus.fire(event=correct_event)
    handler.assert_called_once_with(correct_event)
