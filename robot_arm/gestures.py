"""Gesture helpers for expressive robot arm motions."""

from __future__ import annotations

import time

from robot_arm.scservo_controller import SCServoArm


def _clamp_position(value: int) -> int:
    return max(0, min(4095, value))


class Gestures:
    """Gesture controller with internal robot arm state."""

    def __init__(self, arm: SCServoArm):
        self.arm = arm

    def emphasize_point(self) -> None:
        """Perform a short emphasis gesture from the current arm pose."""

        base_positions = self.arm.read_positions()
        if len(base_positions) < 3:
            return

        gesture_positions = list(base_positions)
        gesture_positions[2] = _clamp_position(gesture_positions[2] + 80)

        for pulse_index in range(3):
            self.arm.write_goal_positions(gesture_positions)
            time.sleep(0.25)
            if pulse_index < 2:
                self.arm.write_goal_positions(base_positions)
                time.sleep(0.25)
