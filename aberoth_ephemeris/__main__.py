from .ephemeris import Ephemeris
from .UpdateWebServer import app

if __name__ == "__main__":
    
    def formatTime(milliseconds: int) -> str:
        """Takes in a length of time in milliseconds and formats it into h:m:s:ms format.

        Parameters
        ---------
            milliseconds: `int`
                The length of time to be formatted
        Returns
        ---------
            `str`
            The length of time in the format f"{hours:.0f}h {minutes:.0f}m {seconds:.0f}s {ms}ms"
        """
        # Convert milliseconds to seconds
        seconds = milliseconds // 1000
        # Calculate hours, minutes and seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        ms = milliseconds % 1000
        # Return formatted time string
        return f"{hours:.0f}h {minutes:.0f}m {seconds:.0f}s {ms}ms"

    import time
    startTime = time.time_ns() // 1_000_000
    ephemeris = Ephemeris(
        start=round((time.time() * 1000) + -4 * 86400000),
        end=round((time.time() * 1000) + 35 * 86400000),
        numMoonCycles=8,
        discordTimestamps=False,
        multiProcess=True,
    )
    stopTime = time.time_ns() // 1_000_000
    print(
        f"{ephemeris.__numCores} cores; Execution time: {formatTime(stopTime-startTime)}"
    )
    print("First scroll event:", ephemeris.scrollEventsCache[0])
    print("Last scroll event:", ephemeris.scrollEventsCache[-1])
    print("First moon event:", ephemeris.moonCyclesCache[0])
    print("Last moon event:", ephemeris.moonCyclesCache[0])
    # import timeit
    # execution_time = timeit.timeit("Ephemeris(start=round((time.time() * 1000) - 0 * 86400000), end=round((time.time() * 1000) + 35 * 86400000), numMoonCycles=8, multiProcess=False)", globals=globals(), number=10)
    
    # print(execution_time/10)
