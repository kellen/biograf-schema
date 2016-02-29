#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import os
import sys
import datetime

import biograf.sf
import biograf.spegeln
import biograf.panora

def main():
    if len(sys.argv) < 4:
        sys.stderr.write("usage: %s city days outfile\n" % sys.argv[0])
        sys.stderr.write("city must be the `city` GET parameter given on the SF domain\n") # TODO ugh
        sys.exit(1)

    # TODO use optparse/whatever
    city = sys.argv[1]
    days = int(sys.argv[2])
    outfile = sys.argv[3]

    sources = [biograf.sf]
    if city in ["malmo"]:
        sources.append(biograf.spegeln)
        sources.append(biograf.panora)

    schedules_list = [mod.get_schedule(city, days) for mod in sources]
    schedules = schedules_list[0]
    for schedule_list in schedules_list[1:]:
        for idx,schedule in enumerate(schedule_list):
            schedules[idx].extend(schedule)

    try:
        top = """
            <!DOCTYPE html>
            <html>
              <head>
                <title>biografkalender</title>
                <meta charset=\"UTF-8\">
                <style type=\"text/css\">
                    th { text-align: left }
                    td { padding-right: 20px }
            </style>
            </head>
            <body>
            <h1>biografkalender</h1>
            """
        bottom = "</body></html>"
        tableheader = "<table>"
        tablefooter = "</table>"
        colheader = """<tr style="background-color: #CCCCCC"><th>time</th><th>title</th><th>cinema</th><th>salon</th><th>info</th><th>buy</th><th>description</th></tr>"""

        out =[]
        out.append(tableheader)
        for day in range(days):
            schedule = schedules[day]
            schedule.sort(key=lambda x: x["datetime"])

            date = datetime.datetime.now() + datetime.timedelta(days=day)
            datestr = date.strftime("%Y-%m-%d")
            if day == 0:
                datestr = datestr + " (today)"
            elif day == 1:
                datestr = datestr + " (tomorrow)"

            out.append("""<tr><th colspan="7" style="background-color: black; color: white"><b>%s</b></th></tr>""" % datestr)
            out.append(colheader)
            formatted = [u"<tr><td>%(time)s</td><td>%(title)s</td><td>%(cinema)s</td><td>%(salon)s</td><td>%(info)s</td><td><a href=\"%(link)s\">buy</a></td><td><a href=\"%(imdb)s\">imdb</a></tr>" % s for s in schedule]
            out.append(u"\n".join(formatted))
        out.append(tablefooter)

        with open(outfile, 'w') as f:
            f.write(top)
            f.write(u"\n".join(out).encode("utf-8"))
            f.write(bottom)
    except requests.ConnectionError:
        sys.stderr.write("No connection")
        sys.exit(1)

if __name__ == '__main__':
    main()
