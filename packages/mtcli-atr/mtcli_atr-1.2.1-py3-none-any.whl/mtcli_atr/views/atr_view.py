import click
from mtcli.logger import setup_logger
from mtcli_atr.conf import DIGITOS

log = setup_logger()


def exibir_resultado_atr(symbol, periodo, timeframe, valor):
    msg = f"ATR({periodo}) de {symbol} no timeframe {timeframe.upper()}: {valor:.{DIGITOS}f}"
    click.echo(msg)
    log.info(msg)


def exibir_erro(msg):
    click.echo(f"Erro: {msg}")
    log.error(msg)
