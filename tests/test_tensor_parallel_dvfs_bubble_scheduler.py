"""
Unit tests for TensorParallelDVFSBubbleScheduler.
"""

import unittest
from apex_infrastructure_killswitch_kernel.core.models import PipelineStageConfig
from apex_infrastructure_killswitch_kernel.core.tensor_parallel_dvfs_bubble_scheduler import (
    TensorParallelDVFSBubbleScheduler,
)


class TestTensorParallelDVFSBubbleScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = TensorParallelDVFSBubbleScheduler(power_scaling_exponent=2.8)
        self.stages = [
            PipelineStageConfig(
                stage_id=f"stage_{i:02d}",
                pp_index=i,
                tp_degree=8,
                dp_degree=64,
                cp_degree=8,
                nominal_freq_ghz=1.98,
                min_freq_ghz=1.10,
                forward_weight_tflops=400.0,
                backward_weight_tflops=800.0,
                num_layers=8,
            )
            for i in range(16)
        ]

    def test_emergency_power_shed_meets_ceiling(self):
        target_ceiling_mw = 250.0
        report = self.scheduler.schedule_power_shed(target_ceiling_mw, self.stages)

        self.assertLessEqual(report.throttled_power_mw, target_ceiling_mw + 1.0)
        self.assertGreater(report.power_reduction_pct, 60.0)
        self.assertFalse(report.checkpoint_diverged)
        self.assertLess(report.allreduce_skew_ns, 50.0)
        self.assertLess(report.solve_time_us, 5000.0)

    def test_power_already_below_ceiling(self):
        target_ceiling_mw = 1500.0
        report = self.scheduler.schedule_power_shed(target_ceiling_mw, self.stages)
        self.assertEqual(report.power_reduction_pct, 0.0)
        self.assertEqual(report.bubble_nop_stages_injected, 0)


if __name__ == "__main__":
    unittest.main()
