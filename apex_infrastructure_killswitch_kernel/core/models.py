"""
Core Data Models for Apex Infrastructure Kill-Switch Orchestration Kernel.
Encompasses Substation Protection Relays, 4D Tensor-Parallel DVFS Shedding,
Complex Electrochemical Impedance Current Splitting, Campbell Resonant Speed Turbine Governors,
and Stochastic Latency-Discounted Dead-Man Market Clearing.
Zero external pip dependencies. Pure Python 3.10+.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional


# ============================================================================
# 1. Protection Relay Coordination Models
# ============================================================================

@dataclass(slots=True)
class ProtectionRelay:
    relay_id: str
    tier: str  # "500KV_MAIN", "34_5KV_FEEDER", "480V_SUB", "RPDU_BRANCH"
    pickup_current_a: float
    time_dial_setting: float
    curve_type: str  # "IEC_STANDARD_INVERSE", "IEC_VERY_INVERSE", "IEC_EXTREMELY_INVERSE"
    ct_ratio: float
    backup_for_relay_ids: List[str]


@dataclass(slots=True)
class FaultTransientEvent:
    fault_id: str
    location_bus: str
    fault_current_a: float
    duration_ms: float


@dataclass(slots=True)
class RelayCoordinationReport:
    fault_id: str
    primary_tripped_relay_id: str
    clearing_time_ms: float
    coordination_margins_ms: Dict[str, float]
    sympathetic_trips_prevented: int
    campus_isolated: bool
    solve_time_us: float


# ============================================================================
# 2. 4D Tensor-Parallel DVFS Bubble Shedding Models
# ============================================================================

@dataclass(slots=True)
class PipelineStageConfig:
    stage_id: str
    pp_index: int
    tp_degree: int
    dp_degree: int
    cp_degree: int
    nominal_freq_ghz: float
    min_freq_ghz: float
    forward_weight_tflops: float
    backward_weight_tflops: float
    num_layers: int


@dataclass(slots=True)
class ClusterSheddingScheduleReport:
    initial_power_mw: float
    throttled_power_mw: float
    power_reduction_pct: float
    bubble_ratio: float
    allreduce_skew_ns: float
    checkpoint_diverged: bool
    bubble_nop_stages_injected: int
    solve_time_us: float


# ============================================================================
# 3. Complex Impedance Current Splitting & Pyrofuse Selectivity Models
# ============================================================================

@dataclass(slots=True)
class BatteryStringImpedance:
    string_id: str
    medium_type: str  # "SUPERCAPACITOR", "FLYWHEEL_INVERTER", "SODIUM_ION", "LFP"
    r_ohmic_mohm: float
    r_charge_transfer_mohm: float
    c_double_layer_farad: float
    warburg_sigma: float
    pyrofuse_i2t_threshold: float
    current_i2t_accumulated: float = 0.0


@dataclass(slots=True)
class ImpedanceSplittingReport:
    total_requested_current_a: float
    pulse_frequency_hz: float
    current_allocations_a: Dict[str, float]
    current_variance_a2: float
    max_pyrofuse_stress_ratio: float
    pyrofuse_tripped: bool
    solve_time_us: float


# ============================================================================
# 4. Turbine Fast-Start Resonance Governor Models
# ============================================================================

@dataclass(slots=True)
class ResonantSpeedBand:
    band_id: str
    min_rpm: float
    max_rpm: float
    max_dwell_ms: float
    mode_name: str  # e.g., "1st Bending", "Torsional", "2nd Bending"


@dataclass(slots=True)
class TurbineRampTrajectoryReport:
    target_sync_rpm: float
    achieved_rpm: float
    total_spool_time_s: float
    max_resonance_dwell_ms: float
    resonance_limit_violated: bool
    peak_tit_c: float
    surge_margin_pct: float
    phase_angle_mismatch_deg: float
    synchronization_locked: bool
    solve_time_us: float


# ============================================================================
# 5. Latency-Discounted A-ECMM Dead-Man Switch Models
# ============================================================================

@dataclass(slots=True)
class GridTelemetrySample:
    sample_id: str
    measured_freq_hz: float
    raw_latency_ms: float
    packet_loss_flag: bool


@dataclass(slots=True)
class DeadManClearingReport:
    estimated_true_freq_hz: float
    kalman_uncertainty_variance: float
    is_genuine_grid_trip: bool
    deadman_switch_fired: bool
    false_trip_defused: bool
    arbitrage_captured_usd: float
    market_clearing_state: str  # "ACTIVE_ARBITRAGE", "ISLANDED_PROTECTION", "DEFUSED_JITTER"
    solve_time_us: float


# ============================================================================
# 6. Master Integration Benchmark Model
# ============================================================================

@dataclass(slots=True)
class KillSwitchPipelineBenchmarkReport:
    total_runtime_ms: float
    timestamp: str
    relay_coordination_summary: Dict[str, float]
    tensor_dvfs_summary: Dict[str, float]
    impedance_bms_summary: Dict[str, float]
    turbine_governor_summary: Dict[str, float]
    deadman_clearing_summary: Dict[str, float]
