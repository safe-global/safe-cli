"""
Drive a Trezor emulator from trezor-user-env: start a model and firmware, set
the seed, and walk through confirmation screens over DebugLink.

The controller is a websocket on localhost:9001. The emulator wire and debug
links are UDP 21324 / 21325 on the host network, which is why the container
runs with `network_mode=host`. The controller `emulator-press-yes` command does
not confirm the screens, so the approver talks to DebugLink directly.
"""

import json
import threading
import time
from functools import cache
from typing import Any

from websockets.sync.client import connect

CONTROLLER_URL = "ws://127.0.0.1:9001"
EMULATOR_PATH = "udp:127.0.0.1:21324"
DEBUGLINK_PATH = "udp:127.0.0.1:21325"
MNEMONIC = " ".join(["all"] * 12)
LABEL = "safe-cli"


class Controller:
    def __init__(self) -> None:
        self.ws = connect(CONTROLLER_URL, max_size=None, open_timeout=30)
        self.welcome = json.loads(self.ws.recv(timeout=30))

    def cmd(self, **payload: Any) -> dict:
        self.ws.send(json.dumps(payload))
        while True:
            message = json.loads(self.ws.recv(timeout=120))
            if message.get("type") == "client":
                continue
            if not message.get("success", True):
                raise RuntimeError(f"{payload['type']}: {message}")
            return message

    def firmwares(self, model: str) -> list[str]:
        return list(self.welcome["firmwares"].get(model, []))

    def start_emulator(self, model: str, version: str, pin: str = "") -> None:
        """
        A wiped emulator of `model` running `version`, set up with the test seed,
        passphrase protection on and an optional PIN.
        """
        try:
            self.cmd(type="emulator-stop")
        except RuntimeError:
            pass
        self.cmd(type="emulator-start", model=model, version=version)
        self.cmd(
            type="emulator-setup",
            mnemonic=MNEMONIC,
            pin=pin,
            passphrase_protection=True,
            label=LABEL,
            needs_backup=False,
        )

    def close(self) -> None:
        self.ws.close()


# The emulator debug port answers one peer, so the approver thread and the PIN
# prompt share one DebugLink, used under this lock
DEBUGLINK_LOCK = threading.Lock()


@cache
def debuglink():
    from trezorlib.debuglink import DebugLink
    from trezorlib.transport import get_transport

    debug = DebugLink(get_transport(DEBUGLINK_PATH))
    debug.open()
    return debug


def encode_pin(pin: str) -> str:
    """
    :return: the PIN as the positions of the scrambled matrix the emulator shows
    """
    with DEBUGLINK_LOCK:
        return debuglink().encode_pin(pin)


class TrezorApprover(threading.Thread):
    """
    Confirms whatever the emulator shows, through DebugLink, until stopped.

    Screens with several pages are advanced with a swipe (touch models) or the
    right button (Model One). A screen that does not move on is the final
    confirmation and gets a hold. Passphrase keyboards get `passphrase` typed
    in. Every distinct screen is recorded. The Model One firmware exposes no
    layout text, so for it the approver only presses yes.
    """

    def __init__(self, touch: bool, passphrase: str = "") -> None:
        super().__init__(daemon=True)
        self.touch = touch
        self.passphrase = passphrase
        self.stop_event = threading.Event()
        self.seen: list[tuple[str, str]] = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_exc):
        self.stop_event.set()
        self.join(timeout=10)

    def run(self) -> None:
        debug = debuglink()
        previous = None
        while not self.stop_event.is_set():
            try:
                with DEBUGLINK_LOCK:
                    layout = debug.read_layout()
                current = (layout.title(), layout.text_content())
            except Exception:
                time.sleep(0.3)
                continue
            if current[1] == LABEL and not current[0]:  # home screen
                previous = None
                time.sleep(0.3)
                continue
            if current not in self.seen:
                self.seen.append(current)
            try:
                with DEBUGLINK_LOCK:
                    self.act(debug, current, previous)
            except Exception:
                pass
            previous = current
            time.sleep(0.8)

    def act(self, debug, current: tuple[str, str], previous) -> None:
        title, text = current
        if "passphrase" in (title + text).lower() and self.passphrase:
            debug.input(self.passphrase)
            debug.press_yes(wait=False)
        elif current == previous:
            debug.press_yes(hold_ms=1500, wait=False)
        elif self.touch:
            debug.swipe_up(wait=False)
        else:
            debug.press_yes(wait=False)

    def saw(self, fragment: str) -> bool:
        return any(fragment in title or fragment in text for title, text in self.seen)

    def dump(self) -> str:
        return "\n".join(f"{title} | {text}" for title, text in self.seen)
