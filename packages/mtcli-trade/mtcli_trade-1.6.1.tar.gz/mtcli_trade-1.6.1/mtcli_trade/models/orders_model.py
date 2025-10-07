import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from mtcli_trade.conf import DIGITOS

log = setup_logger()


def buscar_ordens(symbol=None):
    conectar()
    try:
        return mt5.orders_get(symbol=symbol) if symbol else mt5.orders_get()
    finally:
        shutdown()


def formatar_ordem(ordem):
    tipo = (
        "COMPRA"
        if ordem.type == mt5.ORDER_TYPE_BUY_LIMIT
        else "VENDA" if ordem.type == mt5.ORDER_TYPE_SELL_LIMIT else str(ordem.type)
    )
    return {
        "tipo": tipo,
        "symbol": ordem.symbol,
        "volume": ordem.volume_current,
        "preco": round(ordem.price_open, DIGITOS),
        "ticket": ordem.ticket,
    }
