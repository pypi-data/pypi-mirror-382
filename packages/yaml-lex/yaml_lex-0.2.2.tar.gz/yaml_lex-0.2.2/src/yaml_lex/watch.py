import logging
import time
from pathlib import Path

import click
from rich import print
from rich.progress import track
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .format import format_yaml_file


class Watcher:
    """Monitors a directory for filesystem events and triggers a handler.

    Args:
        directory (str): Path to the directory to watch.
        handler (FileSystemEventHandler): Event handler to process events.
    """

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        """Start watching the directory indefinitely until interrupted."""
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except Exception:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class ModifyStatuteHandler(FileSystemEventHandler):
    """Handles file modifications for statutes, updating content as needed."""

    file_cache: dict = {}

    def on_modified(self, event):
        """Triggered when a file is modified. Updates markdown files accordingly."""
        if event.is_directory:
            return

        # ensure existence
        p = Path(event.src_path)  # type: ignore
        if not p.exists():
            print(f"{p.name=} missing, may have been renamed")
            return

        if not event.src_path.endswith(".yml"):  # type: ignore
            return

        # Deal with caching issues
        seconds = int(time.time())
        key = (seconds, event.src_path)
        if key in self.file_cache:
            return
        self.file_cache[key] = True

        # Update file based on new content
        print(f"\nUpdating: {p.name=}")
        format_yaml_file(p)

    def on_any_event(self, event):
        print(event)  # Your code here
