import os
os.environ["KIVY_VIDEO"] = "ffpyplayer"

import kivy
from app import root
from kivy.core.window import Window

a = kivy.kivy_options["video"]
b = a

# Window.fullscreen = True
myapp = root.MyApp()
myapp.run()