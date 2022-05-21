import time

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
import random

from app.widgets.diashow import diashow
from app.widgets.countdown import LabelCountdown, FlashCountdown
from app.widgets.video_countdown import VideoCountdown
from app.controls.camera_handler import CameraHandler
from app.controls.button_handler import ButtonHandler

class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cameraHandler = CameraHandler(self.photo_taken)
        self.buttonHandler = ButtonHandler(self.button_pressed)
        # we use keyboard to trigger photo without the physical button pressed just for testing
        self.DURATION_TO_SHOW_TAKEN_PHOTO = 10
        self.DIASHOW_INTERVAL_TIME = 3

        self.PREVENT_BUTTON_PRESS = False

    def on_start(self):
        """ is called after built in kivy stack"""
        self.dia = diashow(self.root, diashow_interval_time=self.DIASHOW_INTERVAL_TIME)
        self.dia.start_diashow()

    def button_pressed(self):
        if self.PREVENT_BUTTON_PRESS:
            return

        self.PREVENT_BUTTON_PRESS = True
        # remove events
        self.dia.stop_diashow()

        # show a countdown
        countdown = random.choices(
            population=[
                LabelCountdown(self.root, duration=2, steps=2, trigger_callback=self.take_photo),
                VideoCountdown(self.root, trigger_callback=self.take_photo)
            ],
            weights=[0.1, 0.9],
            k=1
        )[0]
        countdown.start()

    def photo_taken(self, img_src: str):
        """ fires when a photo was made as callback"""
        # threading prevents from setting immediatly since we are not in the main thread. Workaround use clock
        Clock.schedule_once(lambda dt: self.dia.show_img(img_src), 0)
        # allow to take new photos by button press
        self.PREVENT_BUTTON_PRESS = False
        # wait some seconds before we continue with the diashow
        time.sleep(self.DURATION_TO_SHOW_TAKEN_PHOTO - self.DIASHOW_INTERVAL_TIME)
        Clock.schedule_once(lambda dt: self.dia.start_diashow(), 0)

    def take_photo(self):
        # stop concurrent processes
        self.dia.stop_diashow()
        # async make phote
        # self.cameraHandler.take_photo()
        self.cameraHandler.take_photo()
        # use a flash
        fc = FlashCountdown(root_widget=self.root)
        fc.start()
        # show a loading image while photo is not taken
        # rest ist handled in photo_taken method
        self.dia.show_img("assets/loading2.gif")

    def build(self):
        """
        here we return the root widget.
        decided to use a simple float layout to not have any restrictions.
        the root can be accessed via self.root later
        """
        return FloatLayout()


if __name__ == '__main__':
    MyApp().run()
