import pyautogui
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from snapqrpy.utils.logger import Logger

class DeviceController:
    def __init__(self):
        self.logger = Logger("DeviceController")
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
    def move_mouse(self, x: int, y: int):
        pyautogui.moveTo(x, y)
        
    def click_mouse(self, button: str = "left"):
        pyautogui.click(button=button)
        
    def type_text(self, text: str):
        pyautogui.typewrite(text)
        
    def press_key(self, key: str):
        pyautogui.press(key)
