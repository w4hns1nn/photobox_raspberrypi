import glob
import random
import threading

from kivy.core.window import Window
from kivy.uix.image import Image as kvImage
from kivy.clock import Clock
from kivy.uix.widget import Widget


class diashow:

    def __init__(self,
                 root_widget: Widget,
                 image_folder="Images",
                 diashow_interval_time=3
                 ):
        self.root_widget = root_widget
        self.img_path = image_folder
        self.thread_lock = threading.Lock()
        self.curr_img = self.next_img()
        self.diashow_interval = None
        self.diashow_interval_time = diashow_interval_time


    def get_img_list(self):
        return glob.glob(f"{self.img_path}/*.jpg") + glob.glob(f"{self.img_path}/*.png")

    def show_img(self, source):
        self.thread_lock.acquire()
        # remove prev image from root if existant
        if hasattr(self, 'curr_img') and self.curr_img is not None:
            self.root_widget.remove_widget(self.curr_img)

        self.curr_img = kvImage(source=source, size=Window.size, anim_delay=0, allow_stretch=True)
        # add to root
        self.root_widget.add_widget(self.curr_img)
        self.thread_lock.release()
        return self.curr_img

    def next_img(self):
        # load image from file
        img_list = self.get_img_list()
        rnd_img_idx = random.randint(0, len(img_list) - 1)
        rnd_img = img_list[rnd_img_idx]
        # show and add to root widget
        return self.show_img(rnd_img)

    def start_diashow(self):
        self.thread_lock.acquire()
        if self.diashow_interval is None:
            self.diashow_interval = Clock.schedule_interval(lambda dt: self.next_img(), self.diashow_interval_time)
        self.thread_lock.release()

    def stop_diashow(self):
        self.thread_lock.acquire()
        if self.diashow_interval is not None:
            self.diashow_interval.cancel()
            self.diashow_interval = None
        self.thread_lock.release()
