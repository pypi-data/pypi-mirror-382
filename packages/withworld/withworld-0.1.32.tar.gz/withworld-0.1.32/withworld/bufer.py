import tkinter as tk
import pyperclip

def get_bufer():
    text = pyperclip.paste()
    return text

def load_to_bufer(input):
    pyperclip.copy(input)