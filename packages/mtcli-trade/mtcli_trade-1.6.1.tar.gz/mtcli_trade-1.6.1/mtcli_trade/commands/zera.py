"""Comando para encerrar todas as posições."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from mtcli_trade.models.posicoes_model import existem_posicoes, encerra_posicoes

log = setup_logger()


@click.command(
    "zera", help="Encerra todas as posições abertas (ou de um ativo específico)."
)
@click.version_option(package_name="mtcli-trade")
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo (opcional)")
def zera(symbol):
    """Encerra todas as posições abertas (ou de um símbolo)"""
    if not existem_posicoes(symbol):
        click.echo("Não existem posições abertas")
        return

    resultados = encerra_posicoes(symbol)
    log.debug(f"Zeragem: {resultados}")
    if resultados:
        click.echo("Todas as posições foram encerradas")
        for r in resultados:
            click.echo(
                f"{r.order} ativo {r.request.symbol} volume {r.volume} preco {r.price}"
            )
        return
    else:
        click.echo("Falha ao encerrar posiçõs")


if __name__ == "__main__":
    zera()
