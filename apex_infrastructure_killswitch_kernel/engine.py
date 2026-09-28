"""
Unified Coordination Engine for Apex Infrastructure Kill-Switch Orchestrator Kernel.
Coordinates Substation Protection Relay Grading, 4D Tensor-Parallel DVFS Shedding,
Complex Electrochemical Impedance Current Splitting, Campbell Resonant Speed Turbine Governors,
and Stochastic Latency-Discounted Dead-Man Market Clearing.
Zero external pip dependencies. Pure Python 3.10+.
"""

from __future__ import annotations
import datetime
import time
from typing import List, Dict, Set, Tuple, Optional

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


def generate_synthetic_killswitch_state() -> Tuple[
    List[ProtectionRelay],
    FaultTransientEvent,
    List[PipelineStageConfig],
    List[BatteryStringImpedance],
    List[ResonantSpeedBand],
    List[GridTelemetrySample],
]:
    """
    Generates realistic 1-Gigawatt physical-to-computational datacenter infrastructure state.
    """
    # 1. Multi-tier Substation Protection Relays
    relays: List[ProtectionRelay] = [
        ProtectionRelay(
            relay_id="RELAY_500KV_MAIN_01",
            tier="500KV_MAIN",
            pickup_current_a=2400.0,
            time_dial_setting=0.45,
            curve_type="IEC_VERY_INVERSE",
            ct_ratio=3000.0 / 5.0,
            backup_for_relay_ids=["RELAY_34_5KV_FEEDER_A", "RELAY_34_5KV_FEEDER_B"],
        ),
        ProtectionRelay(
            relay_id="RELAY_34_5KV_FEEDER_A",
            tier="34_5KV_FEEDER",
            pickup_current_a=1200.0,
            time_dial_setting=0.25,
            curve_type="IEC_VERY_INVERSE",
            ct_ratio=1500.0 / 5.0,
            backup_for_relay_ids=["RELAY_480V_SUB_HALL_C"],
        ),
        ProtectionRelay(
            relay_id="RELAY_480V_SUB_HALL_C",
            tier="480V_SUB",
            pickup_current_a=600.0,
            time_dial_setting=0.15,
            curve_type="IEC_STANDARD_INVERSE",
            ct_ratio=800.0 / 5.0,
            backup_for_relay_ids=["RELAY_RPDU_RACK_42"],
        ),
        ProtectionRelay(
            relay_id="RELAY_RPDU_RACK_42",
            tier="RPDU_BRANCH",
            pickup_current_a=160.0,
            time_dial_setting=0.05,
            curve_type="IEC_EXTREMELY_INVERSE",
            ct_ratio=200.0 / 5.0,
            backup_for_relay_ids=[],
        ),
    ]

    # Fault event: High-current short circuit at Rack 42 branch bus
    fault = FaultTransientEvent(
        fault_id="FAULT_RPDU_FLASH_001",
        location_bus="BUS_RPDU_RACK_42",
        fault_current_a=2800.0,
        duration_ms=45.0,
    )

    # 2. 4D Tensor-Parallel Megatron-LM Pipeline Stages (16 stages = 960 MW cluster)
    stages: List[PipelineStageConfig] = []
    for idx in range(16):
        stages.append(
            PipelineStageConfig(
                stage_id=f"pipeline_stage_{idx:02d}",
                pp_index=idx,
                tp_degree=8,
                dp_degree=64,
                cp_degree=8,
                nominal_freq_ghz=1.98,
                min_freq_ghz=1.10,
                forward_weight_tflops=450.0,
                backward_weight_tflops=900.0,
                num_layers=8,
            )
        )

    # 3. Hybrid Storage Complex Impedance Strings & Pyrofuses
    strings: List[BatteryStringImpedance] = [
        BatteryStringImpedance(
            string_id="STR_01_EDLC_SUPERCAP",
            medium_type="SUPERCAPACITOR",
            r_ohmic_mohm=0.85,
            r_charge_transfer_mohm=0.12,
            c_double_layer_farad=450.0,
            warburg_sigma=0.015,
            pyrofuse_i2t_threshold=8.5e6,
            current_i2t_accumulated=1.2e5,
        ),
        BatteryStringImpedance(
            string_id="STR_02_MAGLEV_FLYWHEEL",
            medium_type="FLYWHEEL_INVERTER",
            r_ohmic_mohm=1.40,
            r_charge_transfer_mohm=0.25,
            c_double_layer_farad=120.0,
            warburg_sigma=0.035,
            pyrofuse_i2t_threshold=12.0e6,
            current_i2t_accumulated=2.5e5,
        ),
        BatteryStringImpedance(
            string_id="STR_03_SODIUM_ION_BESS",
            medium_type="SODIUM_ION",
            r_ohmic_mohm=4.20,
            r_charge_transfer_mohm=1.85,
            c_double_layer_farad=85.0,
            warburg_sigma=0.110,
            pyrofuse_i2t_threshold=6.5e6,
            current_i2t_accumulated=4.8e5,
        ),
        BatteryStringImpedance(
            string_id="STR_04_LFP_BUFFER",
            medium_type="LFP",
            r_ohmic_mohm=5.80,
            r_charge_transfer_mohm=2.40,
            c_double_layer_farad=60.0,
            warburg_sigma=0.160,
            pyrofuse_i2t_threshold=5.0e6,
            current_i2t_accumulated=6.2e5,
        ),
    ]

    # 4. Campbell Resonant Speed Bands for Aeroderivative Gas Turbine (0 to 3600 RPM)
    bands: List[ResonantSpeedBand] = [
        ResonantSpeedBand(
            band_id="BAND_01_FIRST_BENDING",
            min_rpm=1180.0,
            max_rpm=1320.0,
            max_dwell_ms=120.0,
            mode_name="1st Shaft Lateral Bending Mode",
        ),
        ResonantSpeedBand(
            band_id="BAND_02_TORSIONAL_COUPLING",
            min_rpm=2280.0,
            max_rpm=2420.0,
            max_dwell_ms=150.0,
            mode_name="Generator Torsional Natural Frequency",
        ),
    ]

    # 5. Grid Telemetry Samples (Jittery SCADA / ICCP link with intermittent delay spike)
    telemetry: List[GridTelemetrySample] = [
        GridTelemetrySample("sample_01", 59.982, 18.4, False),
        GridTelemetrySample("sample_02", 59.978, 22.1, False),
        GridTelemetrySample("sample_03", 59.980, 48.0, False),
        GridTelemetrySample("sample_04", 59.975, 780.0, False),  # Network jitter packet stall
        GridTelemetrySample("sample_05", 59.979, 15.2, False),
    ]

    return relays, fault, stages, strings, bands, telemetry


class ApexInfrastructureKillSwitchEngine:
    """
    Unified Orchestrator across the 5 Core Infrastructure & Physical Kill-Switch Solvers.
    """

    def __init__(self):
        self.relay_solver = ProtectionRelayCoordinationSolver(min_cti_ms=200.0)
        self.dvfs_scheduler = TensorParallelDVFSBubbleScheduler(power_scaling_exponent=2.8)
        self.bms_solver = ImpedanceCurrentSplittingBMSSolver(max_allowable_pyrofuse_stress=0.70)
        self.turbine_solver = TurbineResonanceGovernorSolver(target_sync_rpm=3600.0)
        self.deadman_solver = LatencyDiscountedAMMDeadManSolver(
            nominal_frequency_hz=60.0, trip_threshold_hz=59.50
        )

    def coordinate_protection_relays(
        self, fault: FaultTransientEvent, relays: List[ProtectionRelay]
    ) -> RelayCoordinationReport:
        """Solves relay trip grading and verifies CTI >= 200ms to eliminate sympathetic tripping."""
        return self.relay_solver.evaluate_fault_coordination(fault, relays)

    def schedule_tensor_dvfs_shed(
        self, target_power_ceiling_mw: float, stages: List[PipelineStageConfig]
    ) -> ClusterSheddingScheduleReport:
        """Sheds 750 MW in <2ms via synchronized 1F1B bubble injection without checkpoint loss."""
        return self.dvfs_scheduler.schedule_power_shed(target_power_ceiling_mw, stages)

    def split_impedance_currents(
        self,
        total_current_a: float,
        strings: List[BatteryStringImpedance],
        frequency_hz: float = 100.0,
    ) -> ImpedanceSplittingReport:
        """Balances 100 Hz pulse currents across complex impedances to keep pyrofuses intact."""
        return self.bms_solver.optimize_current_split(total_current_a, strings, frequency_hz)

    def optimize_turbine_governor(
        self, duration_s: float, bands: List[ResonantSpeedBand]
    ) -> TurbineRampTrajectoryReport:
        """Computes fast-start fuel governor trajectory avoiding Campbell resonant dwell times."""
        return self.turbine_solver.optimize_ramp_trajectory(duration_s, bands)

    def clear_deadman_market(
        self, telemetry: List[GridTelemetrySample], local_pmu_hz: float
    ) -> DeadManClearingReport:
        """Defuses false-trip network jitter traps while capturing peak ancillary revenue."""
        return self.deadman_solver.filter_telemetry_and_clear_market(telemetry, local_pmu_hz)

    def run_full_pipeline_benchmark(
        self, iterations: int = 50
    ) -> KillSwitchPipelineBenchmarkReport:
        """
        Executes end-to-end multi-physics benchmark across all 5 kill-switch solvers.
        """
        start_t = time.perf_counter()
        relays, fault, stages, strings, bands, telemetry = generate_synthetic_killswitch_state()

        # 1. Benchmark Relay Coordination
        relay_times: List[float] = []
        relay_reports: List[RelayCoordinationReport] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = self.coordinate_protection_relays(fault, relays)
            relay_times.append((time.perf_counter() - t0) * 1_000_000.0)
            relay_reports.append(r)
        last_relay = relay_reports[-1]

        # 2. Benchmark Tensor DVFS Shedding
        dvfs_times: List[float] = []
        dvfs_reports: List[ClusterSheddingScheduleReport] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = self.schedule_tensor_dvfs_shed(250.0, stages)
            dvfs_times.append((time.perf_counter() - t0) * 1_000_000.0)
            dvfs_reports.append(r)
        last_dvfs = dvfs_reports[-1]

        # 3. Benchmark Complex Impedance Current Splitting
        bms_times: List[float] = []
        bms_reports: List[ImpedanceSplittingReport] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = self.split_impedance_currents(25_000.0, strings, 100.0)
            bms_times.append((time.perf_counter() - t0) * 1_000_000.0)
            bms_reports.append(r)
        last_bms = bms_reports[-1]

        # 4. Benchmark Turbine Resonance Governor
        turbine_times: List[float] = []
        turbine_reports: List[TurbineRampTrajectoryReport] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = self.optimize_turbine_governor(30.0, bands)
            turbine_times.append((time.perf_counter() - t0) * 1_000_000.0)
            turbine_reports.append(r)
        last_turbine = turbine_reports[-1]

        # 5. Benchmark Dead-Man Market Clearing
        deadman_times: List[float] = []
        deadman_reports: List[DeadManClearingReport] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = self.clear_deadman_market(telemetry, 59.981)
            deadman_times.append((time.perf_counter() - t0) * 1_000_000.0)
            deadman_reports.append(r)
        last_deadman = deadman_reports[-1]

        total_runtime_ms = (time.perf_counter() - start_t) * 1000.0

        return KillSwitchPipelineBenchmarkReport(
            total_runtime_ms=round(total_runtime_ms, 2),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            relay_coordination_summary={
                "avg_solve_latency_us": round(sum(relay_times) / len(relay_times), 2),
                "clearing_time_ms": float(last_relay.clearing_time_ms),
                "sympathetic_trips_prevented": float(last_relay.sympathetic_trips_prevented),
                "campus_isolated": 1.0 if last_relay.campus_isolated else 0.0,
            },
            tensor_dvfs_summary={
                "avg_solve_latency_us": round(sum(dvfs_times) / len(dvfs_times), 2),
                "initial_power_mw": float(last_dvfs.initial_power_mw),
                "throttled_power_mw": float(last_dvfs.throttled_power_mw),
                "reduction_pct": float(last_dvfs.power_reduction_pct),
            },
            impedance_bms_summary={
                "avg_solve_latency_us": round(sum(bms_times) / len(bms_times), 2),
                "max_pyrofuse_stress": float(last_bms.max_pyrofuse_stress_ratio),
                "current_variance": float(last_bms.current_variance_a2),
                "pyrofuse_tripped": 1.0 if last_bms.pyrofuse_tripped else 0.0,
            },
            turbine_governor_summary={
                "avg_solve_latency_us": round(sum(turbine_times) / len(turbine_times), 2),
                "achieved_rpm": float(last_turbine.achieved_rpm),
                "max_resonance_dwell_ms": float(last_turbine.max_resonance_dwell_ms),
                "synchronization_locked": 1.0 if last_turbine.synchronization_locked else 0.0,
            },
            deadman_clearing_summary={
                "avg_solve_latency_us": round(sum(deadman_times) / len(deadman_times), 2),
                "arbitrage_captured_usd": float(last_deadman.arbitrage_captured_usd),
                "false_trip_defused": 1.0 if last_deadman.false_trip_defused else 0.0,
                "deadman_switch_fired": 1.0 if last_deadman.deadman_switch_fired else 0.0,
            },
        )
