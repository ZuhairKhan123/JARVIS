import pyttsx3
from decouple import config
from datetime import datetime
from conv import random_text
import speech_recognition as sr 
from random import choice
import keyboard
import subprocess as sp
import requests
import os
import imdb
import wolframalpha
from online import find_my_ip, search_on_google, search_on_wikipedia, youtube, send_email, get_news, weather_forecast

engine = pyttsx3.init('sapi5')
engine.setProperty('volume', 1.5)
engine.setProperty('rate', 225)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

USER = config('USER')
HOSTNAME = config('BOT')

def speak(text):
    engine.say(text)
    engine.runAndWait()

def greet_me():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good morning {USER}")
    elif 12 <= hour < 16:
        speak(f"Good afternoon {USER}")
    elif 16 <= hour < 24:
        speak(f"Good evening {USER}")
    speak(f"I am {HOSTNAME}. How can I help you today?")

listening = False

def start_listening():
    global listening
    listening = True
    print("Started listening")

def pause_listening():
    global listening
    listening = False
    print("Stopped listening")

keyboard.add_hotkey('ctrl+alt+z', start_listening)
keyboard.add_hotkey('ctrl+alt+x', pause_listening)

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
        print("Audio captured")

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"Recognized: {query}")
        if 'stop' not in query and 'exit' not in query:
            speak(choice(random_text))
        else:
            speak(f"See you later {USER}")
            global listening
            listening = False  # Stop listening if user says "stop" or "exit"
    except Exception as e:
        print(f"Exception: {e}")
        speak("Sorry, I was unable to understand. Can you repeat that?")
        query = 'None'
    return query

if __name__ == '__main__':
    greet_me()
    while True:
        if listening:
            query = take_command().lower()
            print(f"Query: {query}")  # Debug print
            if "how are you" in query:
                speak("I am absolutely fine. How about you?")
            elif "open command prompt" in query:
                speak("Opening Command Prompt")
                sp.run('start cmd', shell=True)
            elif "open slack" in query:
                speak('Opening Slack')
                slack_path = r"C:\Users\Zuhair\AppData\Local\slack\slack.exe"
                os.startfile(slack_path)
            elif "open word" in query:
                speak('Opening Word')
                word_path = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
                os.startfile(word_path)
            elif "open chrome" in query:
                speak('Opening Chrome')
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                os.startfile(chrome_path)
            elif "ip address" in query:
                ip_address = find_my_ip()
                speak(f"Your IP address is {ip_address}")
                print(f"Your IP address is {ip_address}")
            elif "open youtube" in query:
                speak("What would you like me to play?")
                video = take_command().lower()
                print(f"Video query: {video}")  # Debug print
                youtube(video)
            elif "open google" in query:
                speak(f"Sure, what would you like to search {USER}?")
                search_query = take_command().lower()
                print(f"Google search query: {search_query}")  # Debug print
                search_on_google(search_query)
            elif "wikipedia" in query:
                speak("What would you like to search on Wikipedia?")
                search = take_command().lower()
                print(f"Wikipedia search query: {search}")  # Debug print
                results = search_on_wikipedia(search)
                speak(f"According to Wikipedia, {results}")
                speak("I am also printing this on the screen")
                print(results)
            elif "send an email" in query:
                speak("Please type the email address you would like to send to?")
                receiver_add = input("Email Address: ")
                speak("What should be the email subject?")
                subject = take_command().capitalize()
                speak("And what will be your message?")
                message = take_command().capitalize()
                if send_email(receiver_add, subject, message):
                    speak(f"I have sent the email, {USER}")
                    print("Email Sent")
                else:
                    speak("Something went wrong. Please check the error logs")
            elif "give me news" in query:
                speak(f"I am reading the latest headline of today")
                speak(get_news())
                speak("You can also review it on the screen")
                print(*get_news(),sep='\n')
            elif "weather" in query:
                ip_address= find_my_ip()
                speak("Tell me the name of your city")
                city = input("City: ")
                weather,temp,feels_like = weather_forecast(city)
                speak(f"The current temperature is {temp}, but it feels like {feels_like}")
                speak(f"The weather report also talks about {weather}")
                speak("For your convenience, I am also printing it on the screen")
                print(f"Description:{weather}\n Temperature:{temp}\n Feels Like:{feels_like}")
            elif "movie" in query:
                movies_db = imdb.IMDb()
                speak("Please tell me the movie name: ")
                text = take_command()
                movies = movies_db.search_movie(text)
                speak("Searching for" + text)
                speak("I found these")
                for movie in movies:
                    title = movie.get("title", "Unknown Title")                    
                    year = movie.get("year","Unknown Title")
                    speak(f"{title}-{year}")
                    info = movie.movieID
                    movie_info = movies_db.get_movie(info)
                    rating = movie_info.get("rating", "No rating available")
                    cast = movie_info.get("cast", [])
                    actors = cast[0:5]
                    actor_names = ", ".join(str(actor) for actor in actors)
                    plot = movie_info.get('plot outline', 'Plot summary not available')
                    speak(f"{title} was released in {year} and has an IMDb rating of {rating}. It has a cast of {actor_names}. The plot summary is: {plot}")
                    print(f"{title} was released in {year} and has an IMDb rating of {rating}. It has a cast of {actor_names}. The plot summary is: {plot}")
            

            elif "calculate" in query:
                app_id = "238XH4-Q9JUEHKY7H"
                client = wolframalpha.Client(app_id)
                ind = query.lower().split().index("calculate")
                text = query.split()[ind + 1:]
                result = client.query(" ".join(text))
                try:
                    ans = next(result.results).text
                    speak("The answer is " + ans)
                    print("The answer is " + ans)
                except StopIteration:
                    speak("I couldn't find that. Please try again.")
                except Exception as e:
                    speak("An error occurred. Please try again.")
                    print(f"An error occurred: {e}")

            elif 'what' in query or 'who' in query or 'which' in query or 'when' in query:
                app_id = "238XH4-Q9JUEHKY7H"
                client = wolframalpha.Client(app_id)
                try:
                    ind = None
                    if 'what' in query.lower():
                        ind = query.lower().index('what')
                    elif 'who' in query.lower():
                        ind = query.lower().index('who')
                    elif 'when' in query.lower():
                        ind = query.lower().index('when')
                    elif 'which' in query.lower():
                        ind = query.lower().index('which')

                    if ind is not None:
                        text = query.split()[ind + 1:]
                        res = client.query(" ".join(text))
                        ans = next(res.results).text
                        speak("The answer is " + ans)
                        print("The answer is " + ans)
                    else:
                        speak("I couldn't find that. Please try again.")
                except StopIteration:
                    speak("I couldn't find that. Please try again.")
                except Exception as e:
                    speak("An error occurred. Please try again.")
                    print(f"An error occurred: {e}")
