import pytest
from local_connect.single_char_server import SingleCharScreenShareServer

def test_init():
    server = SingleCharScreenShareServer()
    assert server.screen_height == 540
    assert server.screen_width == 960
    assert server.max_clients == 1
    assert server.server_running == True
    assert server.allow_input == True