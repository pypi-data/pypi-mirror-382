# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pandas
import scipy.stats
import inspect
from ... import utilities as ut
import numpy as np


def count(df):
    # df.count() by default only counts non-NA cells
    return {"count": df.count()}


def min(df):
    return {"min": df.min(skipna=True)}


def max(df):
    return {"max": df.max(skipna=True)}


def minmax(df):
    return {**min(df), **max(df)}


def mean(df):
    return {"mean": df.mean(skipna=True)}


def std(df):
    return {"std": df.std(ddof=1, skipna=True)}


def median(df):
    return {"median": df.median(skipna=True)}


def sem(df):
    return {"sem": df.sem(ddof=1, skipna=True)}


def confidence_intervals_of_the_mean(df):
    loc = mean(df)["mean"]
    scale = sem(df)["sem"]
    dfcount = count(df)['count']

    result = {}
    confidence_levels = [0.68, 0.95, 0.99]
    for confidence_level in confidence_levels:
        key = (
            "confidence interval of the mean at "
            + str(int(confidence_level * 100))
            + "%"
        )
        series = {}
        for column in df:
            params = {
                'confidence': confidence_level,
                'df': dfcount[column] - 1,
                'loc': loc[column],
                'scale': scale[column],
            }
            if scale[column] > 0:
                value = scipy.stats.t.interval(**params)
            else:
                value = (np.nan, np.nan)
            series[column] = value
        result[key] = pandas.Series(series)
    return result


def standard(df):
    mean_ = mean(df)
    sem_ = sem(df)
    count_ = count(df)
    intervals = {}
    for column in df:
        params = {
            'confidence': 0.95,
            'df': count_['count'][column] - 1,
            'loc': mean_["mean"][column],
            'scale': sem_["sem"][column],
        }
        if params['scale'] > 0:
            value = scipy.stats.t.interval(**params)
        else:
            value = (np.nan, np.nan)
        intervals[column] = value
    return {
        **mean_,
        **std(df),
        **sem_,
        "confidence interval of the mean at 95%": pandas.Series(intervals),
    }


def skewness(df):
    return {"skewness": df.skew(skipna=True)}


def kurtosis(df):
    return {"kurtosis": df.kurtosis(skipna=True)}


def high_order(df):
    return {**skewness(df), **kurtosis(df)}


def mode(df):
    return {"mode": df.mode(dropna=True)}


def harmonic_mean(df):
    res = {}
    for column in df:
        try:
            res[column] = scipy.stats.hmean(df[column], nan_policy='omit')
        except ValueError as e:
            # Fix to deal with possible negative input data
            if "only defined if all elements greater" in str(e):
                logger = ut.get_logger(__name__)
                logger.warning(f"Setting harmonic mean as NaN for '{column}'. {str(e)}")
                res[column] = np.nan
            else:
                raise  # pragma: no cover
    return {"harmonic_mean": pandas.Series(res)}


def geometric_mean(df):
    res = {}
    for column in df:
        res[column] = scipy.stats.gmean(df[column], nan_policy='omit')
    return {"geometric_mean": pandas.Series(res)}


def central(df):
    return {**mean(df), **geometric_mean(df), **harmonic_mean(df)}


def covariance(df):
    # df.cov() automatically excludes NA and null values
    return {"covariance": df.cov()}


def correlation(df):
    # df.corr() automatically excludes NA and null values
    return {"correlation": df.corr()}


def quantiles(df):
    q = [
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.30,
        0.35,
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
    ]
    result = {}
    for percentage in q:
        key = "quantile " + str(int(percentage * 100)) + "%"
        result[key] = df.quantile(q=percentage)
    return result


def box_plot(df):
    q1 = df.quantile(q=0.25)
    q3 = df.quantile(q=0.75)
    return {**mean(df), **median(df), "Q1": q1, "Q3": q3, **min(df), **max(df)}
