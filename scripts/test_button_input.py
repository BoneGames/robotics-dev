#!/usr/bin/env python3
"""Manual hardware test for the robot arm button input."""

from __future__ import annotations

import os
import time

from gpiozero import Button


def main() -> int:
    pin = int(os.getenv("BUTTON_GPIO_PIN", "17"))
    button = Button(pin, pull_up=True, bounce_time=0.05)
    was_pressed = button.is_pressed

    print(f"Testing button on GPIO{pin}. Press Ctrl+C to stop.")
    print(f"Initial state: {'pressed' if was_pressed else 'released'}")

    try:
        while True:
            pressed = button.is_pressed
            if pressed != was_pressed:
                print("Button pressed" if pressed else "Button released")
                was_pressed = pressed
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped button test.")
        return 0
    finally:
        button.close()


if __name__ == "__main__":
    raise SystemExit(main())
