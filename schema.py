#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import sys
import re
import datetime

domain = "http://www.sf.se"
base = "%(domain)s/?city=malmo" % {"domain": domain}
movieurl = "%(domain)s/UserControls/Booking/SelectShow/ShowList.control?MoviePageId=%(movie)s&SelectedDate=%(date)s&CityId=%(city)s"

def fetch_base():
    url = base
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
            print id, "->", ret[id]
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
            print id, "->", ret[id]
        else:
            print "no match on", str(movie)
    return ret

def get_city(soup):
    city = soup.find(id="CurrentPageMetaData").select("input[id=CityId]")[0]
    print str(city)
    print "city", "->", city["value"]
    return city["value"]

def get_schedule(date, city, movie):
    vals = {"domain": domain, "date": date, "city": city, "movie": movie}
    url = movieurl % vals
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: %s [outfile]" % sys.argv[0])
        sys.exit(1)

    outfile = sys.argv[1]
    try:
        soup = fetch_base()
        city = get_city(soup)
        cinemas = get_cinemas(soup)
        movies = get_movies(soup)
        date = datetime.datetime.now().strftime("%Y%d%m")
        schedules = []
        for movie in movies:
            schedule = get_schedule(date, city, movie)

    except requests.ConnectionError:
        sys.stderr.write("No connection")
        sys.exit(1)

if __name__ == '__main__':
    main()
