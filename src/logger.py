from rich.console import Console

console = Console()

def append_log(app_state, level, message):
    """
    Appends a log entry to app_state's logs list, with a level and message.
    """
    entry = f"[{level.upper()}] {message}"
    app_state["logs"].append(entry)

def log_info(app_state, message):
    append_log(app_state, "info", message)
    console.log(f"[cyan][INFO][/cyan] {message}")

def log_error(app_state, message):
    append_log(app_state, "error", message)
    console.log(f"[red][ERROR][/red] {message}")

def log_success(app_state, message):
    append_log(app_state, "success", message)
    console.log(f"[green][SUCCESS][/green] {message}")
