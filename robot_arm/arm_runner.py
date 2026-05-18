"""High-level round execution for the SCServo robot arm."""

from __future__ import annotations

import os
import time

from robot_arm.gestures import Gestures
from robot_arm.robot_vision import get_base_positions
from robot_arm.scservo_controller import SCServoArm, SCServoConfig

DEFAULT_MOTOR_PORT = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5A68008715-if00"
DEFAULT_MOTOR_IDS = "1,2,3,4,5"

_arm: SCServoArm | None = None
_gestures: Gestures | None = None


def _parse_motor_ids(raw_ids: str) -> list[int]:
    return [int(item.strip()) for item in raw_ids.split(",") if item.strip()]


def _parse_optional_int(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return None
    return int(raw)


def _get_arm() -> SCServoArm | None:
    global _arm

    if _arm is not None:
        return _arm

    motor_port = os.getenv("MOTOR_PORT", DEFAULT_MOTOR_PORT)
    motor_ids_raw = os.getenv("MOTOR_IDS", DEFAULT_MOTOR_IDS)

    config = SCServoConfig(
        port=motor_port,
        motor_ids=_parse_motor_ids(motor_ids_raw),
        baudrate=int(os.getenv("MOTOR_BAUDRATE", "1000000")),
        move_time=_parse_optional_int("MOTOR_MOVE_TIME"),
        move_speed=_parse_optional_int("MOTOR_MOVE_SPEED"),
    )

    _arm = SCServoArm(config)
    _arm.connect()
    _arm.enable_torque()
    return _arm


def _get_gestures(arm: SCServoArm) -> Gestures:
    global _gestures

    if _gestures is None:
        _gestures = Gestures(arm)

    return _gestures


def _wait_for_targets(
    arm: SCServoArm,
    targets: list[int],
    timeout_seconds: float = 4.0,
    tolerance_ticks: int = 30,
    poll_interval_seconds: float = 0.05,
) -> bool:
    """Wait until motors are near target positions or timeout occurs."""

    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        current = arm.read_positions()
        if len(current) != len(targets):
            return False

        if all(abs(actual - target) <= tolerance_ticks for actual, target in zip(current, targets)):
            return True

        time.sleep(poll_interval_seconds)

    return False


def indicate_position(positions: list[int]) -> None:
    """Move arm to the provided positions and perform the gesture."""

    arm = _get_arm()
    if arm is None:
        print("Position indication requested, but MOTOR_IDS is not configured")
        return

    targets = positions
    arm.write_goal_positions(targets)
    print(f"Sent move to targets: {targets}")

    arrived = _wait_for_targets(arm, targets)
    if not arrived:
        print("Target move timed out; continuing with gesture")

    _get_gestures(arm).emphasize_point()
    print("Completed emphasis gesture")


def move_to_base_position() -> None:
    """Move the arm to base pose."""

    arm = _get_arm()
    if arm is None:
        print("Startup base move skipped, MOTOR_IDS is not configured")
        return

    _get_gestures(arm).snap_finger()

    base_positions = get_base_positions()
    arm.write_goal_positions(base_positions)
    print(f"Moved to startup base position: {base_positions}")


def shutdown_arm() -> None:
    global _arm, _gestures

    if _arm is not None:
        _arm.disconnect()
        _arm = None
    _gestures = None
