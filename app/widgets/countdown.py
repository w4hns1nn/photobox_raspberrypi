import glob
import random

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image as kvImage


class Countdown:
    def __init__(self,
                 root_widget: Widget,
                 duration: float = 5,  # how long shall the countdown be?
                 steps: int = 5,  # how often is update triggered in duration period
                 trigger_callback=None,
                 ):
        self.root = root_widget
        self.trigger_callback = trigger_callback

        self.duration = duration
        self.steps = steps
        self.time_left = 0
        self.interval = self.duration / self.steps
        self.widget = None

    def _decrease_countdown(self):
        if self.time_left <= 0:
            if self.widget is not None:
                self.root.remove_widget(self.widget)
            if self.trigger_callback is not None:
                self.trigger_callback()
            return False  # this ends the interval

        self._update()
        self.time_left -= self.interval
        return True  # interval schedule continues

    def _update(self):
        """it must do something. Abstract method"""
        pass

    def start(self):
        self.root.add_widget(self.widget)
        self.time_left = self.duration - self.interval
        Clock.schedule_interval(lambda dt: self._decrease_countdown(), self.interval)


class LabelCountdown(Countdown):
    def __init__(self,
                 root_widget: Widget,
                 duration: float = 5,  # how long shall the countdown be?
                 steps: int = 5,  # how often is update triggered in duration period
                 trigger_callback=None,
                 ):
        super().__init__(root_widget,
                         trigger_callback=trigger_callback,
                         duration=duration,
                         steps=steps)
        self.root = root_widget
        self.widget = Label(
            text=str(self.duration),
            font_size=50,
            outline_color=[0, 0, 0],
            outline_width=2,
            color=[1, 1, 1, 0.9],
        )
        self.widget.opacity = 0.9

    def _update(self):
        self.widget.text = str(int(self.time_left))


class FlashCountdown(Countdown):
    def __init__(self, root_widget: Widget, duration=0.2, steps=10, **kwargs):
        super().__init__(root_widget, duration=0.5, steps=10, **kwargs)
        self.opacity = 1
        self.opacity_decrease = 1 / steps
        self.widget = kvImage(color=[1, 1, 1, self.opacity], size=Window.size)

    def _update(self):
        self.opacity -= self.opacity_decrease
        self.widget.color = [1, 1, 1, self.opacity]


