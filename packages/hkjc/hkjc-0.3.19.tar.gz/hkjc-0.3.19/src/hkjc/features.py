""" Polars expressions to commonly-used analysis features, subject to frequent changes.
"""
import polars as pl

rating_diff = (pl.col('Rtg').max().over('RaceId')-pl.col('Rtg')).alias('RtgDiff')
frontrunner_pct = (pl.col('FavoriteRunningStyle')=='FrontRunner').mean().over('RaceId').alias('FRPct')