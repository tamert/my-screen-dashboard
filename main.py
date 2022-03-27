import requests
import json
import threading
from tkinter import Canvas, Tk, BOTH
from PIL import Image, ImageTk, ImageFont, ImageDraw
from datetime import date, datetime
import locale
import os
import math
import click
from colorama import Fore

locale.setlocale(locale.LC_ALL, 'tr_TR.utf-8')

window = Tk()
window.attributes('-fullscreen', True)
window.title("My Dashboard")
canvas = Canvas(window, bg='black', highlightthickness=0)
canvas.pack(fill=BOTH, expand=True)

size = 150
dir_path = os.path.dirname(os.path.realpath(__file__))


def get_crypto_prices():
    response = requests.get(
        "https://api2.binance.com/api/v3/ticker/24hr")
    prices = dict()
    data_from_json = response.json()
    for i in range(len(data_from_json)):
        symbol = data_from_json[i].get("symbol")
        last_price = data_from_json[i].get("lastPrice")
        if "BTCUSDT" == symbol:
            prices["btc"] = '{:20,.2f}'.format(math.ceil(float(last_price)))
        if "ETCUSDT" == symbol:
            prices["etc"] = '{:20,.2f}'.format(math.ceil(float(last_price)))

    return prices


def texts(width, draw, theme, config):
    with open(os.path.join(dir_path, "themes/%s.json" % theme), 'r+') as f:
        theme_data = json.load(f)
    padding = int(theme_data['padding'])
    font = ImageFont.truetype(os.path.join(dir_path, 'Pixellari.ttf'), size=size)
    content = date.today().strftime("%A")
    color = theme_data['colors']['primary']
    (x, y) = (int(theme_data['x']), padding)
    draw.text((x, y), content, color, font=font)

    font = ImageFont.truetype(os.path.join(dir_path, 'Pixellari.ttf'), size=size)
    content = "%s %s:%s:%s" % (
        date.today().strftime("%d %B %Y"), datetime.now().hour, datetime.now().minute, datetime.now().second)
    (x, y) = (int(theme_data['x']), (size * 1) + (padding * 1))
    draw.text((x, y), content, color, font=font)

    font = ImageFont.truetype(os.path.join(dir_path, 'Pixellari.ttf'), size=size)

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?q=%s,%s&units=%s&APPID=%s" % (
            config["city"], config["country_prefix"], config["units"], config["open_weather_map_api_key"]))

    json_response = json.loads(response.text)

    content = "%s`C  %s H" % (json_response["main"]["temp"], json_response["main"]["humidity"])
    color = theme_data['colors']['second']
    (x, y) = (int(theme_data['x']), (size * 2) + (padding * 6))
    draw.text((x, y), content, color, font=font)

    data = get_crypto_prices()

    color = theme_data['colors']['last']
    (x, y) = (int(theme_data['x']), (size * 4) + (padding * 7))
    draw.text((x, y), ("%s $" % (data["btc"])).strip(), color, font=font)

    (x, y) = (width / 2, (size * 4) + (padding * 7))
    draw.text((x, y), ("%s $" % (data["etc"])).strip(), color, font=font)

    font = ImageFont.truetype(os.path.join(dir_path, 'Pixellari.ttf'), size=75)
    (x, y) = (int(theme_data['x']), (size * 4) + (padding * 3))
    draw.text((x, y), "btc", color, font=font)

    (x, y) = (width / 2, (size * 4) + (padding * 3))
    draw.text((x, y), "etc", color, font=font)


def drawer(theme, config):
    print("drawing...")
    global bgg, resized, bg2

    bgg = Image.open(os.path.join(dir_path, "themes/%s.png" % theme))

    draw = ImageDraw.Draw(bgg)

    height = int("%s" % window.winfo_height())
    width = int("%s" % window.winfo_width())
    texts(window.winfo_screenwidth(), draw, theme, config)
    resized = bgg.resize((width, height), Image.ANTIALIAS)
    bg2 = ImageTk.PhotoImage(resized)
    canvas.create_image(0, 0, image=bg2, anchor='nw')


def resize_bg(events):
    print("resized")
    global bgg, resized, bg2
    height = events.height
    width = events.width
    resized = bgg.resize((width, height), Image.ANTIALIAS)
    bg2 = ImageTk.PhotoImage(resized)
    canvas.create_image(0, 0, image=bg2, anchor='nw')


def refresher(theme, config):
    drawer(theme, config)
    threading.Timer(10, refresher).start()


@click.group()
def cli():
    pass


@cli.command()
@click.option('--theme', '-t')
def start(theme):
    with open(os.path.join(dir_path, "config.json"), 'r+') as f:
        config = json.load(f)

    if theme is None:
        theme = config["default_theme"]
    window.bind("<Configure>", resize_bg)
    refresher(theme, config)
    window.mainloop()


if __name__ == '__main__':
    click.echo(Fore.LIGHTGREEN_EX + """
    SCREEN STARTING       Tamer Agaoglu
       """ + Fore.RESET)
    cli()
