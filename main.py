import os
os.environ["KIVY_VIDEO"] = "ffpyplayer"

import kivy
from app import root
from kivy.core.window import Window

Window.set_title('photobox by w4hns1nn')

# Window.fullscreen = True
myapp = root.MyApp()
myapp.run()