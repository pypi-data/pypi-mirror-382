from mtcli.logger import setup_logger

log = setup_logger()


def calcular_atr(rates, periodo):
    """Calcula o ATR (Average True Range)."""
    trs = []
    for i in range(1, len(rates)):
        high = rates[i]["high"]
        low = rates[i]["low"]
        prev_close = rates[i - 1]["close"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    if len(trs) < periodo:
        msg = f"Quantidade insuficiente de dados para período {periodo}"
        log.error(msg)
        raise ValueError(msg)

    return sum(trs[-periodo:]) / periodo
