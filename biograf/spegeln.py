#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime
import re

from biograf.nutid import get_nutid_schedule

def get_schedule(city, days):
    """
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    if city != "malmo":
        return [[] for day in range(days)]
    schedules = get_nutid_schedule(days, "https://bokabiospegeln.com", "Spegeln")
    patt = re.compile("^((SALONG BAR DECO|NT|KONSERT|TEATER|CINEMATEKET): )", re.IGNORECASE)
    for schedule in schedules:
        for s in schedule:
            match = patt.match(s["title"])
            if match:
                s["title"] = s["title"][match.group(1):]
    return schedules
