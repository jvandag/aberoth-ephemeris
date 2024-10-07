<div style="user-select: none;" align="center">
    
![Ephemeris Logo](https://github.com/user-attachments/assets/ff091f40-9b89-453d-9692-cf10c9500475)
    
</div>

<h1 align="center">Aberoth Ephemeris</h1>

<p>A python module that provides information about upcoming scroll events and moon phases in the MMORPG Aberoth.</p>

<div align="center">
<b>Example scroll event prediction menu:</b>
<br>

https://github.com/user-attachments/assets/9d1ac76d-a755-4b9b-b36b-f435c71fd833

</div>

## Usage

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
    # adds discord timestamp to ephemeris event tuples if True
    discordTimestamps=False,
    # indicates that calculations should be split between multiple processes/cores
    multiProcess=True,
    # indicates number of cores to use, automatically uses all cores if None
    numCores = None
    )
```
The start and stop times are just examples and any time may be used so long as the start time is before the stop time.

Optionally, a web server may be ran to intake auto-calibration data from separate a script. To do so, run the following code on a separate thread or process

```python
from waitress import serve
from aberoth_ephemeris import app

# serve on separate thread or process
serve(app, host="0.0.0.0", port=5000, threads=1)
```
When valid calibration data is received over http request, the variables used to predict alignments are updated and used next time an ephemeris object is created or the ephemeris event cache is recreated.

An excellent separate script that can be used to send live calibration data to the [Aberoth Ephemeris](https://github.com/jvandag/aberoth-ephemeris) module used for this bot is the [Ephemeris Overheard Hook](https://github.com/aberoth-community/ephemeris-overheard-hook/tree/main) made by github user [jvandag](https://github.com/jvandag). It is built on github user [ashnel3's](https://github.com/ashnel3) [Overheard Scrapper](https://github.com/aberoth-community/overheard) which scrapes the [Aberoth overheard page](https://aberoth.com/highscore/overheard.html) to find changes in scroll state, moon phase, time of day, and number of players online.

