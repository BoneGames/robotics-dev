"""Minimal SCServo control helpers for moving a robot arm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import scservo_sdk as scs

PROTOCOL_VERSION = 0

ADDR_TORQUE_ENABLE = 40
ADDR_GOAL_POSITION = 42
ADDR_PRESENT_POSITION = 56

LEN_TORQUE_ENABLE = 1
LEN_GOAL_POSITION = 2
LEN_PRESENT_POSITION = 2


def _pack_u16(value: int) -> list[int]:
    return [
        scs.SCS_LOBYTE(scs.SCS_LOWORD(value)),
        scs.SCS_HIBYTE(scs.SCS_LOWORD(value)),
    ]


@dataclass
class SCServoConfig:
    port: str
    motor_ids: list[int]
    baudrate: int = 1_000_000
    retries: int = 5


class SCServoArm:
    def __init__(self, config: SCServoConfig):
        self.config = config
        self.port_handler = scs.PortHandler(config.port)
        self.packet_handler = scs.PacketHandler(PROTOCOL_VERSION)
        self.connected = False

    def connect(self) -> None:
        if self.connected:
            return

        if not self.port_handler.openPort():
            raise OSError(f"Failed to open motor port: {self.config.port}")

        if not self.port_handler.setBaudRate(self.config.baudrate):
            self.port_handler.closePort()
            raise OSError(f"Failed to set baudrate: {self.config.baudrate}")

        self.connected = True

    def disconnect(self) -> None:
        if self.connected:
            self.port_handler.closePort()
            self.connected = False

    def enable_torque(self) -> None:
        self._sync_write(
            addr=ADDR_TORQUE_ENABLE,
            byte_len=LEN_TORQUE_ENABLE,
            payloads={motor_id: [1] for motor_id in self.config.motor_ids},
        )

    def read_positions(self) -> list[int]:
        group = scs.GroupSyncRead(
            self.port_handler,
            self.packet_handler,
            ADDR_PRESENT_POSITION,
            LEN_PRESENT_POSITION,
        )

        for motor_id in self.config.motor_ids:
            if not group.addParam(motor_id):
                raise ConnectionError(f"Failed to add motor id {motor_id} to sync read")

        for _ in range(self.config.retries):
            comm = group.txRxPacket()
            if comm == scs.COMM_SUCCESS:
                break
        else:
            raise ConnectionError(self.packet_handler.getTxRxResult(comm))

        values: list[int] = []
        for motor_id in self.config.motor_ids:
            values.append(
                group.getData(motor_id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
            )

        return values

    def write_goal_positions(self, positions: Iterable[int]) -> None:
        payloads = {
            motor_id: _pack_u16(int(position))
            for motor_id, position in zip(
                self.config.motor_ids, list(positions), strict=True
            )
        }
        self._sync_write(
            addr=ADDR_GOAL_POSITION,
            byte_len=LEN_GOAL_POSITION,
            payloads=payloads,
        )

    def move_by_steps(self, steps: int) -> list[int]:
        current = self.read_positions()
        targets = [position + steps for position in current]
        self.write_goal_positions(targets)
        return targets

    def _sync_write(
        self, addr: int, byte_len: int, payloads: dict[int, list[int]]
    ) -> None:
        group = scs.GroupSyncWrite(self.port_handler, self.packet_handler, addr, byte_len)

        for motor_id, payload in payloads.items():
            if not group.addParam(motor_id, payload):
                raise ConnectionError(
                    f"Failed to add motor id {motor_id} to sync write at address {addr}"
                )

        for _ in range(self.config.retries):
            comm = group.txPacket()
            if comm == scs.COMM_SUCCESS:
                break
        else:
            raise ConnectionError(self.packet_handler.getTxRxResult(comm))
