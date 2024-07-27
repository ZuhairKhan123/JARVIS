from datetime import datetime
import multiprocessing
from random import choice
import numpy as np
import sounddevice as sd
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Rotate, Rectangle, Color
from kivy.uix.image import Image
import speech_recognition as sr
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import time
from kivy.uix.textinput import TextInput
import threading
import keyboard
import pyttsx3
import pyautogui
import webbrowser
import os
import subprocess as sp
import pywhatkit
import wolframalpha
import imdb
import pprint
import requests
from conv import random_text
from multiprocessing.pool import ThreadPool
from deco_rator import *
from online import find_my_ip, youtube, search_on_google, search_on_wikipedia, send_email, get_news, weather_forecast

# Set the width and height of the screen
width, height = 1366, 700

# Configure the graphics settings
Config.set('graphics', 'width', width)
Config.set('graphics', 'height', height)
Config.set('graphics', 'fullscreen', 'True')

engine = pyttsx3.init('sapi5')
engine.setProperty('volume', 1.5)
engine.setProperty('rate', 220)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

@threaded      
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing....")
        queri = r.recognize_google(audio, language='en-in')
        print(queri)
        if 'stop' in queri or 'exit' in queri:
            hour = datetime.now().hour
            if hour >= 21 and hour < 6:
                speak("Good night sir, take care!")
            else:
                speak("Have a good day sir!")
            exit()
    except Exception:
        speak("Sorry I couldn't understand. Can you please repeat that?")
        queri = 'None'
    return queri

class RotatingButton(Button):
    def __init__(self, **kwargs):
        super(RotatingButton, self).__init__(**kwargs)
        self.angle = 2
        self.background_angle = 0

    def rotate_button(self, *args):
        self.background_angle += self.angle
        self.canvas.before.clear()
        with self.canvas.before:
            Rotate(angle=self.background_angle, origin=self.center)

class CircleWidget(Widget):
    def __init__(self, **kwargs):
        super(CircleWidget, self).__init__(**kwargs)
        self.volume = 0
        self.volume_history = [0,0,0,0,0,0,0]
        self.volume_history_size = 140
        self.min_size = .2 * width
        self.max_size = .7 * width
        
        self.add_widget(Image(source='border.eps.png', size=(width, height)))
        self.circle = RotatingButton(size=(284.0, 284.0), background_normal='circle.png')
        self.circle.bind(on_press=self.start_recording)
        self.add_widget(Image(source='jarvis.gif', size=(self.min_size, self.min_size), pos=(width / 2 - self.min_size / 2, height / 2 - self.min_size / 2)))

        time_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(300, 100), pos=(150, height - 150))
        self.time_label = Label(text='', font_size=24, markup=True, font_name='mw.ttf')
        time_layout.add_widget(self.time_label)
        self.add_widget(time_layout)
        Clock.schedule_interval(self.update_time, 1)

        self.title = Label(text='[b][color=3333ff]BY ZUHAIR KHAN[/color][/b]', font_size=42, markup=True, font_name='dusri.ttf', size_hint=(None, None), size=(600, 100), pos=(width / 2 - 300, height - 150))
        self.add_widget(self.title)

        self.subtitles_input = TextInput(
            text='Hey Zuhair! I am Jarvis, your personal assistant.',
            font_size=24,
            readonly=True,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(1200, 80),
            pos=(width / 2 - 300, 100),
            font_name='teesri.otf',
        )
        self.add_widget(self.subtitles_input)

        self.vrh = Label(text='', font_size=15, markup=True, font_name='mw.ttf', size_hint=(None, None), size=(300, 200), pos=(width - 400, height / 4))
        self.add_widget(self.vrh)

        self.vlh = Label(text='', font_size=15, markup=True, font_name='mw.ttf', size_hint=(None, None), size=(300, 200), pos=(100, height / 4))
        self.add_widget(self.vlh)

        self.add_widget(self.circle)
        keyboard.on_press_key('`', self.on_keyboard_down)

    def on_keyboard_down(self, event):
        if event.name == '`':
            self.start_recording()

    def start_recording(self, *args):
        threading.Thread(target=self.run_speech_recognition).start()

    def run_speech_recognition(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            audio = r.listen(source)
        query = r.recognize_google(audio, language="en-in")
        Clock.schedule_once(lambda dt: setattr(self.subtitles_input, 'text', query))
        CircleWidget.handle_jarvis_commands(query.lower())
        return query.lower()

    def update_time(self, dt):
        current_time = time.strftime('TIME\n\t%H:%M:%S')
        self.time_label.text = f'[b][color=3333ff]{current_time}[/color][/b]'

    def update_circle(self, dt):
        try:
            self.size_value = int(np.mean(self.volume_history))
        except Exception:
            self.size_value = self.min_size

        if self.size_value <= self.min_size:
            self.size_value = self.min_size
        elif self.size_value >= self.max_size:
            self.size_value = self.max_size

        self.circle.size = (self.size_value, self.size_value)
        self.circle.pos = (width / 2 - self.circle.width / 2, height / 2 - self.circle.height / 2)

    def update_volume(self, indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 100
        self.volume = volume_norm
        self.volume_history.append(volume_norm)
        self.vrh.text = f'[b][color=3333ff]{np.mean(self.volume_history)}[/color][/b]'
        self.vlh.text = f'''[b][color=3344ff]
            {round(self.volume_history[0], 7)}\n
            {round(self.volume_history[1], 7)}\n
            {round(self.volume_history[2], 7)}\n
            {round(self.volume_history[3], 7)}\n
            {round(self.volume_history[4], 7)}\n
            {round(self.volume_history[5], 7)}\n
            {round(self.volume_history[6], 7)}\n
            [/color][/b]'''
        if len(self.volume_history) > self.volume_history_size:
            self.volume_history.pop(0)

    def start_listening(self):
        self.stream = sd.InputStream(callback=self.update_volume)
        self.stream.start()

    @staticmethod
    def handle_jarvis_commands(query):
        try:
            if "how are you" in query:
                speak("I am fine how are you.")
            elif "open command prompt" in query:
                speak("Opening command prompt")
                os.system('start cmd')
            elif "open camera" in query:
                speak("Opening camera sir")
                sp.run('start microsoft.windows.camera:', shell=True)
            elif "open notepad" in query:
                speak("Opening Notepad for you sir.")
                os.system('start notepad')
            elif "search in wikipedia" in query:
                speak("Searching in Wikipedia")
                search_on_wikipedia(query)
            elif "search on google" in query:
                speak("Searching on Google")
                search_on_google(query)
            elif "search youtube" in query:
                speak("Searching on YouTube")
                youtube(query)
            elif "weather" in query:
                speak("Getting weather forecast")
                weather_forecast(query)
            elif "news" in query:
                speak("Getting news")
                get_news()
            elif "ip address" in query:
                speak("Finding your IP address")
                find_my_ip()
            elif "play" in query:
                speak("Playing song")
                pywhatkit.playonyt(query)
            elif "email" in query:
                speak("Sending email")
                send_email(query)
            elif "movie" in query:
                speak("Searching for movies")
                imdb.search_movie(query)
            elif "calculator" in query:
                speak("Opening calculator")
                os.system('start calc')
            elif "stop" in query or "exit" in query:
                hour = datetime.now().hour
                if hour >= 21 and hour < 6:
                    speak("Good night sir, take care!")
                else:
                    speak("Have a good day sir!")
                exit()
            else:
                speak("I didn't understand your command.")
        except Exception as e:
            print(f"Error: {e}")

class TestApp(App):
    def build(self):
        root = CircleWidget()
        root.start_listening()
        Clock.schedule_interval(root.update_circle, 0.1)
        return root

if __name__ == '__main__':
    TestApp().run()
