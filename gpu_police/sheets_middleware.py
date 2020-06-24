from pathlib import Path

import gspread

from gpu_police.config import config

gc = gspread.service_account(Path(config.whitelist.credentials).expanduser())

def _get_values(sheet, query):
    sh = gc.open(config.whitelist.table_name)
    return sh.worksheet(sheet).get(query)

def get_whitelist():
    result = []
    for item in config.whitelist.queries.values():
        result += _get_values(item.sheet, item.query)
    result = [i[0] for i in result if i]
    return result
