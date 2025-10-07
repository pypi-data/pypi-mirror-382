# cli.py
import sys
import click
from .single_char_client import SingleCharScreenShareClient, SingleCharUIClient
from .single_char_server import SingleCharScreenShareServer
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)
    
@main.command(help="Detail guide on command line")
def help():
    print("Nothing is here yet...")
    
@main.command(help="Run script for client single character type")
@click.argument("ip", required=False)
@click.option("-ui", "--ui", is_flag=True, help="Activate GUI for client")
def clientsingle(ip : str = "", ui : bool = False):
    address = ip.strip().upper() if ip is str else ""
    
    if ui:
        app = SingleCharUIClient(address)
        app.run()
        return
    
    if address == "":
        address = input("Please input the ip address of the device you want to connect: ")
    
    app = SingleCharScreenShareClient(address)
    app.run()

@main.command(help="Run script for server single character type")
@click.argument("width", required=False, type=int)
@click.argument("height", required=False, type=int)
@click.argument("clients", required=False, type=int)
def serversingle(clients, width , height ):
    clients : int = clients or 1
    width : int = width or 960
    height : int = height or 540
    app = SingleCharScreenShareServer(screen_width=width, screen_height=height, clients=clients)
    app.run()