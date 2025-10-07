"""Configuracoes do plugin."""

import os
from mtcli.conf import config


SYMBOL = os.getenv("SYMBOL", config["DEFAULT"].get("symbol", fallback="WIN$N"))
PERIOD = os.getenv("PERIOD", config["DEFAULT"].get("period", fallback="D1"))
BARS = int(os.getenv("BARS", config["DEFAULT"].getint("bars", fallback=14)))
DIGITOS = int(os.getenv("DIGITOS", config["DEFAULT"].getint("digitos", fallback=0)))
