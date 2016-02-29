#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime

from biograf.nutid import get_nutid_schedule

def get_schedule(city, days):
    """
    returns a list of schedules indexed by days-from-now. today=0, tomorrow=1, etc
    """
    if city != "malmo":
        return [[] for day in range(days)]
    return get_nutid_schedule(days, "https://217.115.59.98")
