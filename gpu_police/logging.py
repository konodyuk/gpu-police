from rich.console import Console

def get_console(out_file=None):
    return Console(log_path=False, width=120, highlight=False, tab_size=16, file=out_file)

def format_entries(entries):
    for i, entry in enumerate(entries):
        date, sep, body = entry.partition(' ')
        date = f"[cyan][{date}][/]"
        for keyword in ["Killed:", "Reason:"]:
            body = body.replace(keyword, f"[bold red]{keyword}[/]")
        entries[i] = date + sep + body
    return "\n\n".join(entries)
