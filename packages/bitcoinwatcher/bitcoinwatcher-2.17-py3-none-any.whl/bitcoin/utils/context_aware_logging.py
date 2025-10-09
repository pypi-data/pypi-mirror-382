import logging
import sys
from contextvars import ContextVar
from datetime import datetime
import colorlog

import pytz

logger = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.INFO)

class TimezoneFormatter(colorlog.ColoredFormatter):
    def __init__(self, fmt=None, datefmt=None, tz=None, log_colors=None):
        super().__init__(fmt, datefmt, log_colors=log_colors)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return f"\033[94m{s}\033[0m"  # Adding blue color to the date

formatter = TimezoneFormatter(
    ' %(asctime)s %(log_color)s%(levelname)s txid=%(tx_id)s tx_status=%(tx_status)s [%(module)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    tz=pytz.timezone('Asia/Kolkata'),
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)


ctx_tx = ContextVar('tx_id', default='')
ctx_tx_status = ContextVar('tx_status', default='')

class ExcludeModuleFilter(logging.Filter):
    def filter(self, record):
        return not (record.name.startswith('bitcoinlib.transactions') or record.name.startswith('bitcoinlib.scripts'))

class TXContextFilter(logging.Filter):

    def __init__(self):
        super().__init__()

    def filter(self, record):
        tx_id = ctx_tx.get()
        record.tx_id = tx_id
        tx_status = ctx_tx_status.get()
        record.tx_status = tx_status
        return True

ch = logging.StreamHandler(sys.stdout)
f = TXContextFilter()
ch.setFormatter(formatter)
ch.addFilter(f)
ch.addFilter(ExcludeModuleFilter())
root.addHandler(ch)

def get_logger(name):
    return logging.getLogger(name)