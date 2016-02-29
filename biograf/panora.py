#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime

from biograf.nutid import get_nutid_schedule

sv = " (Sv. txt)"
def get_schedule(city, days):
    """
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    if city != "malmo":
        return [[] for day in range(days)]
    schedules = get_nutid_schedule(days, "http://217.115.59.98", "Panora")
    for schedule in schedules:
        for s in schedule:
            if sv in s["title"]:
                s["info"] = "TXT"
                s["title"] = s["title"].replace(sv, "")
    return schedules
