"""Summary
"""
import pytest
from pytest import approx
from fri import genClassificationData, genRegressionData
from fri.bounds import LowerBound, UpperBound
from fri.l1models import L1HingeHyperplane, L1EpsilonRegressor
from sklearn.utils import check_random_state

from cvxpy import OPTIMAL

import numpy as np
from sklearn.preprocessing import StandardScaler


@pytest.fixture(scope="function")
def randomstate():
   """ pytest fixture providing numpy randomstate 
   
   Returns:
       TYPE: numpy randomstate
   """
   return check_random_state(1337)


def test_bounds(randomstate):
    """Test bound functions using very easy data with perfect separation
    
    Args:
        randomstate  pytest fixture providing numpy randomstate:
    """
    n_samples = 4
    n_features = 2
    X = [
        [1, 0],
        [2, 0],
        [-1, 0],
        [-2, 0],
        ]
    X = np.asarray(X)
    y = np.asarray([1, 1, -1, -1])

    C = 1
    l1init = L1HingeHyperplane(C=C)
    l1init.fit(X, y)
    
    bias = l1init.intercept_
    coef = l1init.coef_[0]
    L1 = np.linalg.norm(coef, ord=1)
    loss = np.abs(l1init.slack).sum()

    # Test the init parameters
    assert bias == approx(0)
    assert L1 == approx(1)
    assert loss == approx(0,abs=1e-7)
    assert abs(coef[0]) > abs(coef[1]) 
    assert coef[0] == approx(1)
    assert coef[1] == approx(0)

    kwargs = {"verbose":False,"solver":"ECOS","max_iters":1000}
    isRegression = False
    epsilon = None
    for current_dim in range(n_features):
        for b in (LowerBound,UpperBound):
                
            bound = b(current_dim, n_features,
                                n_samples, kwargs, L1,
                                loss, C, X, y,
                                regression=isRegression,
                                epsilon=epsilon)
            bound.solve()
            
            prob = bound.prob_instance.problem
            assert prob.status == OPTIMAL
            assert prob.value - abs(coef[current_dim]) <= 0.1
            assert bound.prob_instance.loss.value <= max(0.01,loss*1.001) # add a constant factor to handle numerical instabilities
            assert bound.prob_instance.weight_norm.value <= L1 * 1.00001


def test_bounds_twoMiss(randomstate):
    """ Test bound functions using data with two missclassifications
    
    Args:
        randomstate pytest fixture providing numpy randomstate:
    """
    n_samples = 4
    n_features = 2
    X = [
        [1, 0],
        [2, 0],
        [-1, 0],
        [-2, 0],
        [1, 0],# Missclassified
        [-1, 0], # Missclassified
        ]
    X = np.asarray(X)
    y = np.asarray([1, 1, -1, -1,-1, 1])

    C = 1
    l1init = L1HingeHyperplane(C=C)
    l1init.fit(X, y)
    
    bias = l1init.intercept_
    coef = l1init.coef_[0]
    L1 = np.linalg.norm(coef, ord=1)
    loss = np.abs(np.maximum(0, l1init.slack)).sum()
    
    # Test the init parameters
    assert bias == approx(0)
    assert L1 == approx(0.5)
    assert loss == approx(4,abs=1e-7)
    assert abs(coef[0]) > abs(coef[1]) 
    assert coef[0] == approx(0.5)
    assert coef[1] == approx(0)

    kwargs = {"verbose":False,"solver":"ECOS","max_iters":1000}
    isRegression = False
    epsilon = None

    for current_dim in range(n_features):
        for b in (LowerBound, UpperBound):
                
            bound = b(current_dim, n_features,
                                n_samples, kwargs, L1,
                                loss, C, X, y,
                                regression=isRegression,
                                epsilon=epsilon)
            bound.solve()
            
            prob = bound.prob_instance.problem
            assert prob.status == OPTIMAL
            assert prob.value - abs(coef[current_dim]) <= 0.1
            assert bound.prob_instance.loss.value <= max(0.011,loss*1.001) # add a constant factor to handle numerical instabilities
            assert bound.prob_instance.weight_norm.value <= L1 * 1.00001
