import os

from mtcli.conf import config

SYMBOL = os.getenv("SYMBOL", config["DEFAULT"].get("symbol", fallback="WINV25"))
LOT = float(os.getenv("LOT", config["DEFAULT"].getfloat("lot", fallback=1.0)))
SL = float(os.getenv("SL", config["DEFAULT"].getfloat("sl", fallback=150)))
TP = float(os.getenv("TP", config["DEFAULT"].getfloat("tp", fallback=150)))
DIGITOS = int(os.getenv("DIGITOS", config["DEFAULT"].getint("digitos", fallback=0)))
LOSS_LIMIT = float(
    os.getenv("LOSS_LIMIT", config["DEFAULT"].getfloat("loss_limit", fallback=-180.00))
)
STATUS_FILE = os.getenv(
    "STATUS_FILE",
    config["DEFAULT"].get("status_file", fallback="bloqueio.json"),
)
