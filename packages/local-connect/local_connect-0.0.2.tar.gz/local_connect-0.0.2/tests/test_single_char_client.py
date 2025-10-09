import pytest
from local_connect.single_char_server import SingleCharScreenShareServer
from local_connect.single_char_client import SingleCharScreenShareClient, SingleCharUIClient
import socket
import threading
import time

def test_init_no_ui():
    client = SingleCharScreenShareClient(default_ip="Unknown IP")
    assert client.HOST == "Unknown IP"
    assert client.PORT == 5050
    assert client.connecting == False
    assert client.allow_input == True
    assert client.latest_frame == None
    
def test_init_with_ui():
    client = SingleCharUIClient(default_ip="Unknown IP")
    assert client.HOST == "Unknown IP"
    assert client.PORT == 5050
    assert client.connecting == False
    assert client.allow_input == True
    assert client.latest_frame == None
    assert client.root == None
    assert client.entry == None
    assert client.output_var == None
    
@pytest.mark.timeout(6)  # prevent infinite hang
def test_init_connection_no_ui():
    # Create server
    server = SingleCharScreenShareServer()

    # Run server in background thread
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Give server a moment to start listening
    time.sleep(1)

    # Create client and connect
    host_ip = socket.gethostbyname(socket.gethostname())
    client = SingleCharScreenShareClient(default_ip=host_ip)

    client_thread = threading.Thread(target=client.run, daemon=True)
    client_thread.start()

    # Give them time to handshake
    time.sleep(2)

    # Check connection states
    assert client.connecting is True
    assert server.server_running is True

    # Cleanup
    client.exit()
    server.stop()  # assuming your server has a stop() method
    server_thread.join(timeout=1)
    client_thread.join(timeout=1)
    

@pytest.mark.timeout(6)  # prevent infinite hang
def test_init_connection_with_ui():
    # Create server
    server = SingleCharScreenShareServer()

    # Run server in background thread
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Give server a moment to start listening
    time.sleep(1)

    # Create client and connect
    host_ip = socket.gethostbyname(socket.gethostname())
    client = SingleCharUIClient(default_ip=host_ip)
    
    client_thread = threading.Thread(target=client.start_client, daemon=True)
    client_thread.start()

    # Give them time to handshake
    time.sleep(2)

    # Check connection states
    assert client.connecting is True
    assert server.server_running is True

    # Cleanup
    client.exit()
    server.stop()  # assuming your server has a stop() method
    server_thread.join(timeout=1)
    client_thread.join(timeout=1)
    