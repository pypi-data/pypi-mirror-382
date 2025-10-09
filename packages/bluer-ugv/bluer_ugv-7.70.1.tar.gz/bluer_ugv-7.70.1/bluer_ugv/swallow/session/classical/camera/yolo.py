from typing import List
import numpy as np

from bluer_options.timer import Timer
from bluer_options import string
from bluer_options import host
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects import storage
from bluer_objects.metadata import post_to_object, get_from_object
from bluer_sbc.imager.camera import instance as camera
from bluer_sbc.env import BLUER_SBC_CAMERA_WIDTH
from bluer_algo.yolo.dataset.classes import YoloDataset
from bluer_algo.yolo.model.predictor import YoloPredictor

from bluer_ugv import env
from bluer_ugv.swallow.session.classical.camera.generic import ClassicalCamera
from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.swallow.session.classical.mode import OperationMode
from bluer_ugv.logger import logger


class ClassicalYoloCamera(ClassicalCamera):
    def __init__(
        self,
        keyboard: ClassicalKeyboard,
        leds: ClassicalLeds,
        setpoint: ClassicalSetPoint,
        object_name: str,
    ):
        super().__init__(keyboard, leds, setpoint, object_name)

        self.prediction_timer = Timer(
            period=env.BLUER_UGV_CAMERA_ACTION_PERIOD,
            name="{}.prediction".format(self.__class__.__name__),
            log=True,
        )
        self.training_timer = Timer(
            period=env.BLUER_UGV_CAMERA_TRAINING_PERIOD,
            name="{}.training".format(self.__class__.__name__),
            log=True,
        )

        self.dataset = YoloDataset(
            object_name=self.object_name,
            create=True,
        )

        self.predictor = None

        self.action_enabled: bool = True

    def initialize(self) -> bool:
        if not super().initialize():
            return False

        if not storage.download(
            env.BLUER_UGV_SWALLOW_YOLO_MODEL,
            policy=DownloadPolicy.DOESNT_EXIST,
        ):
            return False

        success, self.predictor = YoloPredictor.load(
            object_name=env.BLUER_UGV_SWALLOW_YOLO_MODEL,
            image_size=BLUER_SBC_CAMERA_WIDTH,
        )
        return success

    def cleanup(self):
        super().cleanup()

        self.dataset.save(
            verbose=True,
        )

        if self.dataset.empty:
            return

        dataset_list: List[str] = get_from_object(
            object_name=env.BLUER_UGV_SWALLOW_YOLO_DATASET_LIST,
            key="dataset-list",
            default=[],
            download=True,
        )
        dataset_list.append(self.object_name)
        if not post_to_object(
            object_name=env.BLUER_UGV_SWALLOW_YOLO_DATASET_LIST,
            key="dataset-list",
            value=dataset_list,
            upload=True,
            verbose=True,
        ):
            logger.error("failed to add object to dataset list.")

    def update(self) -> bool:
        if not super().update():
            return False

        if self.keyboard.mode == OperationMode.ACTION:
            return self.update_action()

        if self.keyboard.mode == OperationMode.TRAINING:
            return self.update_training()

        return True

    def update_action(self) -> bool:
        if not self.prediction_timer.tick():
            return True

        self.action_enabled = not self.action_enabled
        if not self.action_enabled:
            self.setpoint.put(
                what="steering",
                value=0,
                log=True,
            )
            return True

        self.leds.flash("red")

        success, image = camera.capture(
            close_after=False,
            open_before=False,
            log=True,
        )
        if not success:
            return success

        success, metadata = self.predictor.predict(
            image=image,
            return_annotated_image=self.keyboard.debug_mode,
            annotated_image_scale=2,
        )
        if not success:
            return success

        if self.keyboard.debug_mode:
            if not self.send_debug_data(metadata["annotated_image"]):
                logger.warning("failed to send debug data.")

        if not metadata["detections"]:
            logger.info("no detections.")
            return True

        detection = metadata["detections"][0]
        logger.info("confidence: {:.2f}".format(detection["confidence"]))
        detection_x_center = (detection["bbox_xyxy"][0] + detection["bbox_xyxy"][2]) / 2
        if detection_x_center < image.shape[1] / 2:
            self.setpoint.put(
                what="steering",
                value=env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
                log=True,
            )
        else:
            self.setpoint.put(
                what="steering",
                value=-env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
                log=True,
            )

        return True

    def update_training(self) -> bool:
        if not (self.training_timer.tick() or self.keyboard.last_key != ""):
            return True

        self.leds.flash("red")

        filename = "{}.png".format(
            string.pretty_date(
                as_filename=True,
                unique=True,
            )
        )

        success, _ = camera.capture(
            close_after=False,
            open_before=False,
            object_name=self.object_name,
            filename=filename,
            log=True,
        )
        if not success:
            return success

        # TODO: dataset +=

        self.training_timer.reset()

        return True
