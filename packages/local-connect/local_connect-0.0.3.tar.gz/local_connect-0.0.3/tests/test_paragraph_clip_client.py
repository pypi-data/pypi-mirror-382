from local_connect.paragraph_clip_client import ParagraphScreenShareClient
from local_connect.paragraph_clip_server import ParagraphScreenShareServer
import pytest
import threading
import time
import socket

def test_init():
    client = ParagraphScreenShareClient("Unknown IP")
    assert client.connecting == False
    assert client.PORT == 5050
    assert client.HOST == "Unknown IP"
    assert client.client == None
    assert client.connecting == False
    assert client.latest_frame == None
    assert client.OUTPUT == ""

    # GUI attributes
    assert client.root == None
    assert client.ip_entry == None
    assert client.input_entry == None
    assert client.output_var == None

@pytest.mark.timeout(10)  # prevent infinite hang
def test_connection():
    # Create server
    server = ParagraphScreenShareServer()

    # Run server in background thread
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Give server a moment to start listening
    time.sleep(1)
    
    # Create client and connect
    host_ip = socket.gethostbyname(socket.gethostname())
    client = ParagraphScreenShareClient(default_ip=host_ip)
    
    client_thread = threading.Thread(target=client.start_client, daemon=True)
    client_thread.start()

    # Give them time to handshake
    time.sleep(2)

    # Check connection states
    assert client.connecting is True
    assert server.server_running is True

    client.send_input()
    expected_text = "Default input"
    time.sleep(2)
    final_text = server.lasted_copy

    assert final_text == expected_text #because pyperclip cant use in threading
    
    # Cleanup
    client.exit()
    server.stop()  # assuming your server has a stop() method
    server_thread.join(timeout=1)
    client_thread.join(timeout=1)
    
