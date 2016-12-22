from abc import ABCMeta, abstractmethod
import cvxpy as cvx
import numpy as np


class BaseProblem(object):
    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None):
        # General data
        self.d = d
        self.n = n
        self.X = X
        self.Y = np.array([Y, ] * 1)
        # Dimension specific data
        self.di = di
        # Solver parameters
        self.kwargs = kwargs

        self.problem = None
        self._constraints = None
        self._objective = None

    def solve(self):
        self.problem = cvx.Problem(self._objective, self._constraints)
        self.problem.solve(**self.kwargs)
        return self


class BaseClassificationProblem(BaseProblem):
    """Base class for all common optimization problems."""

    __metaclass__ = ABCMeta

    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None, C=1, svmloss=1, L1=1):
        super().__init__(di=di, d=d, n=n, kwargs=kwargs, X=X, Y=Y)
        # General data
        self.L1 = L1
        self.svmloss = svmloss
        self.C = C
        self.M = 2 * L1
        # Solver parameters
        self.kwargs = kwargs
        # Solver Variables
        self.xp = cvx.Variable(d)  # x' , our opt. value
        self.omega = cvx.Variable(d)  # complete linear weight vector
        self.b = cvx.Variable()  # shift
        self.eps = cvx.Variable(n)  # slack variables

        self._constraints = [
            # points still correctly classified with soft margin
            cvx.mul_elemwise(self.Y.T, self.X * self.omega - self.b) >= 1 - self.eps,
            self.eps >= 0,
            # L1 reg. and allow slack
            cvx.norm(self.omega, 1) + self.C * cvx.sum_squares(self.eps) <= self.L1 + self.C * self.svmloss
        ]

class MinProblemClassification(BaseClassificationProblem):
    """Class for minimization."""

    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None, C=1, svmloss=1, L1=1):
        super().__init__(di=di, d=d, n=n, kwargs=kwargs, X=X, Y=Y, C=C, svmloss=svmloss, L1=L1)

        self._constraints.extend(
            [
                cvx.abs(self.omega) <= self.xp,
            ])

        self._objective = cvx.Minimize(self.xp[self.di])


class MaxProblem1(BaseClassificationProblem):
    """Class for maximization."""

    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None, C=1, svmloss=1, L1=1):
        super().__init__(di=di, d=d, n=n, kwargs=kwargs, X=X, Y=Y, C=C, svmloss=svmloss, L1=L1)

        self._constraints.extend([
            cvx.abs(self.omega) <= self.xp,
            self.xp[self.di] <= self.omega[self.di],
            self.xp[self.di] <= -(self.omega[self.di]) + self.M
        ])

        self._objective = cvx.Maximize(self.xp[self.di])


class MaxProblem2(BaseClassificationProblem):
    """Class for maximization."""

    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None, C=1, svmloss=1, L1=1):
        super().__init__(di=di, d=d, n=n, kwargs=kwargs, X=X, Y=Y, C=C, svmloss=svmloss, L1=L1)

        self._constraints.extend([
            cvx.abs(self.omega) <= self.xp,
            self.xp[self.di] <= -(self.omega[self.di]),
            self.xp[self.di] <= (self.omega[self.di]) + self.M
        ])

        self._objective = cvx.Maximize(self.xp[self.di])

'''
#############
            ##### REGRESSION
#############
'''

class BaseRegressionProblem(BaseProblem):

    __metaclass__ = ABCMeta

    def __init__(self, di=0, d=0, n=0, kwargs=None, X=None, Y=None, C=1,epsilon=0.1, svrloss=1, L1=1):
        super().__init__(di=di, d=d, n=n, kwargs=kwargs, X=X, Y=Y)
        # General data
        self.svrloss = svrloss
        self.epsilon = epsilon
        self.L1 = L1
        self.C = C
        self.M = 2 * L1
        # Solver parameters
        self.kwargs = kwargs
        # Solver Variables
        self.xp = cvx.Variable(d)  # x' , our opt. value
        self.omega = cvx.Variable(d)  # complete linear weight vector
        self.b = cvx.Variable()  # shift
        self.posSlack = cvx.Variable(n)  # slack variables
        self.negSlack = cvx.Variable(n)  # slack variables


        self._constraints = [

        ]

