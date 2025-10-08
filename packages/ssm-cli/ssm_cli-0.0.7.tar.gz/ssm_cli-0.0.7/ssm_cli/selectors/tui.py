import sys
import termios
import tty
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.style import StyleType

console = Console()

def getch():
    """Blocking read of a single character from stdin (arrow keys supported)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":  # Escape sequence (arrow keys)
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        else:
            return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class TableWithArrows(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selected_row = 0

    def up(self):
        if self._selected_row > 0:
            self._selected_row -= 1

    def down(self):
        if self._selected_row < len(self.rows) - 1:
            self._selected_row += 1

    def get_row_style(self, console: "Console", index: int) -> StyleType:
        style = super().get_row_style(console, index)
        if index == self._selected_row:
            style += console.get_style("on blue")
        return style

def select(instances: list):
    table = TableWithArrows(title="Instances")
    table.add_column("Id")
    table.add_column("Name")
    table.add_column("Ping")
    table.add_column("IP")
    for instance in instances:
        table.add_row(
            instance.id,
            instance.name,
            instance.ping,
            instance.ip,
        )

    with Live(table, console=console, auto_refresh=False) as live:
        while True:
            live.update(table, refresh=True)
            match getch():
                case "\x1b[A": # Up arrow
                    table.up()
                case "\x1b[B": # Down arrow
                    table.down()
                case "\x03":  # Ctrl+C
                    raise KeyboardInterrupt()
                case "\r" | "\n":  # Enter key (carriage return or newline)
                    break

    return instances[table._selected_row]
