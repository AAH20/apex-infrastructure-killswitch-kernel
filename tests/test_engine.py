"""
Unit tests for ApexInfrastructureKillSwitchEngine and synthetic state generator.
"""

import unittest
from apex_infrastructure_killswitch_kernel.engine import (
    ApexInfrastructureKillSwitchEngine,
    generate_synthetic_killswitch_state,
)


class TestApexInfrastructureKillSwitchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ApexInfrastructureKillSwitchEngine()
        (
            self.relays,
            self.fault,
            self.stages,
            self.strings,
            self.bands,
            self.telemetry,
        ) = generate_synthetic_killswitch_state()

    def test_synthetic_state_integrity(self):
        self.assertGreater(len(self.relays), 0)
        self.assertIsNotNone(self.fault)
        self.assertGreater(len(self.stages), 0)
        self.assertGreater(len(self.strings), 0)
        self.assertGreater(len(self.bands), 0)
        self.assertGreater(len(self.telemetry), 0)

    def test_engine_subsystem_execution(self):
        # 1. Protection Relays
        rep_relay = self.engine.coordinate_protection_relays(self.fault, self.relays)
        self.assertEqual(rep_relay.primary_tripped_relay_id, "RELAY_RPDU_RACK_42")
        self.assertFalse(rep_relay.campus_isolated)

        # 2. Tensor DVFS
        rep_dvfs = self.engine.schedule_tensor_dvfs_shed(250.0, self.stages)
        self.assertLessEqual(rep_dvfs.throttled_power_mw, 251.0)
        self.assertFalse(rep_dvfs.checkpoint_diverged)

        # 3. Complex Impedance BMS
        rep_bms = self.engine.split_impedance_currents(25_000.0, self.strings, 100.0)
        self.assertFalse(rep_bms.pyrofuse_tripped)
        self.assertLessEqual(rep_bms.max_pyrofuse_stress_ratio, 0.70)

        # 4. Turbine Governor
        rep_turbine = self.engine.optimize_turbine_governor(30.0, self.bands)
        self.assertEqual(rep_turbine.achieved_rpm, 3600.0)
        self.assertFalse(rep_turbine.resonance_limit_violated)
        self.assertTrue(rep_turbine.synchronization_locked)

        # 5. Dead-Man Market Clearing
        rep_deadman = self.engine.clear_deadman_market(self.telemetry, 59.981)
        self.assertFalse(rep_deadman.deadman_switch_fired)
        self.assertTrue(rep_deadman.false_trip_defused)

    def test_full_pipeline_benchmark(self):
        bench_rep = self.engine.run_full_pipeline_benchmark(iterations=10)
        self.assertGreater(bench_rep.total_runtime_ms, 0.0)
        self.assertTrue(hasattr(bench_rep, "relay_coordination_summary"))
        self.assertTrue(hasattr(bench_rep, "tensor_dvfs_summary"))
        self.assertTrue(hasattr(bench_rep, "impedance_bms_summary"))
        self.assertTrue(hasattr(bench_rep, "turbine_governor_summary"))
        self.assertTrue(hasattr(bench_rep, "deadman_clearing_summary"))


if __name__ == "__main__":
    unittest.main()
