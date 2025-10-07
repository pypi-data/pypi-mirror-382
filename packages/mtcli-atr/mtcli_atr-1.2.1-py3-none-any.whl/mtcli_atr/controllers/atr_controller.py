import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from mtcli_atr.models.atr_model import calcular_atr

log = setup_logger()


def processar_atr(symbol, periodo, timeframe):
    conectar()

    tf = getattr(mt5, f"TIMEFRAME_{timeframe.upper()}", None)
    if tf is None:
        shutdown()
        raise ValueError(f"Timeframe inválido: {timeframe}")

    if not mt5.symbol_select(symbol, True):
        shutdown()
        raise RuntimeError(f"Erro ao selecionar símbolo {symbol}")

    rates = mt5.copy_rates_from_pos(symbol, tf, 0, periodo + 1)
    if rates is None or len(rates) < periodo + 1:
        shutdown()
        raise RuntimeError("Dados insuficientes para cálculo do ATR")

    valor_atr = calcular_atr(rates, periodo)
    shutdown()
    return valor_atr
