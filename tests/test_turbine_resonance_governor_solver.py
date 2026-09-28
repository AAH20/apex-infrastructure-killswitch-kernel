"""
Unit tests for TurbineResonanceGovernorSolver.
"""

import unittest
from apex_infrastructure_killswitch_kernel.core.models import ResonantSpeedBand
from apex_infrastructure_killswitch_kernel.core.turbine_resonance_governor_solver import (
    TurbineResonanceGovernorSolver,
)


class TestTurbineResonanceGovernorSolver(unittest.TestCase):
    def setUp(self):
        self.governor = TurbineResonanceGovernorSolver(
            target_sync_rpm=3600.0, max_tit_c=1450.0, min_surge_margin_pct=18.0
        )
        self.bands = [
            ResonantSpeedBand("BAND_1", 1200.0, 1300.0, 120.0, "1st Bending"),
            ResonantSpeedBand("BAND_2", 2300.0, 2400.0, 150.0, "Torsional"),
        ]

    def test_turbine_spool_and_resonance_avoidance(self):
        report = self.governor.optimize_ramp_trajectory(30.0, self.bands)

        self.assertEqual(report.achieved_rpm, 3600.0)
        self.assertFalse(report.resonance_limit_violated)
        self.assertLess(report.max_resonance_dwell_ms, 120.0)
        self.assertLess(report.peak_tit_c, 1450.0)
        self.assertGreaterEqual(report.surge_margin_pct, 18.0)
        self.assertTrue(report.synchronization_locked)
        self.assertLess(report.solve_time_us, 10000.0)


if __name__ == "__main__":
    unittest.main()
