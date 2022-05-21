import random
import threading

from kivy.core.window import Window
from kivy.uix.video import Video as kyVideoPlayer
import glob

from kivy.uix.widget import Widget


class VideoCountdown(kyVideoPlayer):
    def __init__(self,
                 root_widget: Widget,
                 trigger_callback,
                 video_folder="assets/FunnyVideos",
                 **kwargs):
        self.thread_lock = threading.Lock()
        self.trigger_callback = trigger_callback
        self.root = root_widget
        self.video_folder = video_folder
        super().__init__(
            source=self.get_random_video(),
            options={"eos": 'stop'},
            size=Window.size,
            **kwargs)
        self.allow_stretch = True
        self.bind(eos=self.on_eos_change)
        self.allow_fullscreen = True

    def start(self):
        self.thread_lock.acquire()
        self._do_video_load()
        self.seek(0)
        self.play = True
        self.root.add_widget(self)
        self.thread_lock.release()
        # and end callback

    def get_video_list(self):
        return glob.glob(f"{self.video_folder}/*")

    def get_random_video(self):
        vid_list = self.get_video_list()
        rand_vid = vid_list[random.randint(0, len(vid_list) -1)]
        return rand_vid

    def on_eos_change(self, inst, val):
        self.thread_lock.acquire()
        self.root.remove_widget(self)
        self.trigger_callback()
        self.thread_lock.release()

