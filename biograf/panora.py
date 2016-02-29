#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime

# TODO it seems like there should be some way to get the data as json from drupal rather than as a nested HTML snippet
url = "http://www.panora.se/views/ajax?view_name=screenings&view_display_id=sidebar&date[value][date]=%(date)s&event_date[value][date]=%(date)s"
imdburl = "http://www.imdb.com/find?q=%(title)s"

def get_schedule(city, days):
    """
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    if city != "malmo":
        return [[] for day in range(days)]

    schedules = []
    for day in range(days):
        date = datetime.datetime.now() + datetime.timedelta(days=day)
        r = requests.get(url % {"date": date.strftime("%Y-%m-%d")})
        json = r.json()
        soup = BeautifulSoup(json[1]["data"], 'html.parser')

        showings = []
        for showing in soup.select("article.views-row"):
            title_element = showing.select("h3.movie-sidebar-title a")[0]
            time_element = showing.select("span.time a")[0]
            schedule = {
                "title": title_element.get_text(),
                "time": time_element.get_text(),
                "cinema": "Panora",
                "salon": "--",
                "link": time_element["href"],
                "info": ""
                }
            if schedule["time"]:
                schedule["datetime"] = time.strptime(schedule["time"], "%H:%M")
            schedule["imdb"] = imdburl % schedule
            # alternate description url
            # "http://www.panora.se/%s" % title_element["href"],
            showings.append(schedule)
        schedules.append(showings)
    return schedules
