import keyboard

from bluer_sbc.session.functions import reply_to_bash
from bluer_algo.socket.classes import DEV_HOST

from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.swallow.session.classical.mode import OperationMode
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv import env
from bluer_ugv.logger import logger

bash_keys = {
    "i": "exit",
    "o": "shutdown",
    "p": "reboot",
    "u": "update",
}


class ClassicalKeyboard:
    def __init__(
        self,
        leds: ClassicalLeds,
        setpoint: ClassicalSetPoint,
    ):
        logger.info(
            "{}: {}".format(
                self.__class__.__name__,
                ", ".join(
                    [f"{key}:{action}" for key, action in bash_keys.items()],
                ),
            )
        )

        self.leds = leds

        self.last_key: str = ""
        self.setpoint = setpoint

        self.mode = OperationMode.NONE

        self.debug_mode: bool = False

        self.special_key: bool = False

        self.ultrasound_enabled: bool = True

    def update(self) -> bool:
        self.last_key = ""

        mode = self.mode

        # bash keys
        if self.special_key:
            for key, event in bash_keys.items():
                if keyboard.is_pressed(key):
                    reply_to_bash(event)
                    return False

        # other keys
        for key, func in {
            " ": self.setpoint.stop,
            "x": self.setpoint.start,
            "s": lambda: self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") - 10,
            ),
            "w": lambda: self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") + 10,
            ),
        }.items():
            if keyboard.is_pressed(key):
                self.special_key = False
                func()

        # steering
        if keyboard.is_pressed("a"):
            self.special_key = False
            self.last_key = "a"
            self.setpoint.put(
                what="steering",
                value=env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
            )
        elif keyboard.is_pressed("d"):
            self.special_key = False
            self.last_key = "d"
            self.setpoint.put(
                what="steering",
                value=-env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
            )
        else:
            self.setpoint.put(
                what="steering",
                value=0,
                log=False,
            )

        # debug mode
        if keyboard.is_pressed("b"):
            self.special_key = False
            self.debug_mode = True
            logger.info(f'debug enabled, run "@swallow debug" on {DEV_HOST}.')

        if keyboard.is_pressed("v"):
            self.special_key = False
            self.debug_mode = False
            logger.info("debug disabled.")

        # mode
        if keyboard.is_pressed("y"):
            self.mode = OperationMode.NONE

        if keyboard.is_pressed("t"):
            self.mode = OperationMode.TRAINING

        if keyboard.is_pressed("g"):
            self.mode = OperationMode.ACTION

        if mode != self.mode:
            self.special_key = False
            logger.info("mode: {}.".format(self.mode.name.lower()))

        # ultrasound
        ultrasound_enabled = self.ultrasound_enabled
        if keyboard.is_pressed("n"):
            self.ultrasound_enabled = False

        if keyboard.is_pressed("m"):
            self.ultrasound_enabled = True

        if ultrasound_enabled != self.ultrasound_enabled:
            self.special_key = False
            logger.info(
                "ultrasound: {}.".format(
                    "enabled" if self.ultrasound_enabled else "disabled"
                )
            )

        # special key
        if keyboard.is_pressed("z") and not self.special_key:
            self.special_key = True
            logger.info("🪄 special key enabled.")

        if self.special_key:
            self.leds.flash_all()

        return True
