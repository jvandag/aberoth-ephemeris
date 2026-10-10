"""Regression coverage for lunar event timestamps, phases, and formatting."""

import hashlib
import json
import unittest
from unittest import mock

import numpy as np

from test_scroll import ephemeris


def lunar_ephemeris(custom=False):
    obj = ephemeris(custom)
    obj.noonRefTime = 1725903360554
    obj.oneAberothDay = 8640000
    return obj


class LunarTests(unittest.TestCase):
    def test_complete_calendar_fingerprints(self):
        # Fixed fingerprints cover every timestamp and event dictionary,
        # including Discord formatting, in each calendar.
        cases = (
            (0, 8, False,
             "bf500b149f5d8852bbe4b3f148d88858cfa7e50d3c30a23f906a6dcd76ff6a2d"),
            (-86400001, 8, False,
             "0fc91f6d4437126dc7a35679bb1b8f980f61153009efedba03fc2c43e282670a"),
            (1725903360554, 8, False,
             "7b4a64d7b68313c7f1da72e7b8733571c59f80f5b85ae0d52188209a437cdeec"),
            (1791241200123, 8, True,
             "6311a086aa79e1ebe82cafbfbd618d6cc57d15fc36ce0ced0e86c8a176938c42"),
            (1725903360554, 10000, False,
             "8eee20f5700af2284b25600a7f05d0fdc831fe1e4fb06b2c3b6dd8f5aede427d"),
        )
        for start, cycles, custom, expected in cases:
            with self.subTest(start=start, cycles=cycles, custom=custom):
                events = lunar_ephemeris(custom).createLunarCalendar(start, cycles)
                encoded = json.dumps(events, separators=(",", ":")).encode()
                self.assertEqual(hashlib.sha256(encoded).hexdigest(), expected)
                self.assertEqual(len(events), cycles * 10)

    def test_empty_calendar_and_calibration_refresh(self):
        obj = lunar_ephemeris()
        start = obj.noonRefTime
        self.assertEqual(obj.createLunarCalendar(start, 0), [])
        expected = obj.createLunarCalendar(start, 8)
        offset = obj.v["shadow"]["refOffset"]
        obj.v["shadow"]["refOffset"] = offset + 20
        self.assertNotEqual(obj.createLunarCalendar(start, 8), expected)
        obj.v["shadow"]["refOffset"] = offset
        self.assertEqual(obj.createLunarCalendar(start, 8), expected)

    def test_phase_boundary_requires_strict_crossing(self):
        obj = lunar_ephemeris()
        obj.noonRefTime = 0
        obj.oneAberothDay = 1
        obj.periods = np.array([float("inf")])  # Fixed sun position.
        obj.refTimes = np.array([0])
        obj.refPositions = np.array([0.0])
        obj.v["shadow"] = {"period": 360, "refTime": 0, "refOffset": 89.0}
        # Exactly reaching 90 degrees at the next noon is not a strict crossing.
        # With this exact one-degree step, the first detected phase is the wrap
        # from 359 degrees to zero, rather than a quarter or full phase.
        events = obj.createLunarCalendar(0, 1)
        self.assertEqual(events[0], (270, {
            "phase": "new", "discordTS": "<t:0:D> <t:0:t>",
        }))
        obj.v["shadow"]["refOffset"] = 89.5
        events = obj.createLunarCalendar(0, 1)
        self.assertEqual(events[0][0], 0)
        self.assertEqual(events[0][1]["phase"], "first_quarter")
        self.assertEqual(events[1][0], 1)
        self.assertEqual(events[1][1]["phase"], "waxing_gibbous")

    def test_update_moon_cache(self):
        obj = lunar_ephemeris()
        start = obj.noonRefTime
        expected = obj.createLunarCalendar(start, 8)
        with mock.patch.object(obj, "updateRefTimes") as update:
            obj.updateMoonCache(start, 8)
        update.assert_called_once_with()
        self.assertEqual(obj.moonCyclesCache, expected)


if __name__ == "__main__":
    unittest.main()
