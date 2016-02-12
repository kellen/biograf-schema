#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import sys
import re
import datetime
import time

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
            #print id, "->", ret[id]
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
            #print id, "->", ret[id]
        else:
            print "no match on", str(movie)
    return ret

def get_city(soup):
    city = soup.find(id="CurrentPageMetaData").select("input[id=CityId]")[0]
    #print "city", "->", city["value"]
    return city["value"]

infomap = {"mv_txt": "TXT", "mv_sv": "SV", "mv_notxt": "NOTXT", "mv_3d": "3D"}
def get_schedule(date, city, movie, title):
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

        for showing in soup.select(".selectShowRow"):
            schedule = {
                "title": title,
                "time": soup.select(".cmil_time")[0].get_text(),
                "cinema": cinema,
                "salon": salon,
                "link": soup.select(".cmil_btn a")[0]["href"],
                "info": []
                }
            infos = soup.select(".cmil_versions div")
            for info in infos:
                schedule["info"] + info["class"]
            schedule["info"] = [infomap[info] for info in schedule["info"] if info in infomap]
            schedule["info"] = " ".join(schedule["info"])
            if schedule["time"]:
                schedule["datetime"] = time.strptime(schedule["time"], "%H:%M")
            showings.append(schedule)
    return showings

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
        date = datetime.datetime.now().strftime("%Y%m%d")

        schedules = []
        for id,title in movies.items():
            schedules = schedules + get_schedule(date, city, id, title)
        schedules.sort(key=lambda x: x["datetime"])

        formatted = [u"<tr><td>%(time)s</td><td>%(title)s</td><td>%(cinema)s (%(salon)s)</td><td>%(info)s</td><td><a href=\"%(link)s\">buy</a></td></tr>" % s for s in schedules]
        out = u"\n".join(formatted).encode("utf-8")
        with open(outfile, 'w') as f:
            f.write("<html><head><title>SF improved</title><meta charset=\"UTF-8\"></head><body>\n")
            f.write("<table><tr><th>time</th><th>title</th><th>cinema</th><th>info</th><th>buy</th></tr>\n")
            f.write(out)
            f.write("\n</table></body></html>")

    except requests.ConnectionError:
        sys.stderr.write("No connection")
        sys.exit(1)

if __name__ == '__main__':
    main()
