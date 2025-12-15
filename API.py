import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
from api_tokens import API_KEY


def news(request):
    m = str(int(datetime.today().strftime("%m")) - 1)
    today = str(datetime.today().strftime(f'%Y-{m}-%d'))
    url = f"https://newsapi.org/v2/everything?q={request}&from={today}&sortBy=publishedAt&apiKey={API_KEY}"
    news_data = requests.get(url).json()
    try:
        if len(news_data['articles']) == 0:
            return "По вашему запросу ничего не найдено"
        else:
            r = random.randint(0,len(news_data['articles'])-1)
            author = news_data['articles'][r]['author']
            title = news_data['articles'][r]['title']
            description = news_data['articles'][r]['description']
            new_url = news_data['articles'][r]['url']

            return f'НОВОСТЬ ПО ЗАПРОСУ {request} \n\nАВТОР СТАТЬИ: {author} \n\n{title} \n\n{description} \n\nСсылка на статью: {new_url}'
    except:
        return 'Непредвиденная ошибка'


def get_random_image():
    response = requests.get('https://www.anekdot.ru/random/mem/')
    soup = BeautifulSoup(response.content, 'html.parser')
    image_element = soup.select('.topicbox img')[0]
    image_url = image_element['src']
    return image_url

def currencies():
    BTC = requests.get(
        'https://www.blockchain.com/ru/ticker').json()
    dataNatVal = requests.get(
        'https://www.cbr-xml-daily.ru/daily_json.js').json()
    USD = str(round(dataNatVal['Valute']['USD']['Previous'], 2))
    EUR = str(round(dataNatVal['Valute']['EUR']['Previous'], 2))
    KZT = str(round(dataNatVal['Valute']['KZT']['Previous'] / 100, 2))
    BYN = str(round(dataNatVal['Valute']['BYN']['Previous'], 2))
    btcRate = BTC['USD']
    btcRate = btcRate['last']
    return f'$ USD: {USD} руб \n€ EUR: {EUR} руб \n₿ BTC: {btcRate} USD\n₸  KZT: {KZT} руб\nB BYN: {BYN} руб'



def fact():
    data = requests.get('https://uselessfacts.jsph.pl/api/v2/facts/random').json()
    text = str(data['text'])
    return text


def weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
    try:
        weather_data = requests.get(url).json()
        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])
        wind_speed = round(weather_data['wind']['speed'])
        pressure = round(weather_data['main']['pressure'])
        deg = round((weather_data['wind']['deg'])/45)
        description = weather_data['weather'][0]['description']
        humidity = round(weather_data['main']['humidity'])

        if deg == 0:
            way = "С"
        elif deg == 1:
            way = "СВ"
        elif deg == 2:
            way = "В"
        elif deg == 3:
            way = "ЮВ"
        elif deg == 4:
            way = "Ю"
        elif deg == 5:
            way = "ЮЗ"
        elif deg == 6:
            way = "З"
        elif deg == 7:
            way = "СЗ"
        
        return f"{city}\n\n1. Температура: {str(temperature)}°C, Ощущается как: {str(temperature_feels)}°C\n2. Погода: {str(description)}\n3. Влажность: {str(humidity)} г/м³\n4. Скорость ветра: {str(wind_speed)} м/c, Направление: {str(way)}\n5. Давление: {str(round(pressure/1.33322,0))} мм. рт. ст. / {str(pressure)} мбар"
    except:
        return "Извините, такого города нет"
