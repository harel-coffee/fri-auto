import pytest
from fri import genClassificationData, genRegressionData
from sklearn.utils import check_random_state
from sklearn.utils.testing import  assert_equal
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVR
from sklearn.metrics import r2_score


@pytest.fixture(scope="function")
def randomstate():
    return check_random_state(1337)


@pytest.mark.parametrize('n_samples', [2, 100, 10000])
@pytest.mark.parametrize('n_dim', [1, 5, 30, 100, 1000])
def test_shape(n_samples, n_dim):
    X, y = genClassificationData(n_samples=n_samples, n_features=n_dim)

    # Equal length
    assert_equal(len(X), len(y))
    # Correct parameters
    assert_equal(len(X), n_samples)
    assert_equal(X.shape[1], n_dim)


@pytest.mark.parametrize('wrong_param', [
    {"n_samples": 0},
    {"n_features": 0},
    {"n_samples": -1},
    {"n_features": -1},
    {"n_features": 2, "strRel": 3},
    {"n_features": 2, "n_redundant": 3},
    {"n_features": 2, "n_repeated": 3},
])
def test_wrong_values(wrong_param):
    with pytest.raises(ValueError) as exc:
        genClassificationData(**wrong_param)


@pytest.mark.parametrize('strong', [0, 1, 2, 20, 50])
@pytest.mark.parametrize("weak", [0, 1, 2, 20])
@pytest.mark.parametrize('repeated', [0, 1, 2, 5])
@pytest.mark.parametrize('flip_y', [0, 0.1, 1])
@pytest.mark.parametrize('noise', [0, 0.5, 1, 10])
@pytest.mark.parametrize('problem', ["regression", "classification"])
def test_all_feature_types(problem, strong, weak, repeated, flip_y, noise):
    n_samples = 10
    n_features = 100
    args = {"n_samples": n_samples, "n_features": n_features,
            "strRel": strong, "n_redundant": weak, "n_repeated": repeated}

    if problem == "regression":
        args["noise"] = noise
        gen = genRegressionData
    else:
        args["flip_y"] = flip_y
        gen = genClassificationData
        if flip_y == 1:
            with pytest.raises(ValueError):
                X, y = gen(**args)
            return

    if strong == 0 and weak < 2:
        with pytest.raises(ValueError):
            X, y = gen(**args)
        return

    X, y = gen(**args)

    # Equal length
    assert_equal(len(X), len(y))
    # Correct parameters
    assert_equal(len(X), n_samples)
    assert_equal(X.shape[1], n_features)


def test_class_balance(randomstate):
    X, y = genClassificationData(n_samples=100, random_state=randomstate)

    import collections
    c = collections.Counter(y)
    first_class = c[-1]
    second_class = c[1]
    assert np.abs(first_class - second_class) <= 1


def test_data_truth():
    n = 100
    d = 10
    strRel = 2
    generator = check_random_state(1337)
    X, Y = genRegressionData(n_samples=n, n_features=d, n_redundant=0, strRel=strRel,
                             n_repeated=0, random_state=generator, noise=0)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=generator)

    linsvr = LinearSVR()
    linsvr.fit(X_train, y_train)
    pred = linsvr.predict(X_test)
    r2 = r2_score(y_test, pred)

    assert r2 > 0.9


def test_data_noise():
    n = 100
    d = 10
    strRel = 5

    generator = check_random_state(1337)
    X, Y = genRegressionData(n_samples=n, n_features=d, n_redundant=0, strRel=strRel,
                             n_repeated=0, random_state=generator, noise=100)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=generator)
    reg = linear_model.LinearRegression(normalize=True)
    reg.fit(X_train, y_train)

    testscore = reg.score(X_test, y_test)
    assert testscore < 0.55


@pytest.mark.parametrize('problem', ["regression", "classification"])
@pytest.mark.parametrize('partition', [
    [2, 2, 3],
    [5, 10, 3],
    pytest.param([2, 0, 2], marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param([2, 1, 2], marks=pytest.mark.xfail(raises=ValueError))
])
def test_partition(problem, randomstate, partition):
    n_samples = 10
    n_features = 100
    strong = 5
    weak = sum(partition)
    repeated = 0

    args = {"n_samples": n_samples, "n_features": n_features,
            "strRel": strong, "n_redundant": weak, "n_repeated": repeated,
            "partition": partition}

    if problem == "regression":
        gen = genRegressionData
    else:
        gen = genClassificationData

    X, y = gen(**args)

    # Equal length
    assert_equal(len(X), len(y))
    # Correct parameters
    assert_equal(len(X), n_samples)
    assert_equal(X.shape[1], n_features)
