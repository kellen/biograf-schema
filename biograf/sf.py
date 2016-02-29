#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import datetime

domain = "http://www.sf.se"
movieurl = "%(domain)s/UserControls/Booking/SelectShow/ShowList.control?MoviePageId=%(movie)s&SelectedDate=%(date)s&CityId=%(city)s"
imdburl = "http://www.imdb.com/find?q=%(title)s"

def get_schedule(city, days):
    """
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    soup = fetch_base(city)
    city = get_city(soup)
    cinemas = get_cinemas(soup)
    movies = get_movies(soup)

    schedule = []
    for day in range(days):
        date = datetime.datetime.now() + datetime.timedelta(days=day)
        schedules = []
        for id,title in movies.items():
            schedules = schedules + fetch_schedule(date.strftime("%Y%m%d"), city, id, title)
        schedule.append(schedules)
    return schedule

def fetch_base(city):
    url = "%(domain)s/?city=%(city)s" % {"domain": domain, "city": city}
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')

def get_cinemas(soup):
    patt = re.compile("TheatreId=([0-9]*)")
    cinemas = soup.find(id="ChooseCinema").find(id="ChooseMovieMenu").select("li a")
    ret = {}
    for cinema in cinemas:
        href = cinema["href"]
        match = patt.search(href)
        if match:
            id = match.group(1)
            ret[id] = cinema.get_text()
        else:
            print "no match on", str(cinema)
    return ret

def get_movies(soup):
    patt = re.compile("MoviePageId=([0-9]*)")
    movies = soup.find(id="ChooseMovie").find(id="ChooseMovieMenu").select("li a")
    ret = {}
    for movie in movies:
        href = movie["href"]
        match = patt.search(href)
        if match:
            id = match.group(1)
            ret[id] = movie.get_text()
        else:
            print "no match on", str(movie)
    return ret

def get_city(soup):
    return soup.find(id="CurrentPageMetaData").select("input[id=CityId]")[0]["value"] # e.g. "ma" for malmö

infomap = {"mv_txt": "TXT", "mv_sv": "SV", "mv_notxt": "NOTXT", "mv_3d": "3D"}
def fetch_schedule(date, city, movie, title):
    vals = {"domain": domain, "date": date, "city": city, "movie": movie}
    url = movieurl % vals
    r = requests.get(url)

    if re.match("MessageAnnatDatum", r.text):
        return [] # no showings on this date

    # split on each cinema
    anchor = '<li class="cmil_header">'
    start = 0
    idx = r.text.find(anchor, start)
    chunks = []
    while idx != -1:
        chunks.append(r.text[start:idx])
        start = idx + 1
        idx = r.text.find(anchor, start)
    chunks.append(r.text[start:idx]) # the rest
    chunks = chunks[1:] # discard leading text

    showings = []
    for chunk in chunks:
        soup = BeautifulSoup(chunk, 'html.parser')
        cinema = soup.select(".cmil_theatre")[0].get_text()
        salon = soup.select(".cmil_salong")[0].get_text()

        # split on each showing at the current cinema
        for showing in soup.select(".selectShowRow"):
            schedule = {
                "title": title,
                "time": showing.select(".cmil_time")[0].get_text(),
                "cinema": cinema,
                "salon": salon,
                "link": showing.select(".cmil_btn a")[0]["href"],
                "info": []
                }
            infos = showing.select(".cmil_versions div")
            for info in infos:
                schedule["info"] = schedule["info"] + info["class"]
            schedule["info"] = [infomap[info] for info in schedule["info"] if info in infomap]
            schedule["info"] = " ".join(schedule["info"])
            if schedule["time"]:
                schedule["datetime"] = time.strptime(schedule["time"], "%H:%M")
            schedule["imdb"] = imdburl % schedule
            showings.append(schedule)
    return showings

