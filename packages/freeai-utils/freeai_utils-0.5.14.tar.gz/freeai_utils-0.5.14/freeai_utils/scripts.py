# Contains standalone scripts for quick-support tasks; not for modular reuse.

from .geminiAPI import GeminiClient
from .cleaner import Cleaner
import pyautogui
import keyboard
import time
import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the full path for the screenshot
screenshot_path = os.path.join(script_dir, "screenshot.png")

def screenshot_ask_and_answer_clip(secret_key_for_gemini : str = None, hotkey_asking : str = "`", hotkey_stopping : str = "esc"):
    print("""
          Note: Use '`' (or any key you have configured) to take screenshot and get code answer.
                Use 'esc' to stop the program. 
          """)
    search = False
    active = True
    def screenshot():
        nonlocal search
        pyautogui.screenshot(screenshot_path)
        search = True
    def stop_script():
        nonlocal active
        active = False
        
    if secret_key_for_gemini is None:
        print("Require secret key for gemini api")
        return
    
    client = GeminiClient(model_name="models/gemini-2.5-flash-lite",api_key=secret_key_for_gemini)
    keyboard.add_hotkey(hotkey_asking, screenshot)
    keyboard.add_hotkey(hotkey_stopping, stop_script)
    while active:
        if search:
            client.ask_and_copy_to_clipboard("The attached image contains a programming problem. Write the complete code solution to the problem. Do not provide any explanations, descriptions, or extra text. Only provide the code and nothing else.", screenshot_path)
            search = False
            cleaner = Cleaner()
            cleaner.remove_all_files_end_with(".png")
        time.sleep(0.2)