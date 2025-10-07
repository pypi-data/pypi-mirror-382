"""Comando lucro - exibe os diferentes tipos de lucro."""

import click
from mtcli.logger import setup_logger
from mtcli_risco.models.trades_model import (
    obter_lucro_aberto,
    calcular_lucro_realizado,
    calcular_lucro_total_dia,
)


log = setup_logger()


@click.command(
    "trades", help="Exibe os lucros realizados, abertos e totais do dia atual."
)
@click.version_option(package_name="mtcli-risco")
@click.option(
    "--aberto", "-a", is_flag=True, default=False, help="Exibe o lucro aberto."
)
@click.option(
    "--realizado",
    "-r",
    is_flag=True,
    default=False,
    help="Exibe o lucro realizado do dia.",
)
@click.option(
    "--total", "-t", is_flag=True, default=False, help="Exibe o lucro total do dia."
)
def trades(aberto, realizado, total):
    """Exibe os lucros aberto, realizado e total do dia."""
    lucro_aberto = obter_lucro_aberto()
    lucro_realizado = calcular_lucro_realizado()
    lucro_total = calcular_lucro_total_dia()

    if aberto:
        click.echo(f"{lucro_aberto:.2f}")
        return

    if realizado:
        click.echo(f"{lucro_realizado:.2f}")
        return

    if total:
        click.echo(f"{lucro_total:.2f}")
        return

    click.echo(f"lucro em aberto {lucro_aberto:.2f}")
    click.echo(f"lucro realizado {lucro_realizado:.2f}")
    click.echo(f"lucro total {lucro_total:.2f}")


if __name__ == "__main__":
    trades()
