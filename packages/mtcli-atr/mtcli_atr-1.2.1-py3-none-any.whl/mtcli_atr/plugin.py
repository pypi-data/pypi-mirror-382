import click
from mtcli_atr.controllers.atr_controller import processar_atr
from mtcli_atr.views.atr_view import exibir_resultado_atr, exibir_erro
from mtcli_atr.conf import (
    SYMBOL,
    PERIOD,
    BARS,
)


@click.command(
    "atr", help="Exibe o indicador ATR (Average True Range) do ativo informado."
)
@click.version_option(package_name="mtcli-atr")
@click.option("--symbol", "-s", default=SYMBOL, help="Símbolo do ativo (default IBOV).")
@click.option(
    "--bars",
    "-b",
    "periodo",
    type=int,
    default=BARS,
    help="Período do ATR (default 14).",
)
@click.option(
    "--period", "-p", "timeframe", default=PERIOD, help="Timeframe (ex: M1, H1, D1)."
)
def atr(symbol, periodo, timeframe):
    """Exibe o indicador ATR (Average True Range)."""
    try:
        valor = processar_atr(symbol, periodo, timeframe)
        exibir_resultado_atr(symbol, periodo, timeframe, valor)
    except Exception as e:
        exibir_erro(str(e))


def register(cli):
    cli.add_command(atr)
