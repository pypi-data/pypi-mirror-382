"""Comando para executar venda a mercado ou pendente."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from mtcli_trade.models.risco_model import controlar_risco
from mtcli_trade.models.ordem_model import inicializar, criar_ordem, enviar_ordem
from mtcli_trade.conf import (
    SYMBOL,
    LOT,
    SL,
    TP,
    LOSS_LIMIT,
    STATUS_FILE,
)

log = setup_logger()


@click.command(
    "sell", help="Envia ordem de venda a mercado ou pendente, com SL e TP opcionais."
)
@click.version_option(package_name="mtcli-trade")
@click.option(
    "--symbol", "-s", default=SYMBOL, help="Símbolo do ativo (default WINV25)."
)
@click.option(
    "--lot",
    type=float,
    default=LOT,
    help="Quantidade de contratos (default =1.0)",
)
@click.option(
    "-sl", type=float, default=SL, help="Stop loss (em pontos) (default 150)."
)
@click.option("-tp", type=float, default=TP, help="Take profit (em pontos)")
@click.option("--limit", "-l", is_flag=True, help="Envia ordem limit (sell limit)")
@click.option("--preco", "-pr", type=float, default=None, help="Preço da ordem limit")
def sell(symbol, lot, sl, tp, limit, preco):
    """Venda a mercado ou pendente com sl e tp."""
    conectar()

    # ⚠ Verifica risco antes de enviar qualquer ordem
    if controlar_risco(STATUS_FILE, LOSS_LIMIT):
        click.echo("Ordem bloqueada: limite de prejuízo diário atingido.")
        log.info("Envio de ordem bloqueado por risco.")
        shutdown()
        return

    tick = inicializar(symbol)
    if not tick:
        return

    if limit:
        if preco is None:
            click.echo("Para ordens pendentes, defina o --preco")
            shutdown()
            return
        price = preco
        order_type = mt5.ORDER_TYPE_SELL_LIMIT
    else:
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL

    ordem = criar_ordem(symbol, lot, sl, tp, price, order_type, limit)
    enviar_ordem(ordem, limit)
    shutdown()


if __name__ == "__main__":
    sell()
