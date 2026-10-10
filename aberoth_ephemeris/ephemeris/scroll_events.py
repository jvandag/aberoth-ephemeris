"""Scroll-event detection and alignment-state calculations.

The scanner checks each minute, then rescans a minute containing a change at
one-second resolution. It prepares orbital constants once per range and
represents the nine alignment states as one integer bit mask, avoiding small
per-timestamp NumPy allocations.
"""

import math


def parameters(ephemeris):
    """Snapshot mutable orbital data once per range, not once per timestamp."""
    periods = [float(value) for value in ephemeris.periods]
    shadow = ephemeris.v["shadow"]
    if any(not math.isfinite(p) or p <= 0 for p in periods + [float(shadow["period"])]):
        raise ValueError("Orbital periods must be finite and positive")
    result = (
        tuple(360 / p for p in periods),
        tuple(int(t) for t in ephemeris.refTimes),
        tuple(float(p) for p in ephemeris.refPositions),
        tuple(float(r) for r in ephemeris.radii),
        (360 / float(shadow["period"]), int(shadow["refTime"]), float(shadow["refOffset"])),
    )
    if any(len(values) != 8 for values in result[:4]):
        raise ValueError("Expected eight orbital parameters")
    if any(not math.isfinite(v) for values in (result[0], result[2], result[3]) for v in values):
        raise ValueError("Orbital parameters must be finite")
    if not math.isfinite(result[4][2]):
        raise ValueError("Shadow offset must be finite")
    return result


def alignment_mask(timestamp, params, glow=0.5, dark=1.0):
    omega, refs, offsets, radii, shadow = params
    rw = [(omega[i] * (timestamp - refs[i]) + offsets[i]) % 360 for i in range(8)]
    rw[0] = (rw[0] + 180) % 360
    candle_x = math.cos(math.radians(rw[0]))
    candle_y = math.sin(math.radians(rw[0]))
    positions = [(shadow[0] * (timestamp - shadow[1]) + shadow[2]) % 360,
                 (rw[0] + 180) % 360]
    for i in range(1, 8):
        angle = math.radians(rw[i])
        x = radii[i] * math.cos(angle) - candle_x
        y = radii[i] * math.sin(angle) - candle_y
        positions.append(math.degrees(math.atan2(y, x)) % 360)
    positions = [p % 180 for p in positions]
    mask = 0
    for i in range(8):
        threshold = dark if i == 0 else glow
        for j in range(i + 1, 9):
            difference = abs(positions[i] - positions[j])
            if difference > 90:
                difference = 180 - difference
            if difference < threshold:
                mask |= (1 << i) | (1 << j)
    return mask


def scan_portable(start, end, params, increment, glow, dark):
    """Scan a range with minute probes and second-resolution refinement."""
    current_time = start
    previous_mask = alignment_mask(current_time, params, glow, dark)
    events = []
    while current_time < end:
        current_mask = alignment_mask(current_time, params, glow, dark)
        if current_mask != previous_mask:
            refinement_end = current_time
            current_time -= increment
            while current_time <= refinement_end:
                current_mask = alignment_mask(current_time, params, glow, dark)
                if current_mask != previous_mask:
                    events.append((current_time, previous_mask, current_mask))
                    previous_mask = current_mask
                    break
                current_time += 1000
            else:
                raise RuntimeError("No alignment change found in refinement interval")
        current_time += increment
    return events


def scan(start, end, params, increment=60000, glow=0.5, dark=1.0):
    start, end, increment = int(start), int(end), int(increment)
    if increment <= 0:
        raise ValueError("increment must be positive")
    if not math.isfinite(glow) or not math.isfinite(dark):
        raise ValueError("Alignment thresholds must be finite")
    if start >= end:
        return []
    # Keep integer subtraction exact for the floating-point orbital formulas.
    limit = (1 << 52) - 1
    if any(abs(t) > limit for t in (start, end, increment, *params[1], params[4][1])):
        raise OverflowError("Timestamp or increment outside supported millisecond range")
    return scan_portable(start, end, params, increment, float(glow), float(dark))


def states(mask):
    return [bool(mask & (1 << i)) for i in range(9)]
