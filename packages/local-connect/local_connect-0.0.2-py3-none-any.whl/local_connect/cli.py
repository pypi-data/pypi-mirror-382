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
def help(): # Renamed from 'help' to avoid conflict with Python's built-in help()
    click.echo(main.get_help(click.Context(main)))
    
    
@main.command(help="""
    Run this command on the machine that will view the stream and send key presses to the host. You must provide the IP address of the Server.\n
    ### Arguments (Required)\n
    | SERVER_IP | String | **Required.** The IPv4 address (e.g., 192.168.1.100) of the machine running the server. |\n
    
    \n### Client Hotkeys")\n
    | Key | Action |")\n
    | :--- | :--- |")\n
    | ESC | **Disconnect.** Sends a disconnect message and closes the client window. |")\n
    | ` (Backtick) | Toggles the ability to send keyboard input to the host. |")\n
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

@main.command(help="""Run script for server single character type
    \n### Arguments (Optional)\n
    | Argument | Type | Default | Description |\n
    | WIDTH | Integer | 960 | The horizontal resolution for the screen stream. |\n
    | HEIGHT | Integer | 540 | The vertical resolution for the screen stream. |\n
    | CLIENTS | Integer | 1 | The maximum number of simultaneous clients allowed to connect. |\n
    
    \n### Server Hotkeys\n
    | Key | Action |\n
    | :--- | :--- |\n
    | ESC | **Immediate Shutdown.** Closes the server and all active connections. |\n
    | ` (Backtick) | Toggles all client keyboard input on/off (Input Toggle). |\n
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

@main.command(help= "No info")
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

@main.command(help= "No info")
@click.argument("ip", required=False)
@click.argument("port", required=False, type=int)
def clientpara(ip : str = "", port : int = 5050):
    address = ip.strip().upper() if isinstance(ip, str) else ""
    port : int = port or 5050
    app = ParagraphScreenShareClient(address, port=port)
    app.run()