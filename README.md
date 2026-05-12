# Robotics Dev

This repository is the home for the robot arm controller.

## Install on Linux

1. Add your Python runtime dependencies to `requirements.txt`.
2. Make the installer executable: `chmod +x scripts/install_linux_service.sh`.
3. Run the installer: `scripts/install_linux_service.sh`.

The installer creates a repo-local virtual environment in `.venv`, installs the packages from `requirements.txt`, and registers a `systemd` service named `robot-arm` that runs `python -m robot_arm.main` from this repository.

Wire the button between physical pin 11 (GPIO17) and physical pin 6 (GND). The service defaults to GPIO17, and you can override that with `BUTTON_GPIO_PIN` if needed.

To drive servos with `scservo_sdk`, set these environment variables for the service:

- `MOTOR_PORT` (example: `/dev/ttyUSB0`)
- `MOTOR_IDS` as comma-separated IDs (example: `1,2,3,4,5,6`)
- `MOTOR_BAUDRATE` (default: `1000000`)
- `ROUND_MOVE_STEPS` (default: `50`)

On each button press, `main.py` calls `draw_parser.get_round()` and runs the matching movement profile.

## Service entry point

Replace the loop in `robot_arm/main.py` with your actual robot arm control logic.
