"""Registra os comandos do plugin."""

from .commands.checar import checar
from .commands.monitorar import monitorar
from .commands.trades import trades


def register(cli):
    cli.add_command(checar, name="checar")
    cli.add_command(monitorar, name="monitorar")
    cli.add_command(trades, name="trades")
