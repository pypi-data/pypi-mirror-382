import numpy as np

from .base import DetectionModule, ObjectiveType
from ._bifurcation import test_fn_jacobian_multi, computeBifurcationPoint
from ..Logger import LOG
from ..exceptions import InputError

from dataclasses import dataclass
from typing import Dict, Callable, Any, Optional

@dataclass
class BifurcationState:
    x : np.ndarray
    tangent : np.ndarray
    w_values : np.ndarray
    w_vectors : np.ndarray

class BifurcationDetectionModule(DetectionModule):
    """
    Bifurcation detection module that computes the values of the test functions at every point.
    The number of test functions should be set via `n_bifurcation_vectors` in the solver parameters. 
    Default is min(3, M). 

    The Jacobian-based test functions and bifurcation-point localizers are implemented in _bifurcation.py.
    """
    def __init__(self,
                 G: ObjectiveType,
                 u0 : np.ndarray,
                 p0 : float,
                 sp: Dict[str, Any]) -> None:
        super().__init__("BP", G, u0, p0, sp)

        # Do checks
        self.n_bifurcation_vectors = sp.get("n_bifurcation_vectors", min(3, self.M))
        if self.n_bifurcation_vectors < 0:
            raise InputError(f"number of bifurcation vectors must be a positive integer, got {self.n_bifurcation_vectors}.")
        
    def _orthonormalize_lr(self,
                           tangent : np.ndarray) -> None:
        """
        Orthonormalize the rows of l_vectors and r_vectors (shape (k, M+1) each).
        Additionally, make each row of l_vectors orthogonal to the given tangent (length M+1).

        Parameters
        ----------
        tangent : ndarray
            The current tangent vector.
        """
        extended_r_vectors = self.r_vectors.T
        extended_l_vectors = np.concatenate((tangent[:,np.newaxis], self.l_vectors.T), axis=1)
        extended_r_vectors, _ = np.linalg.qr(extended_r_vectors, mode='reduced')
        extended_l_vectors, _ = np.linalg.qr(extended_l_vectors, mode='reduced')

        self.l_vectors =  extended_l_vectors[:,1:].T
        self.r_vectors = extended_r_vectors.T

    def initializeBranch(self,
                         x : np.ndarray,
                         tangent : np.ndarray) -> None:
        """
        Initialize the Bifurcation detection toolkit by creating the first (empty)
        bifurcation state.

        Parameters
        ----------
        x : ndarray
            The (typically) initial point on the branch.
        tangent : ndarray
            The tangent to the initial point.
        """
        
        # Sample the l- and r-vectors for this test function.
        rng = np.random.RandomState(seed=self.sp["seed"])
        self.r_vectors = rng.normal(0.0, 1.0, (self.n_bifurcation_vectors, self.M+1))
        self.l_vectors = rng.normal(0.0, 1.0, (self.n_bifurcation_vectors, self.M+1))
        self._orthonormalize_lr(tangent)

        # Initialize the BifurcationState along this branch
        init_w_vectors = np.zeros_like(self.r_vectors)
        init_w_values = np.zeros(self.n_bifurcation_vectors)
        self.prev_state = BifurcationState(np.copy(x), np.copy(tangent), init_w_values, init_w_vectors)

    def update(self,
               F : Callable[[np.ndarray], np.ndarray],
               x_new : np.ndarray,
               tangent_new : np.ndarray) -> bool:

        # Calculate the test function for every l- and r-vector
        w_values, w_vectors = test_fn_jacobian_multi(F, x_new, self.l_vectors, self.r_vectors, self.prev_state.w_vectors, self.sp)
        self.new_state = BifurcationState(np.copy(x_new), np.copy(tangent_new), w_values, w_vectors)

        # Test for a bifurcation point
        is_bf =  (w_values * self.prev_state.w_values < 0.0) & (np.abs(self.prev_state.w_values) < 1000.0) & (np.abs(w_values) < 1000.0)
        if np.any(is_bf):
            index = np.where(is_bf)[0].min()
            LOG.info(f'Sign change detected {self.prev_state.w_values} {self.new_state.w_values} {index}')
            self.F_bf = F
            return True
        
        # Else update the internal state
        self.prev_state = self.new_state
        return False
    
    def localize(self) -> Optional[np.ndarray]:
        index = np.argwhere(self.prev_state.w_values * self.new_state.w_values < 0.0)[0].min()
        is_bf, x_bf, alpha_bf = computeBifurcationPoint(self.F_bf, 
                                                        self.prev_state.x, 
                                                        self.new_state.x, 
                                                        self.l_vectors, 
                                                        self.r_vectors, 
                                                        self.prev_state.w_vectors, 
                                                        index, 
                                                        self.M, 
                                                        self.sp)
        if is_bf:
            LOG.info(f'Bifurcation Point at {x_bf}')
            return x_bf
        
        LOG.info('Erroneous sign change in bifurcation detection, most likely due to blowup. Continuing along this branch.')
        self.prev_state = self.new_state
        return None