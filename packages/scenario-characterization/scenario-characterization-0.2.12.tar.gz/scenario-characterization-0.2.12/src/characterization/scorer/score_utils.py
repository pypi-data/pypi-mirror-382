import numpy as np

from characterization.utils.common import EPS

SUPPORTED_SCORERS = ["individual", "interaction", "safeshift"]


def simple_individual_score(
    speed: float = 0.0,
    speed_weight: float = 1.0,
    speed_detection: float = 1.0,
    acceleration: float = 0.0,
    acceleration_weight: float = 1.0,
    acceleration_detection: float = 1.0,
    deceleration: float = 0.0,
    deceleration_weight: float = 1.0,
    deceleration_detection: float = 1.0,
    jerk: float = 0.0,
    jerk_weight: float = 1.0,
    jerk_detection: float = 1.0,
    waiting_period: float = 0.0,
    waiting_period_weight: float = 1.0,
    waiting_period_detection: float = 1.0,
) -> float:
    """Aggregates a simple score for an agent using weighted feature values.

    Args:
        speed (float): Speed of the agent.
        speed_weight (float): Weight for the speed feature.
        speed_detection (float): Detection threshold for the speed feature.
        acceleration (float): Acceleration of the agent.
        acceleration_weight (float): Weight for the acceleration feature.
        acceleration_detection (float): Detection threshold for the acceleration feature.
        deceleration (float): Deceleration of the agent.
        deceleration_weight (float): Weight for the deceleration feature.
        deceleration_detection (float): Detection threshold for the deceleration feature.
        jerk (float): Jerk of the agent.
        jerk_weight (float): Weight for the jerk feature.
        jerk_detection (float): Detection threshold for the jerk feature.
        waiting_period (float): Waiting period of the agent.
        waiting_period_weight (float): Weight for the waiting period feature.
        waiting_period_detection (float): Detection threshold for the waiting period feature.

    Returns:
        float: The aggregated score for the agent.
    """
    # Detection values are roughly obtained from: https://arxiv.org/abs/2202.07438
    return (
        speed_weight * min(speed_detection, speed)
        + acceleration_weight * min(acceleration_detection, acceleration)
        + deceleration_weight * min(deceleration_detection, deceleration)
        + jerk_weight * min(jerk_detection, jerk)
        + waiting_period_weight * min(waiting_period_detection, waiting_period)
    )


def simple_interaction_score(
    collision: float = 0.0,
    collision_weight: float = 1.0,
    mttcp: float = np.inf,
    mttcp_weight: float = 1.0,
    mttcp_detection: float = 1.0,
    thw: float = np.inf,
    thw_weight: float = 1.0,
    thw_detection: float = 1.0,
    ttc: float = np.inf,
    ttc_weight: float = 1.0,
    ttc_detection: float = 1.0,
    drac: float = 0.0,
    drac_weight: float = 1.0,
    drac_detection: float = 1.0,
) -> float:
    """Aggregates a simple interaction score for an agent pair using weighted feature values.

    Args:
        collision (float): Collision indicator (1 if collision occurred, else 0).
        collision_weight (float): Weight for the collision feature.
        mttcp (float): Minimum time to closest point of approach.
        mttcp_weight (float): Weight for the mttcp feature.
        mttcp_detection (float): Detection threshold for the mttcp feature.
        thw (float): Time headway.
        thw_weight (float): Weight for the thw feature.
        thw_detection (float): Detection threshold for the thw feature.
        ttc (float): Time to collision.
        ttc_weight (float): Weight for the ttc feature.
        ttc_detection (float): Detection threshold for the ttc feature.
        drac (float): Deceleration rate to avoid collision.
        drac_weight (float): Weight for the drac feature.
        drac_detection (float): Detection threshold for the drac feature.

    Returns:
        float: The aggregated score for the agent pair.
    """
    inv_mttcp = 1.0 / (mttcp + EPS)
    inv_thw = 1.0 / (thw + EPS)
    inv_ttc = 1.0 / (ttc + EPS)
    return (
        collision_weight * collision
        + mttcp_weight * min(mttcp_detection, inv_mttcp)
        + thw_weight * min(thw_detection, inv_thw)
        + ttc_weight * min(ttc_detection, inv_ttc)
        + min(drac_detection, drac_weight * drac)
    )


INDIVIDUAL_SCORE_FUNCTIONS = {
    "simple": simple_individual_score,
}
INTERACTION_SCORE_FUNCTIONS = {
    "simple": simple_interaction_score,
}
