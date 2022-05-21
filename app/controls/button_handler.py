from kivy.core.window import Window
try:
    from gpiozero import Button
    physical_button_available = True
except:
    print("no gpiozero support please install requirement and use e.g rasperry_pi")
    physical_button_available = False

class ButtonHandler:
    def __init__(self, button_pressed_event):
        self.button_pressed_event = button_pressed_event
        # real button event
        # define gpin listener button
        if physical_button_available:
            self.button = Button(26)
            self.button.when_pressed = button_pressed_event()
        # keyboard for physical button pressed emulatoin
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


    def _keyboard_closed(self):
        # self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        # self._keyboard = None
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':
            keyboard.release()
            self.button_pressed_event()
        return True
