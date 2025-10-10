import numpy as np


def _discreteuniform_fit_args(data):
    dmin = np.floor(min(data))
    dmax = np.floor(max(data))
    bounds = {"low": (dmin, dmin + 1), "high": (dmax, dmax + 1)}
    guess = {"low": dmin, "high": dmax + 1}
    return bounds, guess


def _poisson_fit_args(data):
    loc_guess = min(data)
    mu_guess = np.mean(data - loc_guess)
    bounds = {
        "mu": (mu_guess / 10, mu_guess * 10),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"mu": mu_guess, "loc": loc_guess}
    return bounds, guess


def _bernoulli_fit_args(data):
    loc_guess = min(data)
    p_guess = np.mean(data - loc_guess)
    # Ensure p is between 0 and 1
    p_guess = 0.0 if p_guess < 0.0 else 1.0 if p_guess > 1.0 else p_guess
    bounds = {
        "p": (0, 1),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"p": p_guess, "loc": loc_guess}
    return bounds, guess


def _binomial_fit_args(data):
    loc_guess = min(data)
    mean = np.mean(data - loc_guess)
    std = np.std(data - loc_guess)
    n_guess = int(mean**2 / np.abs(mean - std**2)) + 1
    p_guess = np.abs(mean - std**2) / mean
    loc_guess = min(data)
    p_guess = np.mean(data - loc_guess)
    # Ensure p is between 0 and 1
    p_guess = 0.0 if p_guess < 0.0 else 1.0 if p_guess > 1.0 else p_guess
    bounds = bounds = {
        "n": (0, int(n_guess * 10) + 1),
        "p": (0, 1),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"n": np.round(n_guess), "p": p_guess, "loc": loc_guess}
    return bounds, guess


def _geom_fit_args(data):
    loc_guess = min(data)
    # p_guess = 1 / np.mean(data - loc_guess)
    bounds = {
        "p": (0, 1),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"loc": loc_guess}
    return bounds, guess


def _betabinom_fit_args(data):
    loc_guess = min(data)
    n = max(data) - loc_guess
    m1 = np.mean(data)
    m2 = np.mean(data**2)
    # Guess for a and b obtained from the method of moments
    a = max((n * m1 - m2) / (n * (m2 / m1 - m1 - 1) + m1), 0)
    b = max((n - m1) * (n - m2 / m1) / (n * (m2 / m1 - m1 - 1) + m1), 0)
    a_sup = max(a * 10, 10)
    b_sup = max(b * 10, 10)
    bounds = {
        "n": (0, int(n * 10) + 1),
        "a": (a / 10, a_sup),
        "b": (b / 10, b_sup),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"n": np.round(n), "a": a, "b": b, "loc": loc_guess}
    return bounds, guess


def _hypergeom_fit_args(data):
    loc_guess = min(data)
    data_max = np.round(max(data - loc_guess))
    bounds = {
        "M": (data_max, data_max + 1e4),
        "n": (data_max, data_max + 1e4),
        "N": (data_max, data_max + 1e4),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {}
    return bounds, guess


def _logser_fit_args(data):
    loc_guess = min(data)
    bounds = {
        "p": (0, 1),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {}
    return bounds, guess


def _dlaplace_fit_args(data):
    loc_guess = round(np.mean(data))
    a_guess = np.sqrt(2) / np.std(data - loc_guess)
    bounds = {
        "a": (a_guess / 10, a_guess * 10),
        "loc": (loc_guess - np.abs(loc_guess) - 1, loc_guess + np.abs(loc_guess) + 1),
    }
    guess = {"a": a_guess, "loc": loc_guess}
    return bounds, guess
