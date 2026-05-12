"""User input helpers for robot controls."""

from __future__ import annotations

import os

try:
    from gpiozero import Button
except ImportError:  # pragma: no cover - optional hardware dependency
    Button = None


_button: Button | None = None
_button_init_failed = False


def button_pressed() -> bool:
    """Return True when the configured button input is active.

    Configure BUTTON_GPIO_PIN to override the GPIO pin wired to the physical
    button. If gpiozero is unavailable, the button is treated as inactive.
    """

    global _button, _button_init_failed

    pin_value = os.getenv("BUTTON_GPIO_PIN", "17")
    if Button is None or _button_init_failed:
        return False

    if _button is None:
        try:
            _button = Button(int(pin_value), pull_up=True, bounce_time=0.05)
        except Exception as exc:  # pragma: no cover - hardware/runtime specific
            _button_init_failed = True
            print(f"Button init failed on GPIO{pin_value}: {exc}")
            return False

    pressed = _button.is_pressed
    if pressed:
        print("Button Pressed")
    return pressed
