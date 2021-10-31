'''
Basic Picture Viewer
====================

This simple image browser demonstrates the scatter widget. You should
see three framed photographs on a background. You can click and drag
the photos around, or multi-touch to drop a red dot to scale and rotate the
photos.

The photos are loaded from the local images directory, while the background
picture is from the data shipped with kivy in kivy/data/images/background.jpg.
The file pictures.kv describes the interface and the file shadow32.png is
the border to make the images look like framed photographs. Finally,
the file android.txt is used to package the application for use with the
Kivy Launcher Android application.

For Android devices, you can copy/paste this directory into
/sdcard/kivy/pictures on your Android device.

The images in the image directory are from the Internet Archive,
`https://archive.org/details/PublicDomainImages`, and are in the public
domain.

'''

import kivy
from kivy.uix.label import Label
from kivy.uix.videoplayer import VideoPlayer

kivy.require('1.0.6')

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
from kivy.core.window import Window
import time
from kivy.clock import Clock
from gpiozero import Button
from gpiozero import LED
import threading
import os
import subprocess
from PIL import Image
from kivy.uix.image import Image as kvImage
import gphoto2 as gp
import io

DURATION_OF_TAKE_PHOTO = 0.5
DURATION_OF_SHOW_TAKEN_PHOTO = 12
DURATION_DIASHOW = 3

photo_busy = False
event_rotate_picture = None

class myVideo(VideoPlayer):
    def __init__(self, finish_callback, **kwargs):
        super().__init__(**kwargs)
        self.finish_callback = finish_callback

    def _play_started(self, instance, value):
        start = max(0.01, self.duration - DURATION_OF_TAKE_PHOTO)
        Clock.schedule_once(lambda dt: self.finish_callback(), start)
        super()._play_started(instance, value)

class PicturesApp(App):

    def __init__(self, **kwargs):       
        # the root is created in pictures.kv
        super().__init__(**kwargs)
       
        # Make diashow based on taken pictures
        self.picture = None # The picture which is shown in fullscreen when idle
        global event_rotate_picture
        event_rotate_picture =  Clock.create_trigger(
            lambda dt: self.load_random_taken_photo(),
            timeout=DURATION_DIASHOW,
            interval=True
        )
        event_rotate_picture()
        # Countdown events
        # Before a photo is taken a countdown is shown as video or as 321 timer.
        # This is the media player init and text label init        
        self.countdown_vids = glob(join(dirname(__file__), 'FunnyVideos', '*'))
        self.video_countdown = None #
        self.count_down_label = None # 

        # define gpin listener button
        self.button = Button(26)
        self.button.when_pressed = self.take_photo_countdown
        
         # define cam
         
        self.camera = gp.Camera()
        self.camera.init()
        
        self.last_photo_taken = time.time()
        Clock.schedule_interval(self.keep_alive_interval, 30)
       
    
    def set_text(self, txt):
        if self.count_down_label is None:
            self.count_down_label = Label(
                text=txt,
                pos=(0.4, 0.5),
                font_size='200sp',
                outline_color=[0, 0, 0],
                outline_width=2,
                color=[1, 1, 1, 0.9],
            )
            self.root.add_widget(self.count_down_label)
        else:
            self.count_down_label.opacity = 0.9
            self.count_down_label.text = txt

    def hide_text(self):
        if self.count_down_label is not None:
            self.count_down_label.opacity=0.0

    def show_image(self, filename):
        #filename = "Images/15_14_25.jpg"
        print("show img " + filename)
    
        try:
            # load the image
            if self.picture is None:
                self.picture = kvImage(source=filename, size=Window.size)
                self.root.add_widget(self.picture)
            else:
                self.picture.source = filename
                self.picture.opacity = 1.0
        except Exception as e:
            Logger.exception('Pictures: Unable to load <%s>' % filename + str(e))

    def hide_image(self):
        try:
            if self.picture is not None:
                self.picture.opacity = 0.0
        except Exception as e:
            print("failed to hide image " + str(e))

    #def on_video_loaded(self, instance, duration):
    #    print("the duration of the video is")
    
    def show_video(self, filename, callback):
        try:
            self.hide_image()
            self.hide_text()

            # show video
            if self.video_countdown is None:
                self.video_countdown = myVideo(
                    finish_callback=callback,
                    #duration=callback,
                    source=filename, size=Window.size, state='play',
                    options={'allow_stretch': True}
                )
                
                
                self.root.add_widget(self.video_countdown)
            else:
                self.video_countdown.source = filename
                self.video_countdown.opacity = 0.0
                self.video_countdown.state = "play"
            print(self.video_countdown.duration) # returns -1 in the beginning.. needs further callback
        except Exception as e:
            print('Videos: Unable to load <%s>' % filename + str(e))


    def hide_video(self):
        try:
            if self.video_countdown is not None:
                self.video_countdown.opacity = 0.0
                #self.root.remove_widget(self.video_countdown)
                self.video_countdown = None
        except Exception as e:
            print("failed to hide video " + str(e))
            
    def load_random_taken_photo(self):
        taken_photos = glob(join(dirname(__file__), 'Images', '*'))

        # get any files into images directory
        filename = taken_photos[randint(0, len(taken_photos) - 1)]
        self.show_image(filename)

    def on_pause(self):
        return True

    def take_photo_video_countdown(self):
        filename = self.countdown_vids[randint(0, len(self.countdown_vids) - 1)]
        self.show_video(filename, self.take_photo_threaded)

    def photo_is_processed(self):
        # hide video
        self.hide_video()
        # hide countdown label
        self.hide_text()
        # show loading image
        self.show_image("Icons/loading.jpg")

    def take_photo_321_countdown(self):
        # show countdown
        countdown_steps = 5
        def sched(t, st):
            Clock.schedule_once(lambda dt: self.set_text(str(t)), st)
        
        for i in range(countdown_steps, 0, -1):
            start = countdown_steps - i + 0.001
            sched(str(i), start)
        
        # cam has 2 sec delay approximately thats why we start directly
        start = max(0.01, countdown_steps - DURATION_OF_TAKE_PHOTO)
        Clock.schedule_once(lambda dt: self.take_photo_threaded(), start)
        
    def take_photo_countdown(self, dt):
        # prevent other take photo events
        global photo_busy
        if photo_busy:
            print("photo busy")
            return
        photo_busy = True
        # remove image rotation event
        global event_rotate_picture
        event_rotate_picture.cancel()
   
        # make a countdown for image capture
        if randint(0, 100) <= 50:
            self.take_photo_video_countdown()
        else:
            self.take_photo_321_countdown()

    def take_photo_threaded(self):
        threading.Thread(target=self.take_photo).start()
        Clock.schedule_once(lambda dt: self.photo_is_processed(), DURATION_OF_TAKE_PHOTO)

    def keep_alive_interval(self, dt):
        global photo_busy
        if time.time() - self.last_photo_taken >= 180:
            photo_busy = True
            self.cam_take_photo()
            self.take_photo_finished(1)

    def take_photo_finished(self, dt):
        def make_not_busy(dt):
            global photo_busy
            global event_rotate_picture
            event_rotate_picture()
            photo_busy = False

        global event_rotate_picture
        event_rotate_picture.cancel()
        Clock.schedule_once(make_not_busy, DURATION_DIASHOW)
      
    def cam_take_photo(self):
        self.last_photo_taken = time.time()
        file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.camera,
            file_path.folder,
            file_path.name,
            gp.GP_FILE_TYPE_NORMAL)
        )
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
    
        self.camera.exit()
        
        return Image.open(io.BytesIO(file_data))
      
    def take_photo(self):
        try:
            imgname = time.strftime("%H_%M_%S", time.localtime()) + ".jpg"
            target_cam = "CameraPhotos/" + imgname
            target_prev = "Images/" + imgname
            print("take photo " + target_cam)
            
            start = time.time()
            img = self.cam_take_photo()
            img.save(target_cam)
            # create a preview
            img = img.resize((img.size[0]//2, img.size[1]//2))
            img.save(target_prev)
            # show the preview
            Clock.schedule_once(lambda dt: self.show_image(target_prev), 0.01)
            duration = time.time() - start
            print("taking photo took " + str(duration) + "s")
            
        except Exception as e:
            print("saving preview or sheduling it failed " + str(e))
            
        # show images
        Clock.schedule_once(
            self.take_photo_finished,
            DURATION_OF_SHOW_TAKEN_PHOTO - DURATION_DIASHOW
        )
        
        
            
    def build(self):
        self.load_random_taken_photo()

if __name__ == '__main__':
    Window.fullscreen = True
    PicturesApp().run()