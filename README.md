# biograf-schema

Produces a no-bullshit version of SF Bio's showing times for an entire day in a given city.

In Malmö also includes Biograf Spegeln and Panora.

Usage:

```
python -m biograf.schema city num-days outfile
```

`city` must be the GET parameter used on SF's homepage for a given city. It seems like this is just lowercase with öäå converted to o/a as appropriate. Malmö is `malmo`.

So, to fetch 2 days of the schedule for Malmö:

```
python -m biograf.schema malmo 2 schedule.html
```

If running via cron, the "buy" links will not work unless the script is run after 7am since 
SF's booking system is inexplicably "closed" during the night.
