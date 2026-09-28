"""
Unit tests for ProtectionRelayCoordinationSolver.
"""

import unittest
from apex_infrastructure_killswitch_kernel.core.models import (
    ProtectionRelay,
    FaultTransientEvent,
)
from apex_infrastructure_killswitch_kernel.core.protection_relay_coordination_solver import (
    ProtectionRelayCoordinationSolver,
)


class TestProtectionRelayCoordinationSolver(unittest.TestCase):
    def setUp(self):
        self.solver = ProtectionRelayCoordinationSolver(min_cti_ms=200.0)
        self.relays = [
            ProtectionRelay(
                relay_id="MAIN_500KV",
                tier="500KV_MAIN",
                pickup_current_a=2500.0,
                time_dial_setting=0.45,
                curve_type="IEC_VERY_INVERSE",
                ct_ratio=600.0,
                backup_for_relay_ids=["FEEDER_34_5KV"],
            ),
            ProtectionRelay(
                relay_id="FEEDER_34_5KV",
                tier="34_5KV_FEEDER",
                pickup_current_a=1200.0,
                time_dial_setting=0.20,
                curve_type="IEC_VERY_INVERSE",
                ct_ratio=300.0,
                backup_for_relay_ids=["RPDU_BRANCH"],
            ),
            ProtectionRelay(
                relay_id="RPDU_BRANCH",
                tier="RPDU_BRANCH",
                pickup_current_a=160.0,
                time_dial_setting=0.05,
                curve_type="IEC_EXTREMELY_INVERSE",
                ct_ratio=40.0,
                backup_for_relay_ids=[],
            ),
        ]

    def test_selective_isolation_without_sympathetic_trip(self):
        fault = FaultTransientEvent("F_RACK_01", "RPDU_BRANCH", 2800.0, 40.0)
        report = self.solver.evaluate_fault_coordination(fault, self.relays)

        self.assertEqual(report.primary_tripped_relay_id, "RPDU_BRANCH")
        self.assertLess(report.clearing_time_ms, 50.0)
        self.assertFalse(report.campus_isolated)
        self.assertGreater(report.sympathetic_trips_prevented, 0)
        self.assertLess(report.solve_time_us, 5000.0)

    def test_fault_below_pickup_no_trip(self):
        fault = FaultTransientEvent("F_MICRO_LEAK", "RPDU_BRANCH", 50.0, 10.0)
        report = self.solver.evaluate_fault_coordination(fault, self.relays)
        self.assertEqual(report.primary_tripped_relay_id, "NO_TRIP_BELOW_PICKUP")
        self.assertFalse(report.campus_isolated)


if __name__ == "__main__":
    unittest.main()
