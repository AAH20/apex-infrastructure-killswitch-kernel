"""
Multi-Chemistry Complex Electrochemical Impedance Current Splitting & Pyrofuse Selectivity BMS Solver.
Computes frequency-dependent electrochemical impedance Z(omega) across supercapacitors,
vacuum flywheel inverters, and sodium-ion/LFP battery strings under 100 Hz pulse discharges.
Optimizes current allocation to eliminate current crowding and prevent spurious pyrofuse detonation.
Zero external pip dependencies. Pure Python 3.10+.
"""

from __future__ import annotations
import math
import time
from typing import List, Dict, Set, Tuple, Optional

from apex_infrastructure_killswitch_kernel.core.models import (
    BatteryStringImpedance,
    ImpedanceSplittingReport,
)


class ImpedanceCurrentSplittingBMSSolver:
    """
    Sub-millisecond Complex Impedance Balancing & Pyrofuse Safety Controller.
    Dispatches 100 Hz high-power pulse currents proportionally across heterogeneous strings
    to maintain thermal equilibrium and keep pyrofuse thermal stress well below detonation limits.
    """

    def __init__(self, max_allowable_pyrofuse_stress: float = 0.70):
        self.max_stress = max_allowable_pyrofuse_stress

    def compute_string_impedance_magnitude(
        self, string: BatteryStringImpedance, pulse_frequency_hz: float
    ) -> float:
        """
        Calculates magnitude of complex impedance |Z(omega)| in Ohms.
        Models Randles Equivalent Circuit: R_ohmic + (R_ct || C_dl) + Warburg impedance.
        """
        omega = 2.0 * math.pi * max(1.0, pulse_frequency_hz)
        r_omega = string.r_ohmic_mohm * 1e-3
        r_ct = string.r_charge_transfer_mohm * 1e-3
        c_dl = string.c_double_layer_farad
        sigma = string.warburg_sigma

        # Parallel R_ct and C_dl branch:
        # Z_p = R_ct / (1 + j * omega * R_ct * C_dl)
        tau = r_ct * c_dl
        denom = 1.0 + (omega * tau) ** 2

        real_p = r_ct / denom
        imag_p = -(omega * r_ct * tau) / denom

        # Warburg impedance: Z_w = sigma / sqrt(omega) * (1 - j)
        z_w_mag = sigma / math.sqrt(omega)
        real_w = z_w_mag
        imag_w = -z_w_mag

        # Total Real and Imaginary components
        z_real = r_omega + real_p + real_w
        z_imag = imag_p + imag_w

        return math.sqrt(z_real**2 + z_imag**2)

    def optimize_current_split(
        self,
        total_requested_current_a: float,
        strings: List[BatteryStringImpedance],
        pulse_frequency_hz: float = 100.0,
        pulse_duration_s: float = 0.005,  # 5 ms pulse in 100 Hz cycle
    ) -> ImpedanceSplittingReport:
        """
        Calculates optimal current distribution across strings to avoid pyrofuse detonation.
        """
        start_t = time.perf_counter()

        if total_requested_current_a <= 0 or not strings:
            elapsed_us = (time.perf_counter() - start_t) * 1_000_000.0
            return ImpedanceSplittingReport(
                total_requested_current_a=total_requested_current_a,
                pulse_frequency_hz=pulse_frequency_hz,
                current_allocations_a={s.string_id: 0.0 for s in strings},
                current_variance_a2=0.0,
                max_pyrofuse_stress_ratio=0.0,
                pyrofuse_tripped=False,
                solve_time_us=round(elapsed_us, 2),
            )

        # 1. Compute complex impedance magnitudes and admittances Y = 1 / |Z|
        admittances: Dict[str, float] = {}
        for s in strings:
            z_mag = self.compute_string_impedance_magnitude(s, pulse_frequency_hz)
            admittances[s.string_id] = 1.0 / max(1e-5, z_mag)

        total_admittance = sum(admittances.values())

        # 2. Natural physical current distribution based on admittances
        allocations: Dict[str, float] = {}
        stresses: Dict[str, float] = {}
        pyrofuse_tripped = False

        for s in strings:
            share = admittances[s.string_id] / max(1e-5, total_admittance)
            i_k = total_requested_current_a * share
            allocations[s.string_id] = round(i_k, 2)

            # Pyrofuse I^2 * t energy calculation
            i2t_pulse = (i_k**2) * pulse_duration_s
            total_i2t = s.current_i2t_accumulated + i2t_pulse
            stress_ratio = total_i2t / max(1e-3, s.pyrofuse_i2t_threshold)
            stresses[s.string_id] = stress_ratio

            if stress_ratio >= 1.0:
                pyrofuse_tripped = True

        # 3. Active Trimming if any string exceeds safety threshold
        max_stress = max(stresses.values()) if stresses else 0.0
        if max_stress > self.max_stress and not pyrofuse_tripped:
            # Rebalance excess current away from over-stressed strings to supercapacitors
            surplus_i = 0.0
            for s in strings:
                if stresses[s.string_id] > self.max_stress:
                    allowed_i = math.sqrt(
                        (self.max_stress * s.pyrofuse_i2t_threshold) / pulse_duration_s
                    )
                    diff = allocations[s.string_id] - allowed_i
                    if diff > 0:
                        allocations[s.string_id] = round(allowed_i, 2)
                        surplus_i += diff
            # Allocate surplus to highest capacity / supercap strings
            supercaps = [s for s in strings if s.medium_type == "SUPERCAPACITOR"]
            target_strings = supercaps if supercaps else strings
            added_per_target = surplus_i / len(target_strings)
            for ts in target_strings:
                allocations[ts.string_id] = round(allocations[ts.string_id] + added_per_target, 2)

            # Re-evaluate max stress
            for s in strings:
                i2t_pulse = (allocations[s.string_id] ** 2) * pulse_duration_s
                stresses[s.string_id] = (s.current_i2t_accumulated + i2t_pulse) / max(
                    1e-3, s.pyrofuse_i2t_threshold
                )
            max_stress = max(stresses.values())

        # 4. Statistical variance in string currents
        mean_i = sum(allocations.values()) / max(1, len(allocations))
        variance = sum((i - mean_i) ** 2 for i in allocations.values()) / max(
            1, len(allocations)
        )

        elapsed_us = (time.perf_counter() - start_t) * 1_000_000.0

        return ImpedanceSplittingReport(
            total_requested_current_a=round(total_requested_current_a, 2),
            pulse_frequency_hz=pulse_frequency_hz,
            current_allocations_a=allocations,
            current_variance_a2=round(variance, 2),
            max_pyrofuse_stress_ratio=round(max_stress, 4),
            pyrofuse_tripped=pyrofuse_tripped,
            solve_time_us=round(elapsed_us, 2),
        )
