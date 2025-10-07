# cli.py
import sys
import click

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)
    
@main.command(help="Detail guide on command line")
def help():
    print("Nothing is here yet...")