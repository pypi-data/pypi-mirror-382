# cli.py
import sys
import click
from .single_char_client import SingleCharScreenShareClient, SingleCharUIClient
from .single_char_server import SingleCharScreenShareServer
from .paragraph_clip_server import ParagraphScreenShareServer
from .paragraph_clip_client import ParagraphScreenShareClient

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)
    
@main.command(help="Detail guide on command line usage.")
def help():
    click.echo(main.get_help(click.Context(main)))
    
@main.command(help="""
    Run this command on the machine that will view the stream and send key presses to the host. You must provide the IP address of the Server.\n
    ### Arguments (Required)\n
    | SERVER_IP | String | The IPv4 address (e.g., 192.168.1.100) of the machine running the server. |\n
    
    \n### Client Hotkeys\n
    | Key | Action |\n
    | :--- | :--- |\n
    | ESC | **Disconnect.** Sends a disconnect message and closes the client window. |\n
    | ` (Backtick) | Toggles the ability to send keyboard input to the host. |\n
    ### Usage\n
    Run this command with the **SERVER_IP** of the host machine running **`serversingle`** to connect.\n
    Upon connecting, a window will open displaying the host's screen, and you can send keyboard input (if not toggled off by the host).\n
    **Important Note on Input Toggle:** The ` (Backtick) hotkey disables *sending* input, but it **continues to store** your keystrokes.\n
    When you toggle input back on, the client will immediately send the entire queue of buffered keys to the host.
    """)
@click.argument("ip", required=False)
@click.argument("port", required=False, type=int)
@click.option("-ui", "--ui", is_flag=True, help="Activate GUI for client")
def clientsingle(ip : str = "",port : int = 5050, ui : bool = False):
    address = ip.strip().upper() if isinstance(ip, str) else ""
    
    if ui:
        app = SingleCharUIClient(address, port=port)
        app.run()
        return
    
    if address == "":
        address = input("Please input the ip address of the device you want to connect: ")
    
    app = SingleCharScreenShareClient(address, port=port)
    app.run()

@main.command(help="""Run script for server single character type\n
    ### Arguments (Optional)\n
    | Argument | Type | Default | Description |\n
    | WIDTH | Integer | 960 | The horizontal resolution for the screen stream. |\n
    | HEIGHT | Integer | 540 | The vertical resolution for the screen stream. |\n
    | CLIENTS | Integer | 1 | The maximum number of simultaneous clients allowed to connect. |\n
    \n
    ### Server Hotkeys\n
    | Key | Action |\n
    | :--- | :--- |\n
    | ESC | **Immediate Shutdown.** Closes the server and all active connections. |\n
    | ` (Backtick) | Toggles all client keyboard input on/off (Input Toggle). |\n
    ### Usage\n
    Start this command on the host machine to begin streaming your screen and enable remote keyboard input.\n
    Clients can connect using the **`clientsingle`** command and interact with your desktop.\n
    """)
@click.argument("width", required=False, type=int)
@click.argument("height", required=False, type=int)
@click.argument("clients", required=False, type=int)
@click.argument("port", required=False, type=int)
def serversingle(clients, port, width , height ):
    clients : int = clients or 1
    port : int = port or 5050
    width : int = width or 960
    height : int = height or 540
    app = SingleCharScreenShareServer(screen_width=width, screen_height=height, clients=clients)
    app.run()

@main.command(help="""Run script for server paragraph type\n
    ### Arguments (Optional)\n
    | Argument | Type | Default | Description |\n
    | WIDTH | Integer | 960 | The horizontal resolution for the screen stream. |\n
    | HEIGHT | Integer | 540 | The vertical resolution for the screen stream. |\n
    | CLIENTS | Integer | 1 | The maximum number of simultaneous clients allowed to connect. |\n
    \n
    ### Server Hotkeys\n
    | Key | Action |\n
    | :--- | :--- |\n
    | ESC | **Immediate Shutdown.** Closes the server and all active connections. |\n
    ### Usage\n
    **Purpose:** This command starts the server to receive a single, large block of text (a paragraph) from a connected client.\n\n
    1. **Run the Command:** Start the server on the host machine using the desired stream resolution and client limit.\n
    2. **Client Transfer:** The remote client connects and sends the complete paragraph of text.\n
    3. **Host Buffer:** The server receives the text and immediately places it into your system's clipboard/memory.\n
    4. **Paste:** You (the host user) can then instantly paste the received content using **Ctrl+V** (or the equivalent paste command for your system).\n\n
    The server remains active until explicitly shut down (e.g., via the **ESC** hotkey).
    """)
@click.argument("width", required=False, type=int)
@click.argument("height", required=False, type=int)
@click.argument("clients", required=False, type=int)
@click.argument("port", required=False, type=int)
def serverpara(clients, port, width , height ):
    clients : int = clients or 1
    port : int = port or 5050
    width : int = width or 960
    height : int = height or 540
    app = ParagraphScreenShareServer(screen_width=width, screen_height=height, clients=clients)
    app.run()

@main.command(help= """Run this command to connect to the paragraph server and send block of text to the host's clipboard.\n
    ### Arguments (Optional)\n
    | Argument | Type | Description |\n
    | SERVER_IP | String | The IPv4 address (e.g., 192.168.1.100) of the machine running the server. |\n
    | PORT | Integer | The port number the server is listening on. |\n
    ### Usage\n
    1. **Run the Command:** Start this client, providing the **SERVER_IP** of the machine running to connect.\n
    2. **Input Text:** Paste or type the full text in the textbox and click **Connect** button.\n
    3. **Transfer:** The client sends the entire paragraph to the server, which places it into the host's clipboard.\n\n
    The client remains active until explicitly shut down on any sides, or just disconnect.
    """)
@click.argument("ip", required=False)
@click.argument("port", required=False, type=int)
def clientpara(ip : str = "", port : int = 5050):
    address = ip.strip().upper() if isinstance(ip, str) else ""
    port : int = port or 5050
    app = ParagraphScreenShareClient(address, port=port)
    app.run()