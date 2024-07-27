import requests
import wikipedia
import pywhatkit as kit
import smtplib
from decouple import config
from email.message import EmailMessage


EMAIL = "contentsolutionsglobal@gmail.com"
PASSWORD = "Htconev@123"

def find_my_ip():
    ip_address = requests.get('https://api.ipify.org?format=json').json()
    return ip_address["ip"]

def search_on_wikipedia(query):
    results = wikipedia.summary(query, sentences = 2)
    return results

def search_on_google(query):
    kit.search(query)

def youtube(video):
    kit.playonyt(video)

def send_email(receiver_add, subject, message):
    try:
        email = EmailMessage()
        email['To'] = receiver_add
        email['Subject'] = subject
        email['From'] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(e)
        return False


def get_news():
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey=855a6324219a41c3a86910bc81e71fe3'
        response = requests.get(url)
        news_data = response.json()

        articles = news_data.get('articles')
        if not articles:
            return ["Sorry, I couldn't fetch the news at this moment."]

        news_headlines = [article['title'] for article in articles[:5]]  # Get top 5 news headlines
        return news_headlines
    except Exception as e:
        print(f"Error occurred: {e}")
        return ["Sorry, I couldn't fetch the news at this moment."]


def weather_forecast(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=f09c55cc39f3db26bff21fed23e6f7eb&units=metric"
        response = requests.get(url)
        weather_data = response.json()

        weather_description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        return weather_description, temp, feels_like
    except Exception as e:
        print(f"Error occurred: {e}")
        return None, None, None