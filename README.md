<div style="user-select: none;" align="center">
    
![Ephemeris Logo](https://github.com/user-attachments/assets/ff091f40-9b89-453d-9692-cf10c9500475)
    
</div>

<h1 align="center">Aberoth Ephemeris</h1>

<p>A python module that provides information about upcoming scroll events and moon phases in the MMORPG <a href="https://www.aberoth.com">Aberoth</a>.</p>

#### Installing
The module can be downloaded from PyPi using

```bash
pip install aberoth-ephemeris
```
or you can download [the latest release](https://github.com/jvandag/aberoth-ephemeris/releases) from GitHub
#### Use Example
Once you've installed the module it can be used like so:
```python
from aberoth_ephemeris import Ephemeris
import time

# number of milliseconds in a day
ms_1day = 86400000
# four days before the current time
startTime = round((time.time() * 1000) + -4 * ms_1day)
# 35 days after the current time
endTime = round((time.time() * 1000) + 35 * ms_1day)

ephemeris = Ephemeris(
    # the epoch time in ms that prediction calculations will start from
    start=round((time.time() * 1000) + -4 * 86400000),
    # the epoch time in ms that scroll prediction calculations will stop at
    end=round((time.time() * 1000) + 35 * 86400000),
    # the number of cycles into the future that the moon phases are calculated for
    numMoonCycles=8, 
    # adds discord timestamp to ephemeris event information if True
    discordTimestamps=False,
    # indicates that calculations should be split between multiple processes/cores
    multiProcess=True,
    # indicates number of cores to use, automatically uses all cores if None
    numCores = None,
    # None indicates that the built in orb variables should be used
    varFile = None
    )
```
The start and stop times are just examples and any time may be used so long as the start time is before the stop time.

By default, built in orb variables are used for predictions. If you wish to use your own variables you can pass the path to your own variables file into varFile as a string. See the [gathering your own variables](#gathering-your-own-variables) section for details on how you might gather your own variables.

Optionally, a web server may be ran to intake auto-calibration data from separate a script. To do so, run the following code on a separate thread or process

```python
from waitress import serve
from aberoth_ephemeris import app

# serve on separate thread or process
serve(app, host="0.0.0.0", port=5000, threads=1)
```
When valid calibration data is received over http request, the variables used to predict alignments are updated and used next time an ephemeris object is created or the ephemeris event cache is recreated.

Make sure to configure a .env file containing a pass key for the http server request
****

An excellent separate script that can be used to gather and send live calibration data to this module is the [Ephemeris Overheard Hook](https://github.com/aberoth-community/ephemeris-overheard-hook/tree/main) made by github user [jvandag](https://github.com/jvandag). It is built on github user [ashnel3's](https://github.com/ashnel3) [Overheard Scrapper](https://github.com/aberoth-community/overheard) which scrapes the [Aberoth overheard page](https://aberoth.com/highscore/overheard.html) to find changes in scroll state, moon phase, time of day, and number of players online.

For formatting of this http message refer to this [example fetch request](aberoth_ephemeris/UpdateWebServer/exampleCalibrationMsg.js) in javascript

#### Event Structure
The calculated scroll events are stored in the `Ephemeris.scrollEventsCache` which is formatted as follows
```python
[()]
```

#### Gathering your own variables
If you do not already have a moderate understanding of how Aberoth events happen, it would be helpful to read the wiki page on the [Aberoth solar system](https://bookofaberoth.fandom.com/wiki/Solar_System).

 Most variables are close to the real life [values provided by NASA](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) but not exact. These make a good starting point for calibrating variables. Conversely, you could also gather experimental data from the Aberoth orb room as well as some reference points using the [Ephemeris Overheard Hook](https://github.com/aberoth-community/ephemeris-overheard-hook/tree/main) or something similar. Some notes on how to do this with experimental data can be found [here](https://docs.google.com/document/d/1Zm3-20HE9L-DPRuTaEgN9hdeDa8B2-0iSYuh6M82Rs8/edit?usp=sharing). When it comes to refining/calibrating these variables, it is important to create a system that can tell you how a change affects the whole system not just the specific alignment event you're looking at. [Here is an example spreadsheet](https://docs.google.com/spreadsheets/d/1QrP-_moAXsK96srTq3BXStWcX4WGAzbLB_idEUgXuy4/edit?usp=sharing) that shows how you might set up such a system. To help better your understanding of this spreadsheet, it would be useful to still read the notes on [gathering the variables with experimental data](https://docs.google.com/document/d/1Zm3-20HE9L-DPRuTaEgN9hdeDa8B2-0iSYuh6M82Rs8/edit?usp=sharing) as it covers some of the more in-depth details on how the solar system works that aren't mentioned elsewhere.