import threading
import time
from PIL import Image
import io
from enum import Enum
import psutil

class GP2_STATES(Enum):
    IMPORT_OK= 0
    NO_MODULE = 1
    NO_CLAIM = 2


def import_gphoto2():
    try:
        global gp
        import gphoto2 as gp2
        gp = gp2
    except Exception as e:
        if "No module" in str(e):
            return GP2_STATES.NO_MODULE
        elif "[-53]" in str(e): 
            return GP2_STATES.NO_CLAIM
    return GP2_STATES.IMPORT_OK

def kill_gphoto2():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if "gphoto2" in proc.name():
            proc.kill()


class CameraHandler:
    """ uses libgphoto2 and gphoto2 to make a photo."""

    def __init__(self, photo_taken_callback):
        self.save_folder = "Images/"
        self.photo_taken_callback = photo_taken_callback
        self.camera = None
        
        self.connect_to_camera()


    def apply_camera_settings(self, settings_path):
        if self.args.config is not None:
            print('Setting config %s' % self.args.config)
            for c in self.args.config:
                cs = c.split("=")
                if len(cs) == 2:
                    self.set_config(cs[0], cs[1])
                else:
                    print('Invalid config value %s' % c)

    def set_config(self, name, value):
        try:
            config = self.camera.get_config()
            setting = config.get_child_by_name(name)
            setting_type = setting.get_type()
            if setting_type == gp.GP_WIDGET_RADIO \
                    or setting_type == gp.GP_WIDGET_MENU \
                    or setting_type == gp.GP_WIDGET_TEXT:
                try:
                    int_value = int(value)
                    count = setting.count_choices()
                    if int_value < 0 or int_value >= count:
                        print('Parameter out of range')
                        self.exit_gracefully()
                    choice = setting.get_choice(int_value)
                    setting.set_value(choice)
                except ValueError:
                    setting.set_value(value)
            elif setting_type == gp.GP_WIDGET_TOGGLE:
                setting.set_value(int(value))
            elif setting_type == gp.GP_WIDGET_RANGE:
                setting.set_value(float(value))
            else:
                # unhandled types (most don't make any sense to handle)
                # GP_WIDGET_SECTION, GP_WIDGET_WINDOW, GP_WIDGET_BUTTON, GP_WIDGET_DATE
                print('Unhandled setting type %s for %s=%s' % (setting_type, name, value))
                self.exit_gracefully()
            self.camera.set_config(config)
            print('Config set %s=%s' % (name, value))
        except gp.GPhoto2Error or ValueError:
            print('Config error for %s=%s' % (name, value))
            self.exit_gracefully()


    def connect_to_camera(self):
        """ method trys to init camera. If it fails we need to wait and show a mesage"""
        kill_gphoto2() # sometimes required
        import_gphoto2()
        
        try:
            self.camera = gp.Camera()
            self.camera.init()
            print('Connected to camera')
        except gp.GPhoto2Error as e:
            print(f"camera init failed {e}")
            self.camera = None
   
    def exit_gracefully(self, *_):
        if self.running:
            self.running = False
            print('Exiting...')
            if self.camera:
                self.disable_video()
                self.camera.exit()
                print('Closed camera connection')
            sys.exit(0)
   
   
    def _cam_take_photo(self):
        #self.camera.init()
        file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.camera,
            file_path.folder,
            file_path.name,
            gp.GP_FILE_TYPE_NORMAL)
        )
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        #self.camera.exit()
        return io.BytesIO(file_data)

    def capture_image(self):
        print('Capturing image')
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        # refresh images on camera
        self.camera.wait_for_event(1000)
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
        file_jpg = str(file_path.name).replace('.CR2', '.JPG')

        camera_file = self.camera.file_get(file_path.folder, file_jpg, gp.GP_FILE_TYPE_NORMAL)

        return camera_file


    def _take_photo_async(self):
        start_time = time.time()
        try:
            camera_file = self.capture_image()
            #img_bytes = self._cam_take_photo()
        except Exception as e:
            print("taking photo failed " + str(e))
            self.photo_taken_callback(None)
            return
        # save it
        imgname = f"{self.save_folder}{time.strftime('%H_%M_%S', time.localtime())}.jpg"
        print('Copying image to', imgname)
        camera_file.save(imgname)
        
        #img = Image.open(img_bytes)
        #imgname = f"{self.save_folder}{time.strftime('%H_%M_%S', time.localtime())}.jpg"
        #img.save(imgname)
        print("taking photo took " + str(time.time() - start_time) + "s")
        self.photo_taken_callback(imgname)

    def _take_photo_fake_async(self):
        time.sleep(3)
        self.photo_taken_callback("dummy_test.jpg")

    def take_photo(self):
        photo_method = self._take_photo_async if self.camera is not None else self._take_photo_fake_async
        # make photo asynchronous
        threading.Thread(target=photo_method).start()



