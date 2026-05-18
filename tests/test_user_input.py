from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import robot_arm.user_input as user_input


class FakeButton:
    instances: list["FakeButton"] = []

    def __init__(self, pin: int, pull_up: bool, bounce_time: float) -> None:
        self.pin = pin
        self.pull_up = pull_up
        self.bounce_time = bounce_time
        self.is_pressed = False
        self.instances.append(self)


class FailingButton:
    attempts = 0

    def __init__(self, pin: int, pull_up: bool, bounce_time: float) -> None:
        self.__class__.attempts += 1
        raise RuntimeError("GPIO unavailable")


class ButtonPressedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_button_class = user_input.Button
        self.reset_button_state()

    def tearDown(self) -> None:
        user_input.Button = self.original_button_class
        self.reset_button_state()

    def reset_button_state(self) -> None:
        user_input._button = None
        user_input._button_init_failed = False
        FakeButton.instances.clear()
        FailingButton.attempts = 0

    def test_returns_false_when_gpiozero_is_unavailable(self) -> None:
        user_input.Button = None

        self.assertFalse(user_input.button_pressed())

    def test_reads_configured_button_pin_and_pressed_state(self) -> None:
        user_input.Button = FakeButton

        with patch.dict(os.environ, {"BUTTON_GPIO_PIN": "22"}):
            self.assertFalse(user_input.button_pressed())
            button = FakeButton.instances[0]
            button.is_pressed = True

            self.assertTrue(user_input.button_pressed())

        self.assertEqual(button.pin, 22)
        self.assertTrue(button.pull_up)
        self.assertEqual(button.bounce_time, 0.05)

    def test_reuses_button_instance_between_polls(self) -> None:
        user_input.Button = FakeButton

        user_input.button_pressed()
        user_input.button_pressed()

        self.assertEqual(len(FakeButton.instances), 1)

    def test_init_failure_is_reported_once_then_treated_as_inactive(self) -> None:
        user_input.Button = FailingButton

        self.assertFalse(user_input.button_pressed())
        self.assertFalse(user_input.button_pressed())

        self.assertEqual(FailingButton.attempts, 1)


if __name__ == "__main__":
    unittest.main()
