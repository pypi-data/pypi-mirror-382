import numpy as np
import scipy.optimize as opt

from .base import DetectionModule, ObjectiveType
from ..Logger import LOG
from ..exceptions import InputError

from typing import Dict, Any, Callable, Optional

class ParamMinDetectionModule(DetectionModule):
    """ 
    Detection module to halt continuation beyond `param_min` - if the value is set by the user.
    The `update` function only fires on the first point beyond this minimal paramter value, at
    the moment of crossing, not anymore after.

    `localize` computes the point with `p = param_min` on the continuation boundary.
    """

    def __init__(self,
                 G : ObjectiveType,
                 u0 : np.ndarray,
                 p0 : float,
                 sp : Dict[str, Any],
                 param_min_value : float) -> None:
        """
        Initialize new detection module for the problem.

        Parameters
        ----------
        G : Callable
            The continuation objective function.
        u0 : ndarray
            The initial state on the branch
        p0 : ndarray
            The initial parameter value on the branch
        sp : Optional Dict
            The solver parameters.

        Returns
        -------
        Nothing.
        """
        super().__init__("PARAM_MIN", G, u0, p0, sp)
        self.param_min_value = param_min_value

        if self.param_min_value > p0:
            raise InputError(f"p0 cannot be smaller than param_min, got {p0} and {self.param_min_value}")

    def initializeBranch(self,
                         x: np.ndarray,
                         tangent: np.ndarray) -> None:
        self.u_prev = x[:self.M]
        self.p_prev = x[self.M]
    
    def update(self,
               F : Callable[[np.ndarray], np.ndarray],
               x_new : np.ndarray,
               tangent_new : np.ndarray) -> bool:
        # Update the internal state
        self.u_new = x_new[:self.M]
        self.p_new = x_new[self.M]

        # Return true if we passed `param_max`. Otherwise update the internal state.
        if self.p_new < self.param_min_value and self.p_prev >= self.param_min_value:
            LOG.info(f'Stopping Continuation Along this Branch. PARAM_MIN {self.param_min_value} reached.')
            return True
        
        self.u_prev = self.u_new
        self.p_prev = self.p_new
        return False

    def localize(self) -> Optional[np.ndarray]:
        if self.p_new == self.p_prev:
            alpha = 0.0
        else:
            alpha = (self.param_min_value - self.p_prev) / (self.p_new - self.p_prev)
        u_guess = self.u_prev + alpha * (self.u_new - self.u_prev)

        # Use Newton-Krylov to determine the exact point on the branch where `p = param_min`.
        objective = lambda u : self.G(u, self.param_min_value)
        rdiff = self.sp["rdiff"]
        tolerance = self.sp["tolerance"]
        try:
            u_param_min = opt.newton_krylov(objective, u_guess, rdiff=rdiff, f_tol=tolerance)
        except opt.NoConvergence as e:
            u_param_min = e.args[0]

        # Return the full state at param_min
        return np.append(u_param_min, self.param_min_value)
