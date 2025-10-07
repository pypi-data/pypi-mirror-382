import click
from mtcli_trade.controllers.orders_controller import obter_ordens_pendentes
from mtcli_trade.views.orders_view import exibir_ordens


@click.command("orders", help="Lista todas as ordens pendentes abertas, com detalhes.")
@click.version_option(package_name="mtcli-trade")
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo (opcional)")
def orders(symbol):
    """Lista todas as ordens pendentes (ou de um símbolo)"""
    ordens = obter_ordens_pendentes(symbol)
    exibir_ordens(ordens, symbol)


if __name__ == "__main__":
    orders()
