# Robot Arm Controller

A Raspberry Pi robot arm controller that reads an NRL draw CSV, finds the next upcoming game, and moves the arm to the corresponding position when a button is pressed.

---

## Hardware Requirements

- Raspberry Pi Zero WH (or any Pi with GPIO)
- SCServo-compatible servo arm connected via USB serial
- Momentary push button

### Button Wiring

| Button pin | Pi physical pin | Notes |
|---|---|---|
| Signal | Pin 11 (GPIO17) | |
| Ground | Pin 6 (GND) | |

### Servo Connection

Connect the servo controller via USB. The default serial port is:

```
/dev/serial/by-id/usb-1a86_USB_Single_Serial_5A68008715-if00
```

Verify it appears on your Pi with:

```bash
ls /dev/serial/by-id/
```

If the path differs, update `MOTOR_PORT` in `systemd/robot-arm.service`.

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd robotics-dev
```

### 2. Run the installer

```bash
chmod +x scripts/install_linux_service.sh
sudo scripts/install_linux_service.sh
```

The installer:
- Creates a `.venv` virtual environment in the repo root
- Installs packages from `requirements.txt`
- Registers and starts a `systemd` service named `robot-arm`

---

## Configuration

Default values are pre-configured for the standard hardware setup. Override them by editing `systemd/robot-arm.service` before running the installer.

| Variable | Default | Description |
|---|---|---|
| `MOTOR_PORT` | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5A68008715-if00` | Serial port for the servo controller |
| `MOTOR_IDS` | `1,2,3,4,5` | Comma-separated servo motor IDs |
| `MOTOR_BAUDRATE` | `1000000` | Serial baudrate |
| `BUTTON_GPIO_PIN` | `17` | GPIO pin number for the button |

---

## Manual Test (without service)

To run directly without installing the service:

```bash
.venv/bin/python -m robot_arm.main
```

---

## Service Management

```bash
# Check status
sudo systemctl status robot-arm

# View logs
journalctl -u robot-arm -f

# Restart
sudo systemctl restart robot-arm

# Stop
sudo systemctl stop robot-arm
```

---

## How It Works

1. On startup the arm moves to the base (neutral) position.
2. The service polls for a button press on GPIO17.
3. On press, it reads `draw.csv` to find the next upcoming game by date.
4. It moves the arm to the positions defined in that row's column 4.
5. An emphasis gesture is performed (joint 4 pulses 3×).
6. After 1 second the arm returns to the base position.

