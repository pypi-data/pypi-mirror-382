from mtcli_trade.models.orders_model import buscar_ordens, formatar_ordem
from mtcli.logger import setup_logger

log = setup_logger()


def obter_ordens_pendentes(symbol=None):
    ordens_raw = buscar_ordens(symbol)

    if not ordens_raw:
        log.info(
            f"Nenhuma ordem pendente para {symbol}."
            if symbol
            else "Nenhuma ordem pendente encontrada"
        )
        return []

    ordens = []
    for o in ordens_raw:
        dados = formatar_ordem(o)
        log.info(
            f"{dados['tipo']} | {dados['symbol']} | volume: {dados['volume']} | preço: {dados['preco']} | ticket: {dados['ticket']}"
        )
        ordens.append(dados)
    return ordens
