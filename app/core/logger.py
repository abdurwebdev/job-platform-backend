import logging

from app.core.request_context import request_id_ctx_var


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True


logging.basicConfig(
    level=logging.INFO,
)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(request_id)s | %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.addFilter(RequestIdFilter())

logger = logging.getLogger("app")
logger.handlers.clear()  # avoid duplicate handlers
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False
