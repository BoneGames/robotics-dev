"""Entry point for the robot arm controller service."""

from __future__ import annotations

import signal
import time

from robot_arm.arm_runner import indicate_position, move_to_base_position, shutdown_arm
from robot_arm.draw_parser import get_round
from robot_arm.robot_vision import get_positions
from robot_arm.user_input import button_pressed

BUTTON_POLL_INTERVAL_SECONDS = 0.05


def main() -> int:
    
    running = True

    def handle_shutdown(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    move_to_base_position()

    previous_pressed = False

    while running:
        pressed = button_pressed()
        if pressed and not previous_pressed:
            round_number = get_round()
            positions = get_positions(round_number)
            indicate_position(positions)
            move_to_base_position()
        previous_pressed = pressed
        time.sleep(BUTTON_POLL_INTERVAL_SECONDS)

    shutdown_arm()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
