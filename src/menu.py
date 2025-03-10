from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from rich.console import Console
import os

console = Console()

# Menu options with icons
MENU_OPTIONS = [
    ("🎵", "Set Playlist URL"),
    ("🎼", "Set Number of Tracks"),
    ("📂", "Import Tracks"),
    ("📇", "Generate Cards"),
    ("🪵", "View Logs"),
    ("❓", "Help / Usage"),
    ("❌", "Quit")
]

style = Style.from_dict({
    "header": "bg:#61afef #282c34 bold",
    "menu": "bg:#4c566a #d8dee9",
    "menu-selected": "bg:#88c0d0 #2e3440 bold",
    "footer": "bg:#3b4252 #d8dee9",
    "default": "bg:#2e3440 #d8dee9",
})

def create_main_menu(app_state):
    """
    Left-aligned main menu. Returns an int (0..4) or "quit".
    """
    selected_index = [0]

    def render_header():
        return [
            ("class:header", "🌟 Hitsteripy 🌟\n"),
            ("class:header", "🎶 Spotify Track Manager 🎶\n"),
            ("class:header", "Use UP/DOWN to navigate, ENTER to select, ESC to quit.\n")
        ]

    def render_footer():
        """Render the footer with the playlist name, track count, and recent logs."""
        playlist_name = app_state.get("playlist_name", "No playlist selected")
        track_count = app_state.get("track_count", "N/A")  # might be 'all' or a number or None
        logs = app_state.get("logs", [])[-3:]  # Show last 3 logs

        footer_lines = [
            f"🎵 Playlist: {playlist_name}",
            f"🎼 Track Count: {track_count}",
        ] + logs

        return "\n".join(footer_lines)



    def render_menu():
        menu_content = []
        for i, (icon, option) in enumerate(MENU_OPTIONS):
            line = f"{icon} {option}"
            if i == selected_index[0]:
                menu_content.append(("class:menu-selected", line + "\n"))
            else:
                menu_content.append(("class:menu", line + "\n"))
        return menu_content

    def handle_enter():
        idx = selected_index[0]
        if idx == len(MENU_OPTIONS) - 1:  # Quit
            return "quit"
        return idx

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        selected_index[0] = (selected_index[0] - 1) % len(MENU_OPTIONS)

    @kb.add("down")
    def move_down(event):
        selected_index[0] = (selected_index[0] + 1) % len(MENU_OPTIONS)

    @kb.add("enter")
    def select_option(event):
        event.app.exit(result=handle_enter())

    @kb.add("escape")
    @kb.add("c-c")
    def exit_app(event):
        event.app.exit(result="quit")

    layout = Layout(
        HSplit([
            Window(FormattedTextControl(render_header), height=4, style="class:header"),
            Window(FormattedTextControl(render_menu), height=len(MENU_OPTIONS) + 2, style="class:menu"),
            Window(FormattedTextControl(render_footer), height=3, style="class:footer"),
        ])
    )

    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)
    return app.run()

def select_playlist(app_state, playlist_history):
    """
    Sub-menu to pick either "Enter new playlist URL" or reuse a previously stored dict:
      { "name": "MyPlaylist", "url": "https://spotify..." }
    Returns:
      dict {"name": "...", "url": "..."} OR None if user cancels (Esc).
    """
    options = ["Enter a new playlist URL"] + [p["name"] for p in playlist_history]
    selected_index = [0]

    def render_menu():
        lines = []
        for i, opt in enumerate(options):
            text = opt
            if i == selected_index[0]:
                lines.append(("class:menu-selected", text + "\n"))
            else:
                lines.append(("class:menu", text + "\n"))
        return lines

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        selected_index[0] = (selected_index[0] - 1) % len(options)

    @kb.add("down")
    def move_down(event):
        selected_index[0] = (selected_index[0] + 1) % len(options)

    @kb.add("enter")
    def select_option(event):
        event.app.exit(result=selected_index[0])

    @kb.add("escape")
    @kb.add("c-c")
    def cancel(event):
        event.app.exit(result=None)

    layout = Layout(
        Window(FormattedTextControl(render_menu), height=len(options) + 2, style="class:menu")
    )
    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)
    choice = app.run()

    if choice is None:
        # user cancelled
        return None

    if choice == 0:
        # new playlist
        console.print("[bold cyan]Enter a new playlist URL:[/bold cyan]")
        user_url = console.input("> ").strip()
        if not user_url:
            return None
        return {"name": "Unknown", "url": user_url}
    else:
        # existing from history
        return playlist_history[choice - 1]

def select_track_count(app_state, track_count_history):
    """
    Sub-menu for picking or customizing track count.  We store track_count_history as strings or ints.
    Returns the chosen value (string or int) or None if canceled.
    """
    # Some default quick picks
    quick_picks = ["1", "10", "50", "100", "200", "all", "Custom"]
    selected_index = [0]

    def render_menu():
        lines = []
        for i, opt in enumerate(quick_picks):
            text = opt
            if i == selected_index[0]:
                lines.append(("class:menu-selected", text + "\n"))
            else:
                lines.append(("class:menu", text + "\n"))
        return lines

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        selected_index[0] = (selected_index[0] - 1) % len(quick_picks)

    @kb.add("down")
    def move_down(event):
        selected_index[0] = (selected_index[0] + 1) % len(quick_picks)

    @kb.add("enter")
    def select_option(event):
        event.app.exit(result=selected_index[0])

    @kb.add("escape")
    @kb.add("c-c")
    def cancel(event):
        event.app.exit(result=None)

    layout = Layout(
        Window(FormattedTextControl(render_menu), height=len(quick_picks) + 2, style="class:menu")
    )
    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)
    choice = app.run()

    if choice is None:
        # user canceled
        return None

    if quick_picks[choice].lower() == "custom":
        console.print("[bold cyan]Enter a custom number of tracks (or 'all'):[/bold cyan]")
        user_val = console.input("> ").strip()
        if not user_val:
            return None
        return user_val
    else:
        return quick_picks[choice]
    
def select_imported_csv_file():
    """
    Show a submenu listing all CSV files in 'imported_tracks'.
    Return the full path to the selected CSV file, or None if user cancels.
    """
    files = find_imported_csv_files()

    if not files:
        # No CSV files found
        return None

    selected_index = [0]
    options = [f[0] for f in files]  # The labels from the (label, path) pairs

    style = Style.from_dict({
        "menu": "bg:#4c566a #d8dee9",
        "menu-selected": "bg:#88c0d0 #2e3440 bold",
    })

    def render_menu():
        lines = []
        for i, opt in enumerate(options):
            if i == selected_index[0]:
                lines.append(("class:menu-selected", opt + "\n"))
            else:
                lines.append(("class:menu", opt + "\n"))
        return lines

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        selected_index[0] = (selected_index[0] - 1) % len(options)

    @kb.add("down")
    def move_down(event):
        selected_index[0] = (selected_index[0] + 1) % len(options)

    @kb.add("enter")
    def select_option(event):
        event.app.exit(result=selected_index[0])

    @kb.add("escape")
    @kb.add("c-c")
    def cancel(event):
        event.app.exit(result=None)

    layout = Layout(Window(FormattedTextControl(render_menu), style="class:menu"))
    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)
    choice = app.run()

    if choice is None:
        return None

    # Return the path of the chosen file
    chosen_label, chosen_path = files[choice]
    return chosen_path

def find_imported_csv_files():
    """
    Scan the 'imported_tracks' folder for any CSV files in subdirectories.
    Returns a list of tuples (label, csv_path), e.g.
      [
        ("20250310_183133_100 -> Metal  Death  Industrial  Progressive_tracks.csv",
         "imported_tracks/20250310_183133_100/Metal  Death  Industrial  Progressive_tracks.csv"),
        ...
      ]
    """
    base_dir = "imported_tracks"
    if not os.path.isdir(base_dir):
        return []

    results = []
    for subdir_name in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir_name)
        if not os.path.isdir(subdir_path):
            continue

        # Look for CSV files in this subdir
        for file_name in os.listdir(subdir_path):
            if file_name.lower().endswith(".csv"):
                csv_path = os.path.join(subdir_path, file_name)
                label = f"{subdir_name} -> {file_name}"
                results.append((label, csv_path))

    return results

