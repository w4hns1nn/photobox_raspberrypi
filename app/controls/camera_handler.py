import threading

try:
    import gphoto2 as gp
    camera_available = True
except:
    camera_available = False
    print("please install gphoto2 and libgphoto2")

import time
from PIL import Image
import io


class CameraHandler:
    """ uses libgphoto2 and gphoto2 to make a photo."""

    def __init__(self, photo_taken_callback):
        if camera_available:
            self.camera = self.init_camera()
        self.save_folder = "Images/"
        self.photo_taken_callback = photo_taken_callback

    def init_camera(self):
        """ method trys to init camera. If it fails we need to wait and show a mesage"""
        camera = gp.Camera()
        camera.init()
        return camera

    def _cam_take_photo(self):
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

    def _take_photo_async(self):
        start_time = time.time()
        try:
            img = self._cam_take_photo()
        except Exception as e:
            print("taking photo failed " + str(e))
            self.photo_taken_callback(None)
            return
        # save it
        imgname = f"{self.save_folder}{time.strftime('%H_%M_%S', time.localtime())}.jpg"
        img.save(imgname)
        print("taking photo took " + str(time.time() - start_time) + "s")
        self.photo_taken_callback(imgname)

    def _take_photo_fake_async(self):
        time.sleep(3)
        self.photo_taken_callback("dummy_test.jpg")

    def take_photo(self):
        photo_method = self._take_photo_async if camera_available else self._take_photo_fake_async
        # make photo asynchronous
        threading.Thread(target=photo_method).start()



