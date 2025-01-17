import configparser
import datetime
import getpass
import time
import json

import pylast
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init()

now = datetime.datetime.now()
unixtime = time.mktime(now.timetuple())

config = configparser.ConfigParser()
web_prompt = Fore.YELLOW + 'URL for BBC Sounds episode to scrobble: '
first_prompt = Fore.YELLOW + 'First track number: '
last_prompt = Fore.YELLOW + 'Last track number: '
pass_prompt = Fore.RED + 'Last.fm password: '


def find_tracklist(scripts):
    for script in soup("script"):
        text = script.text
        if 'window.__PRELOADED_STATE__'.lower() in text.lower():
            return text


def find_artists_and_tracks(tracklist_list):
    artists = []
    tracks = []
    lengths = []
    for item in tracklist_list:
        artists.append(item["titles"]["primary"])
        tracks.append(item["titles"]["secondary"])
        lengths.append(item["offset"]["end"]-item["offset"]["start"])
    return artists, tracks, lengths


if __name__ == "__main__":

    config.read('.details')

    API_KEY = config['API']['API_KEY']
    API_SECRET = config['API']['API_SECRET']
    username = " "
    username = config['LOGIN']['username']

    webpage = input(web_prompt)
    first = int(input(first_prompt))
    last = int(input(last_prompt))

    password_hash = pylast.md5(getpass.getpass(pass_prompt))
    print(Style.RESET_ALL)

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=username,
                                   password_hash=password_hash)
    print(Fore.LIGHTCYAN_EX + webpage)

    page = requests.get(str(webpage))
    print(page)
    print()

    soup = BeautifulSoup(page.content, 'html.parser')

    tracklist = find_tracklist(soup)
    tracklist = tracklist.strip('window.__PRELOADED_STATE__ = ')
    tracklist_json = json.loads(tracklist[:-1])
    tracklist_list = tracklist_json["tracklist"]["tracks"]

    artists, tracks, lengths = find_artists_and_tracks(tracklist_list[first-1:last][::-1])

    #artist_class_string = "sc-u-truncate gel-pica-bold gs-u-mb-- gs-u-pr-alt@m"
    #artists = soup.find_all("p", {"class": artist_class_string})

    #track_class_string = "sc-u-truncate gel-long-primer gs-u-pr-alt@m"
    #tracks = soup.find_all("p", {"class": track_class_string})

    for artist, track, length in zip(artists, tracks, lengths):
        scrobble_text = Fore.LIGHTYELLOW_EX + 'Scrobbling: '
        artist_text = Fore.LIGHTBLUE_EX + artist
        track_text = Fore.LIGHTGREEN_EX + track + Style.RESET_ALL
        separator = Fore.LIGHTMAGENTA_EX + " - "
        print(scrobble_text, artist_text, separator, track_text)
        unixtime -= length
        network.scrobble(artist, track, unixtime)

    print()
    print(Fore.LIGHTRED_EX + "Scrobbling complete")
    print()
