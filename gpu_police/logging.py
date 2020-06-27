import re

from rich.console import Console
from rich.markup import escape

TIMESTAMP_REGEX = "\[\[[\d\.: ]+\]\]"

def get_console(out_file=None):
    return Console(log_path=False, width=125, highlight=False, tab_size=16, file=out_file, log_time_format="[%d.%m.%y %H:%M]")

def format_time(match):
    time = match.group(0)
    return f"[cyan]{time}[/]"

def format_keyword(match):
    keyword = match.group(0)
    return f"[bold red]{keyword}[/]"

def format_logs(text):
    text = escape(text)
    text = re.sub(TIMESTAMP_REGEX, format_time, text)
    for keyword in ["Killed:", "Reason:"]:
        text = re.sub(keyword, format_keyword, text)
    return text
