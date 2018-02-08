import numpy as np
from sklearn.utils import check_random_state
from sklearn.datasets import make_regression
from sklearn.datasets.samples_generator import make_blobs

def _combFeat(n, size, strRelFeat,randomstate):
        # Split each strongly relevant feature into linear combination of it
        weakFeats = np.zeros((n,size))
        for x in range(size):
            cofact = 2 * randomstate.rand() - 1
            weakFeats[:,x] = cofact  * strRelFeat
        return weakFeats

def _dummyFeat(n,randomstate):
        return  randomstate.randn(n)

def _repeatFeat(feats, i,randomstate):
        i_pick = randomstate.choice(i)
        return feats[:, i_pick]

def genData(**args):
    """ 
    Deprecated Method call generating Classification data
    """
    return genClassificationData(**args)

def _checkParam(n_samples: int=100, n_features: int=2,
                          n_redundant: int=0, strRel: int=1,
                          n_repeated: int=0,
                          flip_y: float=0,noise: float = 1, partition=None,**kwargs):
    if not 1 < n_samples:
        raise ValueError("We need at least 2 samples.")
    if not 0 < n_features:
        raise ValueError("We need at least one feature.")
    if not 0 <= flip_y < 1:
        raise ValueError("Flip percentage has to be between 0 and 1.")
    if not n_redundant+n_repeated+strRel<= n_features:
        raise ValueError("Inconsistent number of features")
    if strRel + n_redundant < 1:
        raise ValueError("No informative features.")
    if strRel == 0 and n_redundant < 2:
        raise ValueError("Redundant features have per definition more than one member.")
    if partition is not None:
        if sum(partition) != n_redundant:
            raise ValueError("Sum of partition values should yield number of redundant features.")
        if 0 in partition or 1 in partition:
            raise ValueError("Subset defined in Partition needs at least 2 features. 0 and 1 is not allowed.")
    print("Generating dataset with d={},n={},strongly={},weakly={}, partition of weakly={}".format(n_features,n_samples,strRel,n_redundant,partition))

def _fillVariableSpace(X_informative, random_state: object, n_samples: int=100, n_features: int=2,  
                          n_redundant: int=0, strRel: int=1,
                          n_repeated: int=0,
                          noise: float = 1,partition=None,**kwargs):
        X = np.zeros((int(n_samples), int(n_features)))
        X[:, :strRel] = X_informative[:, :strRel]
        holdout = X_informative[:, strRel:]
        i = strRel
        
        pi = 0
        for x in range(len(holdout.T)):
            size = partition[pi]
            X[:, i:i + size] = _combFeat(n_samples, size, holdout[:, x], random_state)
            i += size
            pi +=1

        for x in range(n_repeated):
            X[:, i] = _repeatFeat(X[:, :i], i, random_state)
            i += 1    
        for x in range(n_features - i):
            X[:, i] = _dummyFeat(n_samples, random_state)
            i += 1

        return X

def _partition_min_max(n, k, l, m):
    '''n is the integer to partition, k is the length of partitions, 
    l is the min partition element size, m is the max partition element size '''
    # Source: https://stackoverflow.com/a/43015372

    if k < 1:
        raise StopIteration
    if k == 1:
        if n <= m and n>=l :
            yield (n,)
        raise StopIteration
    for i in range(l,m+1):
        for result in _partition_min_max(n-i,k-1,i,m):                
            yield result+(i,)

def genClassificationData(n_samples: int=100, n_features: int=2,
                          n_redundant: int=0, strRel: int=1,
                          n_repeated: int=0,
                          flip_y: float=0, random_state: object=None,
                          partition=None):
    """Generate synthetic classification data
    
    Parameters
    ----------
    n_samples : int, optional
        Number of samples
    n_features : int, optional
        Number of features
    n_redundant : int, optional
        Number of features which are part of redundant subsets (weakly relevant)
    strRel : int, optional
        Number of features which are mandatory for the underlying model (strongly relevant)
    n_repeated : int, optional
        Number of features which are clones of existing ones. 
    flip_y : float, optional
        Ratio of samples randomly switched to wrong class.
    random_state : object, optional
        Randomstate object used for generation.
    
    Returns
    -------
    X : array of shape [n_samples, n_features]
        The generated samples.
    y : array of shape [n_samples]
        The output classes.
    
    Raises
    ------
    ValueError
        Description
    ValueError
    Wrong parameters for specified amonut of features/samples.
    

    Examples
    ---------
    >>> X,y = genClassificationData(n_samples=200)
    Generating dataset with d=2,n=200,strongly=1,weakly=0, partition of weakly=None
    >>> X.shape
    (200, 2)
    >>> y.shape
    (200,)
    """
    _checkParam(**locals())
    random_state = check_random_state(random_state)

    def genStrongRelFeatures(n, strRel,random_state):

        width = 2
        stddev = 1.8
        centers = np.zeros((2,strRel))
        centers[0] = width
        centers[1] = -width

        X, y = make_blobs(n_samples=n, centers=centers, cluster_std=stddev, n_features=strRel, random_state=random_state)
        
        y[y == 0] = -1

        return X, y

    X = np.zeros((n_samples,n_features))

    # Find partitions which defíne the weakly relevant subsets
    if partition is None and n_redundant > 0:
        partition =  [n_redundant]
        part_size = 1    
    elif partition is not None:
        part_size = len(partition)
    else:
        part_size = 0

    X_informative, Y = genStrongRelFeatures(n_samples, strRel + part_size, random_state)
    
    X = _fillVariableSpace(X_informative, random_state, n_samples = n_samples, n_features = n_features,  
                          n_redundant = n_redundant, strRel = strRel,
                          n_repeated = n_repeated, partition = partition)

    if flip_y > 0:
        n_flip = int(flip_y * n_samples)
        Y[random_state.choice(n_samples,n_flip)] *= -1

    return X, Y


def genRegressionData(n_samples: int = 100, n_features: int = 2, n_redundant: int = 0, strRel: int = 1,
                      n_repeated: int = 0, noise: float = 0, random_state: object = None,
                      partition = None) -> object:
    """Generate synthetic regression data
    
    Parameters
    ----------
    n_samples : int, optional
        Number of samples
    n_features : int, optional
        Number of features
    n_redundant : int, optional
        Number of features which are part of redundant subsets (weakly relevant)
    strRel : int, optional
        Number of features which are mandatory for the underlying model (strongly relevant)
    n_repeated : int, optional
        Number of features which are clones of existing ones. 
    noise : float, optional
        Noise of the created samples around ground truth.
    random_state : object, optional
        Randomstate object used for generation.
    
    Returns
    -------
    X : array of shape [n_samples, n_features]
        The generated samples.
    y : array of shape [n_samples]
        The output values (target).
    
    Raises
    ------
    ValueError
    Wrong parameters for specified amonut of features/samples.
    """ 

    _checkParam(**locals())
    random_state = check_random_state(random_state)

    X = np.zeros((int(n_samples), int(n_features)))

    # Find partitions which defíne the weakly relevant subsets
    if partition is None and n_redundant > 0:
        partition =  [n_redundant]
        part_size = 1    
    elif partition is not None:
        part_size = len(partition)
    else:
        part_size = 0

    X_informative, Y = make_regression(n_features=int(strRel + part_size),
                                        n_samples=int(n_samples),
                                        noise=noise,
                                        n_informative=int(strRel + part_size),
                                        random_state=random_state,
                                        shuffle=False)

    X = _fillVariableSpace(X_informative, random_state, n_samples = n_samples, n_features = n_features,  
                          n_redundant = n_redundant, strRel = strRel,
                          n_repeated = n_repeated,
                          noise = noise, partition = partition)

    return X, Y
