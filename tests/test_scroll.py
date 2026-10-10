"""Regression tests for NumPy reference calculations and adaptive scanning."""

import importlib.resources
import math
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from aberoth_ephemeris import Ephemeris
from aberoth_ephemeris.ephemeris import scroll_events


def ephemeris(custom=False):
    obj = Ephemeris.__new__(Ephemeris)
    obj.variablesFile = Path(str(importlib.resources.files("aberoth_ephemeris.ephemeris").joinpath("variables.json")))
    obj.v = obj.getVariables(obj.variablesFile)
    if custom:
        for index, orb in enumerate(obj.v.values()):
            if "period" in orb:
                orb["period"] *= 1.0 + (index + 1) / 100
            if "radius" in orb:
                orb["radius"] *= 0.98
    obj.periods = obj.getPeriods()
    obj.radii = obj.getRadii()
    obj.refTimes = obj.getRefTimes()
    obj.refOffsets = obj.getRefOffsets()
    with mock.patch.object(Ephemeris, "updateVariables"):
        obj.setRefPositions()
    obj.refPositions = obj.getRefPositions()
    obj.increment = 60000
    obj.glowThresh = 0.5
    obj.darkThresh = 1
    obj.discordTimestamps = False
    obj.multiProcess = True
    obj.numCores = 2
    obj.scrollEventsCache = []
    obj.currentAlignmentStates = obj.lastAlignmentStates = np.zeros(9, dtype=bool)
    return obj


def reference_states(timestamp, params, glow=0.5, dark=1.0):
    omega, refs, offsets, radii, shadow = params
    rw = (np.array(omega) * (timestamp - np.array(refs)) + np.array(offsets)) % 360
    rw[0] = (rw[0] + 180) % 360
    positions = np.array([(shadow[0] * (timestamp - shadow[1]) + shadow[2]) % 360,
                          (rw[0] + 180) % 360])
    x = np.array(radii[1:]) * np.cos(np.radians(rw[1:])) - np.cos(np.radians(rw[0]))
    y = np.array(radii[1:]) * np.sin(np.radians(rw[1:])) - np.sin(np.radians(rw[0]))
    positions = np.append(positions, np.degrees(np.arctan2(y, x)) % 360)
    states = np.zeros(9, dtype=bool)
    for i in range(1, 9):
        diff = abs(positions[i:] % 180 - positions[i - 1] % 180)
        diff[diff > 90] = 180 - diff[diff > 90]
        for j in np.where(diff < (dark if i == 1 else glow))[0]:
            states[i - 1] = states[i + j] = True
    return states


def mask(states):
    return sum(1 << i for i, state in enumerate(states) if state)


def reference_scan(start, end, params, increment=60000, glow=0.5, dark=1.0):
    current = start
    last = reference_states(current, params, glow, dark)
    events = []
    while current < end:
        now = reference_states(current, params, glow, dark)
        if not np.array_equal(last, now):
            current -= increment
            while True:
                now = reference_states(current, params, glow, dark)
                if not np.array_equal(last, now):
                    events.append((current, mask(last), mask(now)))
                    last = now.copy()
                    break
                current += 1000
        current += increment
    return events, last, now if start < end else last


class ScrollTests(unittest.TestCase):
    def test_states_across_dates_and_custom_variables(self):
        rng = random.Random(373)
        for custom in (False, True):
            obj = ephemeris(custom)
            params = scroll_events.parameters(obj)
            for timestamp in [0, -86400000, 1725903360554, 1791241200000] + [rng.randrange(-10**12, 3 * 10**12) for _ in range(200)]:
                self.assertEqual(scroll_events.alignment_mask(timestamp, params), mask(reference_states(timestamp, params)))

    def test_scans_match_reference_timestamps_and_states(self):
        for custom in (False, True):
            params = scroll_events.parameters(ephemeris(custom))
            for start in (-86400000, 0, 1725903360554, 1791241200123):
                end = start + 86400000
                expected, _, _ = reference_scan(start, end, params)
                with self.subTest(custom=custom, start=start):
                    self.assertEqual(scroll_events.scan_portable(start, end, params, 60000, 0.5, 1), expected)
                    self.assertEqual(scroll_events.scan(start, end, params), expected)

    def test_39_day_regression(self):
        obj = ephemeris()
        params = scroll_events.parameters(obj)
        start, end = 1791241200000, 1794610800000
        # Use an independent NumPy calculation as the full-range reference.
        expected, _, _ = reference_scan(start, end, params)
        self.assertEqual(scroll_events.scan(start, end, params), expected)
        self.assertEqual(scroll_events.scan_portable(start, end, params, 60000, 0.5, 1), expected)

    def test_strict_threshold_and_opposite_alignment(self):
        for offset in (0.999999999, 1.0, 1.000000001, 178.999999999, 179.0, 179.000000001):
            params = ((0.0,) * 8, (0,) * 8, (0.0,) * 8, (2.0,) * 8,
                      (0.00001, 0, offset))
            for glow, dark in ((0.5, 1.0), (0.2, 0.8)):
                expected, _, _ = reference_scan(0, 120000, params, glow=glow, dark=dark)
                self.assertEqual(scroll_events.scan(0, 120000, params, glow=glow, dark=dark), expected)
                self.assertEqual(scroll_events.scan_portable(0, 120000, params, 60000, glow, dark), expected)

    def test_public_events_states_and_cache(self):
        obj = ephemeris()
        obj.discordTimestamps = True
        start, end = 1791241200123, 1791327600123
        changes, last, current = reference_scan(start, end, scroll_events.parameters(obj))
        expected = [obj.createAlignmentEvent(t, scroll_events.states(before), scroll_events.states(after))
                    for t, before, after in changes]
        obj.cacheFile = Path("unused")
        with mock.patch.object(obj, "saveCache") as save:
            self.assertEqual(obj.createScrollEventRange(start, end, True), expected)
            self.assertEqual(obj.scrollEventsCache, expected)
            save.assert_called_once_with(obj.cacheFile)
        np.testing.assert_array_equal(obj.lastAlignmentStates, last)
        np.testing.assert_array_equal(obj.currentAlignmentStates, current)
        self.assertEqual(obj.processScrollTimeRange(start, end), expected)

    def test_explicit_process_pool_and_tiny_range(self):
        obj = ephemeris()
        chunks = [(1791241200000, 1791284400000, 0), (1791284400000, 1791327600000, 1)]
        expected = [event for start, end, _ in chunks for event in obj.processScrollTimeRange(start, end)]
        self.assertEqual(obj.createProcessPool(chunks), expected)
        self.assertEqual(obj.multiProcessCreateScrollEventRange(0, 1), [])

    def test_empty_and_invalid_ranges(self):
        params = scroll_events.parameters(ephemeris())
        self.assertEqual(scroll_events.scan(123, 123, params), [])
        self.assertEqual(scroll_events.scan(124, 123, params), [])
        with self.assertRaises(ValueError):
            scroll_events.scan(0, 10000, params, increment=0)
        with self.assertRaises(ValueError):
            scroll_events.scan(0, 10000, params, glow=math.nan)
        with self.assertRaises(OverflowError):
            scroll_events.scan(0, 1 << 63, params)

    def test_constructor_default_and_custom_path(self):
        obj = ephemeris()
        with mock.patch("pathlib.Path.exists", return_value=True), \
             mock.patch.object(Ephemeris, "saveCache"), \
             mock.patch.object(Ephemeris, "updateVariables"):
            actual = Ephemeris(start=1791241200000, end=1791244800000,
                               varFile=str(obj.variablesFile))
        expected_cores = os.cpu_count() or 1
        self.assertEqual(actual.numCores, expected_cores)
        self.assertEqual(actual.scrollEventsCache,
                         obj.processScrollTimeRange(1791241200000, 1791244800000))

    def test_portable_scanner_and_lazy_app_import(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, "-B", "-c",
                            "import sys; from aberoth_ephemeris import Ephemeris; "
                            "from aberoth_ephemeris.ephemeris import scroll_events; "
                            "assert 'flask' not in sys.modules; "
                            "from aberoth_ephemeris import app; assert app.name; "
                            "from aberoth_ephemeris import app as again; assert again is app"],
                           env=dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path)),
                           cwd=directory, check=True)


if __name__ == "__main__":
    unittest.main()
