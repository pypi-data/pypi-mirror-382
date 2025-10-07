import os
from mtcli.conf import config


LOSS_LIMIT = float(
    os.getenv("LOSS_LIMIT", config["DEFAULT"].getfloat("loss_limit", fallback=-180.00))
)

STATUS_FILE = os.getenv(
    "STATUS_FILE",
    config["DEFAULT"].get("status_file", fallback="bloqueio.json"),
)
INTERVALO = int(
    os.getenv("INTERVALO", config["DEFAULT"].getint("intervalo", fallback=60))
)
