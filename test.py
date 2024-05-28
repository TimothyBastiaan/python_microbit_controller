import time
from pynput.keyboard import Key, Controller

keyboard_controller = Controller()

# Give yourself a few seconds to focus the browser or other application
time.sleep(10)  # Increase the time if needed

# Send keystrokes
keyboard_controller.type('Hello, Raspberry Pi!')
keyboard_controller.press(Key.enter)
keyboard_controller.release(Key.enter)