# Ephemeris manual calibration:
For calibration you will need to use the time for the middle of alignments that have linear change in position relative to each other. This means that White will be calibrated using dark alignments with the shadow orb and all other orbs will be calibrated using alignments between white and that orb.
## First get the candle's position:
It's important to gather white's position first since the period of the moon is our most accurate measured sample and all other subsequent calibrations depend on the white orb. 
- First find the epoch in milliseconds of the start and end time of the most recent accurate alignment between the shadow and white orb. Tools like [epochconverter.com](https://www.epochconverter.com/) are great for taking a human readable timestamp and converting it into an epoch time stamp
- Next, sum the start and end times and divide by two to get the time that the orbs should be exactly aligned.
- Find the position of the shadow orb relative to the candle at this exact alignment time.
- Add 180 degrees to this position and then modulus by 360 to find the position of the candle relative to the white orb
- Replace the refTime and refPos in your [variables file](aberoth_ephemeris\ephemeris\variables.json) with the exact alignment time and the found position respectively
- The refOffset is unused for the candle so there is no need to set it
- If the moon predictions are off by half a cycle, use the next or previous white glow to calibrate instead

## Getting the orb's positions
The order in which you get the positions of the remaining orbs does not matter, just make sure you've calibrated the candle's position first.
The white orb will not be calibrated as it's used as a reference point. Calibrations to the shadow orb should be made using manually gathered data. The process for calibrating the shadow orb's position is detailed in the next section.
- First find the epoch in milliseconds of the start and end time of the most recent accurate alignment between the orb in question and the white orb. 
- Next, sum the start and end times and divide by two to get the time that the orbs should be exactly aligned.
- If the candle and the orb in question are on opposite sides of the white orb set the refOffset for the respective orb to 180, otherwise set it to 0
- You needn't find the position of the orb, only the time of alignment and the offset.

## Getting the shadow orb's position
Calibration for the shadow orb must be done manually. It is recommended to record the orb room with a epoch clock visible in the recording to gather data.
The shadow orb's period is highly accurate and should not need to be recalibrated as often as the other orbs. If you do recalibrate the shadow orb it should be recalibrated first, before the candle.
- Find the epoch time of the frame that the shadow orb moves to the pixel at 90 or 270 degrees from the candle.
- Find the epoch time of the frame that the shadow orb moves off of that pixel.
- Average the two time stamps to find your refTime
- If the pixel was 90 degrees set the refPos to 90. Otherwise If the pixel was 270 degrees set the refPos to 270.
