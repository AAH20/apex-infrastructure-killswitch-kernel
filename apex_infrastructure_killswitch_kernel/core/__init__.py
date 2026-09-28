"""
Core solver modules for Apex Infrastructure Kill-Switch Orchestration Kernel.
"""

from apex_infrastructure_killswitch_kernel.core.models import (
    ProtectionRelay,
    FaultTransientEvent,
    RelayCoordinationReport,
    PipelineStageConfig,
    ClusterSheddingScheduleReport,
    BatteryStringImpedance,
    ImpedanceSplittingReport,
    ResonantSpeedBand,
    TurbineRampTrajectoryReport,
    GridTelemetrySample,
    DeadManClearingReport,
    KillSwitchPipelineBenchmarkReport,
)
from apex_infrastructure_killswitch_kernel.core.protection_relay_coordination_solver import (
    ProtectionRelayCoordinationSolver,
)
from apex_infrastructure_killswitch_kernel.core.tensor_parallel_dvfs_bubble_scheduler import (
    TensorParallelDVFSBubbleScheduler,
)
from apex_infrastructure_killswitch_kernel.core.impedance_current_splitting_bms import (
    ImpedanceCurrentSplittingBMSSolver,
)
from apex_infrastructure_killswitch_kernel.core.turbine_resonance_governor_solver import (
    TurbineResonanceGovernorSolver,
)
from apex_infrastructure_killswitch_kernel.core.latency_discounted_amm_deadman import (
    LatencyDiscountedAMMDeadManSolver,
)

__all__ = [
    "ProtectionRelay",
    "FaultTransientEvent",
    "RelayCoordinationReport",
    "PipelineStageConfig",
    "ClusterSheddingScheduleReport",
    "BatteryStringImpedance",
    "ImpedanceSplittingReport",
    "ResonantSpeedBand",
    "TurbineRampTrajectoryReport",
    "GridTelemetrySample",
    "DeadManClearingReport",
    "KillSwitchPipelineBenchmarkReport",
    "ProtectionRelayCoordinationSolver",
    "TensorParallelDVFSBubbleScheduler",
    "ImpedanceCurrentSplittingBMSSolver",
    "TurbineResonanceGovernorSolver",
    "LatencyDiscountedAMMDeadManSolver",
]
