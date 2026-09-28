"""
Unit tests for LatencyDiscountedAMMDeadManSolver.
"""

import unittest
from apex_infrastructure_killswitch_kernel.core.models import GridTelemetrySample
from apex_infrastructure_killswitch_kernel.core.latency_discounted_amm_deadman import (
    LatencyDiscountedAMMDeadManSolver,
)


class TestLatencyDiscountedAMMDeadMan(unittest.TestCase):
    def setUp(self):
        self.solver = LatencyDiscountedAMMDeadManSolver(
            nominal_frequency_hz=60.0, trip_threshold_hz=59.50, deadman_timeout_ms=500.0
        )

    def test_nominal_arbitrage_clearing(self):
        telemetry = [
            GridTelemetrySample("s1", 59.98, 20.0, False),
            GridTelemetrySample("s2", 59.97, 25.0, False),
        ]
        report = self.solver.filter_telemetry_and_clear_market(telemetry, 59.98)
        self.assertEqual(report.market_clearing_state, "ACTIVE_ARBITRAGE")
        self.assertFalse(report.deadman_switch_fired)
        self.assertFalse(report.false_trip_defused)
        self.assertGreater(report.arbitrage_captured_usd, 0.0)

    def test_network_jitter_defuses_false_deadman_trip(self):
        # High network latency (750 ms > 500 ms timeout), but healthy local PMU (59.98 Hz)
        telemetry = [
            GridTelemetrySample("s1", 59.98, 750.0, False),
        ]
        report = self.solver.filter_telemetry_and_clear_market(telemetry, 59.98)
        self.assertTrue(report.false_trip_defused)
        self.assertFalse(report.deadman_switch_fired)
        self.assertEqual(report.market_clearing_state, "DEFUSED_JITTER")
        self.assertGreater(report.arbitrage_captured_usd, 0.0)

    def test_genuine_grid_collapse_fires_deadman(self):
        # Genuine frequency collapse below 59.50 Hz
        telemetry = [
            GridTelemetrySample("s1", 59.35, 15.0, False),
        ]
        report = self.solver.filter_telemetry_and_clear_market(telemetry, 59.35)
        self.assertTrue(report.deadman_switch_fired)
        self.assertTrue(report.is_genuine_grid_trip)
        self.assertEqual(report.market_clearing_state, "ISLANDED_PROTECTION")


if __name__ == "__main__":
    unittest.main()
