import pytest
from local_connect.paragraph_clip_server import ParagraphScreenShareServer

def test_init():
    server = ParagraphScreenShareServer()
    assert server.screen_height == 540
    assert server.screen_width == 960
    assert server.max_clients == 1
    assert server.PORT == 5050
    assert server.server_running == True