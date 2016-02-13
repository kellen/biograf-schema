# sf-schema

Produces a no-bullshit version of SF Bio's showing times for an entire day in a given city.

To change to a different city, edit the `base` variable and give the correct city name (without öäå).


```
python schema.py sf.html
```

If running via cron, the "buy" links will not work unless the script is run after 7am since 
SF's booking system is "closed" during the night.
