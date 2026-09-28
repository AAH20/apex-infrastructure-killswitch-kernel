"""
Unit tests for ImpedanceCurrentSplittingBMSSolver.
"""

import unittest
from apex_infrastructure_killswitch_kernel.core.models import BatteryStringImpedance
from apex_infrastructure_killswitch_kernel.core.impedance_current_splitting_bms import (
    ImpedanceCurrentSplittingBMSSolver,
)


class TestImpedanceCurrentSplittingBMS(unittest.TestCase):
    def setUp(self):
        self.bms = ImpedanceCurrentSplittingBMSSolver(max_allowable_pyrofuse_stress=0.70)
        self.strings = [
            BatteryStringImpedance(
                string_id="SC_STRING",
                medium_type="SUPERCAPACITOR",
                r_ohmic_mohm=0.8,
                r_charge_transfer_mohm=0.1,
                c_double_layer_farad=500.0,
                warburg_sigma=0.01,
                pyrofuse_i2t_threshold=10.0e6,
            ),
            BatteryStringImpedance(
                string_id="SODIUM_STRING",
                medium_type="SODIUM_ION",
                r_ohmic_mohm=4.0,
                r_charge_transfer_mohm=1.5,
                c_double_layer_farad=80.0,
                warburg_sigma=0.10,
                pyrofuse_i2t_threshold=8.0e6,
            ),
        ]

    def test_current_splitting_and_pyrofuse_safety(self):
        report = self.bms.optimize_current_split(15_000.0, self.strings, 100.0)

        self.assertFalse(report.pyrofuse_tripped)
        self.assertLessEqual(report.max_pyrofuse_stress_ratio, 0.70)
        # Supercapacitor should carry higher current due to lower impedance
        self.assertGreater(
            report.current_allocations_a["SC_STRING"],
            report.current_allocations_a["SODIUM_STRING"],
        )
        self.assertLess(report.solve_time_us, 5000.0)

    def test_zero_current_request(self):
        report = self.bms.optimize_current_split(0.0, self.strings, 100.0)
        self.assertEqual(report.max_pyrofuse_stress_ratio, 0.0)
        self.assertFalse(report.pyrofuse_tripped)


if __name__ == "__main__":
    unittest.main()
