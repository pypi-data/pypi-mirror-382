from datetime import datetime
from io import BytesIO
from urllib import request

import cv2
import keras
import numpy as np
import tensorflow as tf
from fastcs.attributes import AttrR
from fastcs.controller import Controller
from fastcs.datatypes import Int
from fastcs.wrappers import command

# 20250929_122040_epoch100_binary_batch4.keras is 1/5 scaled image!

image_divider = 5


class GoniOwlController(Controller):
    status = AttrR(Int())

    def __init__(self):
        self.log_path = "GoniOwl_binary_controller.log"
        with open(self.log_path, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - INFO - GoniOwl binary controller started.\n")
        self.model_name = (
            "/workspaces/fastcs-goniowl/20250929_122040_epoch100_binary_batch4.keras"
        )
        self.model = keras.models.load_model(self.model_name)

        with open(self.log_path, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"{timestamp} - INFO - Model {self.model_name} loaded successfully.\n"
            )
        self.model.summary()
        self.classes = ["pinoff", "pinon"]
        super().__init__()

    def urltoimage(self, url):
        self.resp = request.urlopen(url)
        self.image = np.asarray(bytearray(self.resp.read()), dtype="uint8")
        self.image = cv2.imdecode(self.image, cv2.IMREAD_COLOR)
        self.image = self.image[100:-100, 100:-100]
        cv2.imwrite("tmp.jpg", self.image)
        _, buffer = cv2.imencode(".jpg", self.image)
        io_buf = BytesIO(buffer.tobytes())
        return io_buf

    def is_image_valid(self, img, low_thresh=20, high_thresh=235):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)
        if mean_intensity < low_thresh or mean_intensity > high_thresh:
            print(f"Image rejected: mean intensity {mean_intensity:.2f}")
            return False
        return True

    def infer(self):
        self.stream = self.urltoimage(
            "http://bl23i-di-serv-04.diamond.ac.uk:8080/ECAM6.mjpg.jpg"
        )
        self.stream.seek(0)
        img_bytes = self.stream.read()
        img_tensor = tf.image.decode_image(img_bytes, channels=3)
        img_height, img_width = int(img_tensor.shape[0]), int(img_tensor.shape[1])
        self.stream.seek(0)
        self.img_in = keras.preprocessing.image.load_img(
            (self.stream),
            target_size=(
                int(img_height / image_divider),
                int(img_width / image_divider),
            ),
        )
        self.img_array = keras.preprocessing.image.img_to_array(self.img_in)
        if not self.is_image_valid(self.img_array.astype(np.uint8)):
            self.predicted_label = "invalid"
            self.score = 0.0
            self.printscore()
            return 3
        self.img_array = tf.expand_dims(self.img_array, 0)
        self.predictions = self.model.predict(self.img_array, verbose=0)
        self.score = self.predictions[0]

        if self.score < 0.15:
            print(f"{self.score} is {self.classes[0]}")
            self.predicted_label = self.classes[0]
            self.score = 1 - self.score
            self.printscore()
            return 1
        elif self.score > 0.85:
            print(f"{self.score} is {self.classes[1]}")
            self.predicted_label = self.classes[1]
            self.printscore()
            return 2
        else:
            print(f"{self.score} is unknown")
            self.predicted_label = "unknown"
            self.printscore()
            return 3

    def printscore(self):
        rounded_score = np.round((self.score * 100), 3)
        msg = f"Status is {self.predicted_label} with {str(rounded_score)} % conf."
        print(msg)

        with open(self.log_path, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - INFO - {msg}\n")

    @command()
    async def infer_pin(self) -> None:
        await self.status.set(self.infer())
