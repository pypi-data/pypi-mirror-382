from mtcli_trade.commands.buy import buy
from mtcli_trade.commands.sell import sell
from mtcli_trade.commands.orders import orders
from mtcli_trade.commands.positions import positions
from mtcli_trade.commands.cancel import cancel
from mtcli_trade.commands.zera import zera

# from mtcli_trade.commands.trade import trade
# from mtcli_trade.commands.trade import trade


def register(cli):
    cli.add_command(buy)
    cli.add_command(sell)
    cli.add_command(orders)
    cli.add_command(positions)
    cli.add_command(cancel)
    cli.add_command(zera)
    # cli.add_command(trade)
