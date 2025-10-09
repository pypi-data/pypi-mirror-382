import pyautogui
import time
import platform

from pynput.keyboard import Key, Controller
import tkinter as tk
from withworld.bufer import load_to_bufer


keyboard = Controller()



def paste(input):
    
    load_to_bufer(input)
    if platform.system() == "Windows":
        keyboard.press(Key.ctrl)
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release(Key.ctrl)
        time.sleep(0.5)
    else:
        keyboard.press(Key.cmd)   # для macOS
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release(Key.cmd)
        time.sleep(0.5)
    enter()   

def enter():
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    time.sleep(0.5)

def esc():
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    time.sleep(0.5)

def f12():
    keyboard.press(Key.f12)
    keyboard.release(Key.f12)
    time.sleep(0.5)

def tab():
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    time.sleep(0.5)

def close_tab():
    if platform.system() == "Windows":
        keyboard.press(Key.ctrl)
        keyboard.press('w')
        keyboard.release('w')
        keyboard.release(Key.ctrl)
        time.sleep(0.5)
    else:
        keyboard.press(Key.cmd)   # для macOS
        keyboard.press('w')
        keyboard.release('w')
        keyboard.release(Key.cmd)
        time.sleep(0.5)