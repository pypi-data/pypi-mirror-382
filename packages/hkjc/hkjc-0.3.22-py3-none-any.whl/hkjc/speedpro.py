"""Functions to scrap SpeedPro data.
"""
from __future__ import annotations

from datetime import datetime as dt

import polars as pl
import requests
import json

ENERGY_XLS_TEMPLATE = "https://racing.hkjc.com/racing/speedpro/assets/excel/{date}_energygrid_en.xls"
SPEEDMAP_URL_TEMPLATE = "https://racing.hkjc.com/racing/speedpro/assets/json/speedguide/race_{race_num}.json"


def speedpro_energy(race_date: str) -> pl.DataFrame:
    """Fetch and process SpeedPro scores for a given race date.

    Args:
        race_date (str): Date in 'YYYY-MM-DD' format.

    Returns:
        pl.DataFrame: Processed DataFrame with SpeedPro scores.
    """
    # validate date format
    try:
        dt.strptime(race_date, "%Y-%m-%d")
    except Exception:
        raise ValueError("Date must be in 'YYYY-MM-DD' format")

    df = pl.read_excel(ENERGY_XLS_TEMPLATE.format(
        date=dt.strptime(race_date, "%Y-%m-%d").strftime("%Y%m%d")))
    
    # Clean column names
    df.columns = [col.strip().replace(" ", "").replace(
        "\n", "_").replace('.', '') for col in df.columns]

    df = (df.with_columns(pl.col('RunnerNumber').str.to_integer())
          .with_columns(pl.col('SpeedPRO_Energy_Difference').str.to_integer())
          .with_columns(pl.col('FitnessRatings').str.to_integer())
          .select(['RaceNo', 'RunnerNumber', 'HorseName', 'FitnessRatings','SpeedPRO_Energy_Difference']))

    return df


def speedmap(race_num: int) -> str:
    """Fetch SpeedMap as base64 encoded string.

    Args:
        race_date (str): Date in 'YYYY-MM-DD' format.
        race_num (int): Race number.
    
    Returns:
        str: Base64 encoded string of the SpeedMap image.
    """
    r = requests.get(SPEEDMAP_URL_TEMPLATE.format(race_num=race_num))
    if r.status_code != 200:
        raise RuntimeError(f"Request failed: {r.status_code} - {r.text}")
    # Decode with 'utf-8-sig' to strip a possible UTF-8 BOM before JSON parsing
    content = r.content.decode("utf-8-sig")
    return json.loads(content)['en-us']['RaceMap']