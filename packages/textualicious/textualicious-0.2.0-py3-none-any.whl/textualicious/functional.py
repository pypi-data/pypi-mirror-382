from __future__ import annotations

from typing import TYPE_CHECKING

from textual.screen import Screen


if TYPE_CHECKING:
    import os

    from textual.app import ComposeResult
    from textual.widget import Widget


def show_path(path: str | os.PathLike[str]) -> None:
    """Show the contents of a path in a UniversalDirectoryTree widget."""
    from upath import UPath

    from textualicious.upath_tree import UniversalDirectoryTree

    path_obj = UPath(path)
    widget = UniversalDirectoryTree(path_obj)
    show(widget)


def show(widget: Widget | Screen):
    """Show given widget inside an App."""
    from textual.app import App
    from textual.widgets import Footer, Header

    class DemoApp(App):
        """Demo app showing the UniversalDirectoryTree widget."""

        def compose(self) -> ComposeResult:
            yield Header()
            if isinstance(widget, Screen):
                self.app.push_screen(widget)
            else:
                yield widget
            yield Footer()

    app = DemoApp()
    app.run()


if __name__ == "__main__":
    show_path(".")
