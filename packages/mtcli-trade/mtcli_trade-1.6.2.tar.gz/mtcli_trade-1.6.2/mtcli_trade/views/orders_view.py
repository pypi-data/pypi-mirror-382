import click


def exibir_ordens(ordens, symbol=None):
    if not ordens:
        click.echo(
            f"Nenhuma ordem pendente para {symbol}."
            if symbol
            else "Nenhuma ordem pendente encontrada."
        )
        return

    click.echo(f"Ordens pendentes{' para ' + symbol if symbol else ''}:\n")
    for o in ordens:
        click.echo(
            f"{o['tipo']} {o['symbol']} {o['volume']} {o['preco']} ticket {o['ticket']}"
        )
