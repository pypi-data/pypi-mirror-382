# Std
import sys
import time
import threading
from IPython.display import clear_output
import ipywidgets

# OMGUI
from omgui.spf import spf
from omgui.util.jupyter import nb_mode


class Spinner:
    """
    A simple spinner for terminal and Jupyter notebook.
    """

    frames_fancy: list[str] = [
        "▉▋▍▎▏▏",
        "▉▉▋▍▎▏",
        "▋▉▉▋▍▎",
        "▍▋▉▉▋▍",
        "▏▎▋▉▉▋",
        "▏▎▍▋▉▉",
        "▎▏▎▍▋▉",
        "▍▎▏▎▍▋",
        "▋▍▎▏▎▍",
    ]
    frames: list[str] = ["◢", "◣", "◤", "◥"]
    interval: float = 0.3
    text: str | None = None

    _running: bool = False
    _thread: threading.Thread | None = None
    _task: ipywidgets.Widget | None = None
    _widget: ipywidgets.Label | None = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __init__(
        self,
        frames: list[str] | None = None,
        interval: float | None = None,
    ):
        """
        Initializes the Spinner.
        """
        if frames:
            self.frames = frames
        if interval:
            self.interval = interval

        self._running = False
        self._thread = None
        self._task = None
        self._widget = ipywidgets.Label()

    def _animate(self):
        """
        The animation loop for terminal, running in a separate thread.
        """
        index = 0
        text = spf.produce(f" <soft>{self.text}...</soft>") if self.text else ""

        while self._running:
            sys.stdout.write(f"\r{self.frames[index]}{text}")
            sys.stdout.flush()
            index = (index + 1) % len(self.frames)
            time.sleep(self.interval)

        sys.stdout.write("\r \r")
        sys.stdout.flush()

    def _animate_jupyter_v1(self):
        """
        The animation loop for Jupyter Notebook, running in the main thread.
        """
        index = 0

        while self._running:
            clear_output(wait=True)
            text = (
                f"{self.frames[index]} {self.text}..."
                if self.text
                else self.frames[index]
            )
            print(text)
            index = (index + 1) % len(self.frames)
            time.sleep(self.interval)

        clear_output(wait=True)

    def _animate_jupyter(self):
        """
        The animation loop for Jupyter Notebook, running asynchronously.
        """
        index = 0

        def _update_spinner():
            nonlocal index
            if not self._running:
                return

            # Update the widget's value with the next frame and text
            if self.text:
                self._widget.value = f"{self.frames[index]} {self.text}..."
            else:
                self._widget.value = self.frames[index]

            index = (index + 1) % len(self.frames)
            # Schedule the next update
            time.sleep(self.interval)
            self._task = ipywidgets.interact_manual(_update_spinner)
            self._task.close()

        _update_spinner()

    def start(self, text: str | None = None, fancy: bool = False):
        """
        Starts the spinner animation in a new thread.
        """
        self.text = text
        if fancy:
            self.frames = self.frames_fancy
            self.interval = 0.1
        if not self._running:
            self._running = True
            if nb_mode():
                self._animate_jupyter()
            else:
                self._thread = threading.Thread(target=self._animate)
                self._thread.start()

    def stop(self):
        """
        Stops the spinner animation and cleans up the thread.
        """
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join()

    def countdown(
        self,
        seconds: int,
        msg: str = None,
        stop_msg: str = None,
    ) -> bool:
        """
        Spinner with countdown timer.

        Parameters
        ----------
        seconds : int
            Number of seconds to countdown from.
        msg : str, optional
            Message to display, with {sec} as placeholder for seconds.
        stop_msg : str, optional
            Message to display when countdown is complete,
            instead of stopping spinner.
        """

        msg = msg or "Waiting {sec} seconds before retrying"
        self.start(msg.format(sec=seconds))
        time.sleep(1)
        if seconds > 1:
            self.countdown(seconds - 1, msg, stop_msg)
        else:
            if stop_msg:
                self.start(stop_msg)
            else:
                self.stop()
            return True
