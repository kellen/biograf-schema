#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime

def get_nutid_schedule(days, domain):
    """
    Panora/Spegeln use "Nutid AB" software.
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    filmsurl = domain + "/chap/bookforestall/"
    infourl = domain + "/chap/ajax/getDaysForMovie"
    bookingurl = domain + "/chap/ajax/tomovie@salongnr=%(salon)s&tid=%(time)s&datum=%(date)s"
    imdburl = "http://www.imdb.com/find?q=%(title)s"

    r = requests.get(filmsurl)
    soup = BeautifulSoup(r.text, 'html.parser')

    schedules = {}
    for day in range(days):
        date = datetime.datetime.now() + datetime.timedelta(days=day)
        schedules[date.strftime("%Y-%m-%d")] = []

    movies = [movie["value"] for movie in soup.select("#current_movies input")]
    for movie in movies:
        r = requests.post(infourl, data={"movie": movie, "offset": 0})
        for showing in r.json():
            showdate = showing["Datum"]
            if showdate in schedules:
                schedule = {
                    "title": movie,
                    "time": showing["Tid"],
                    "cinema": "Spegeln",
                    "salon": showing["SalongNr"],
                    "info": "",
                    "date": showdate
                    }
                schedule["link"] = bookingurl % schedule
                if schedule["time"]:
                    schedule["datetime"] = time.strptime(schedule["time"], "%H:%M")
                schedule["imdb"] = imdburl % schedule
                schedules[showdate].append(schedule)
    return [x[1] for x in sorted(schedules.items(), key=lambda x: x[0])]
