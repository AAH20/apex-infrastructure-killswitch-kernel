"""
Apex Infrastructure Kill-Switch & Protection Orchestration Kernel.
Zero external pip dependencies. Pure Python 3.10+.
"""

__version__ = "0.1.0"
__author__ = "Ahmed Hassan"

from apex_infrastructure_killswitch_kernel.engine import (
    ApexInfrastructureKillSwitchEngine,
    generate_synthetic_killswitch_state,
)

__all__ = [
    "ApexInfrastructureKillSwitchEngine",
    "generate_synthetic_killswitch_state",
]
