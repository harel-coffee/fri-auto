import numpy as np
from sklearn.utils import check_X_y

from fri.base import FRIBase
from fri.l1models import L1OrdinalRegressor
from fri.optproblems import BaseOrdinalRegressionProblem
import scipy.stats


class FRIOrdinalRegression(FRIBase):
    """Class for performing FRI on ordinal regression data.
    
    Parameters
    ----------
    C : float , optional
        Regularization parameter, default obtains the hyperparameter through gridsearch optimizing accuracy
    random_state : object
        Set seed for random number generation.
    n_resampling : integer ( Default = 3)
        Number of probe feature permutations used. 
    iter_psearch : integer ( Default = 10)
        Amount of samples used for parameter search.
        Trade off between finer tuned model performance and run time of parameter search.
    parallel : boolean, optional
        Enables parallel computation of feature intervals
    optimum_deviation : float, optional (Default = 0.001)
        Rate of allowed deviation from the optimal solution (L1 norm of model weights).
        Default allows one percent deviation. 
        Allows for more relaxed optimization problems and leads to bigger intervals which are easier to interpret.
        Setting to 0 allows the best feature selection accuracy.
    debug : boolean
        Enable output of internal values for debugging purposes.
    
    Attributes
    ----------
    allrel_prediction_ : array of booleans
        Truth value for each feature if it is relevant (weakly OR strongly).
    interval_ : array [[lower_Bound_0,UpperBound_0],...,]
        Relevance bounds in 2D array format.
    optim_L1_ : double
        L1 norm of baseline model.
    optim_loss_ : double
        Sum of slack (loss) of baseline model.
    optim_model_ : fri.l1models object
        Baseline model
    optim_score_ : double
        Score of baseline model
    relevance_classes_ : array like
        Array with classification of feature relevances: 2 denotes strongly relevant, 1 weakly relevant and 0 irrelevant.
    unmod_interval_ : array like
        Same as `interval_` but not scaled to L1.
    
    """

    problemType = BaseOrdinalRegressionProblem

    def __init__(self, C=None, optimum_deviation=0.001, random_state=None,
                    parallel=False, n_resampling=3, iter_psearch=10, debug=False, **kwargs):
        super().__init__(C=C, random_state=random_state,
                         parallel=parallel,
                         n_resampling=n_resampling,iter_psearch=iter_psearch,
                         debug=debug, optimum_deviation=optimum_deviation)

        self.initModel = L1OrdinalRegressor

        # Define parameters which are optimized in the initial gridsearch
        self.tuned_parameters = {}

        # Only use parameter grid when no parameter is given
        if self.C is None:
            self.tuned_parameters["C"] = scipy.stats.reciprocal(a=1e-7,b=1e7)
        else:
            self.tuned_parameters["C"] = [self.C]


    def fit(self, X, y):

        """
        Fit model to data and provide feature relevance intervals
        Parameters
        ----------
        X : array_like
            standardized data matrix
        y : array_like
            response vector
        """

        # Check that X and y have correct shape
        X, y = check_X_y(X, y)

        # Get ordinal classes
        self.classes_ = np.unique(y)

        super().fit(X, y)