"""Gerenciamento de posiçõs e órdens pendentes."""

import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


def existem_posicoes(symbol=None) -> bool:
    """Verifica se existem posiçõs abertas."""
    conectar()

    posicoes = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()

    if not posicoes:
        log.info(
            f"Nenhuma posição para {symbol}" if symbol else "Nenhuma posição encontrada"
        )
        shutdown()
        return False
    else:
        return True


def encerra_posicoes(symbol=None):
    """Encerra todas as posições abertas (ou de um símbolo)"""
    conectar()

    posicoes = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    log.debug(posicoes)
    resultados = []
    for p in posicoes:
        ordem = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": p.symbol,
            "volume": p.volume,
            "type": (
                mt5.ORDER_TYPE_SELL
                if p.type == mt5.POSITION_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            ),
            "price": (
                mt5.symbol_info_tick(p.symbol).bid
                if p.type == mt5.POSITION_TYPE_BUY
                else mt5.symbol_info_tick(p.symbol).ask
            ),
            "deviation": 10,
            "magic": 1001,
            "comment": "Zerar posição",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        log.debug(f"Requisição para zerar posições: {ordem}.")

        resultado = mt5.order_send(ordem)
        if resultado.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"Posição {p.ticket} ({p.symbol}) encerrada.")
        else:
            log.error(
                f"Falha ao encerrar {p.symbol} (ticket {p.ticket}): {resultado.retcode}"
            )
        resultados.append(resultado)

    shutdown()
    return resultados
