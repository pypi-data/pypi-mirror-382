"""Functions to fetch and process historical race and horse data from HKJC
"""
from __future__ import annotations

import requests
import polars as pl
from bs4 import BeautifulSoup
from cachetools.func import ttl_cache

from .utils import _parse_html_table

HKJC_RACE_URL_TEMPLATE = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate={date}&Racecourse={venue_code}&RaceNo={race_number}"
HKJC_HORSE_URL_TEMPLATE = "https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseNo={horse_no}"

incidents = ['DISQ', 'DNF', 'FE', 'ML', 'PU', 'TNP', 'TO',
             'UR', 'VOID', 'WR', 'WV', 'WV-A', 'WX', 'WX-A', 'WXNR']


@ttl_cache(maxsize=100, ttl=3600)
def _soupify(url: str) -> BeautifulSoup:
    """Fetch and parse a webpage and return BeautifulSoup object
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def _soupify_race_page(date: str, venue_code: str, race_number: int) -> BeautifulSoup:
    """Fetch and parse HKJC race results page and return BeautifulSoup object
    """
    url = HKJC_RACE_URL_TEMPLATE.format(
        date=date, venue_code=venue_code, race_number=race_number)
    return _soupify(url)


def _soupify_horse_page(horse_no: str) -> BeautifulSoup:
    """Fetch and parse HKJC race results page and return BeautifulSoup object
    """
    url = HKJC_HORSE_URL_TEMPLATE.format(horse_no=horse_no)
    return _soupify(url)


def _classify_running_style(df: pl.DataFrame, running_pos_col="RunningPosition") -> pl.DataFrame:
    """Classify running style based on RunningPosition column
    """
    # Split the RunningPosition column into separate columns and convert to integers
    df = df.with_columns(
        pl.col(running_pos_col)
        .str.split_exact(" ", n=3)
        .struct.rename_fields(["StartPosition", "Position2", "Position3", "FinishPosition"])
        # Give an alias to the struct for easier selection
        .alias("split_data").cast(pl.Int64, strict=False)
    ).unnest("split_data")

    df = df.with_columns(
        pl.col('FinishPosition').fill_null(pl.col('Position3')))

    df = df.with_columns([
        (pl.col("StartPosition")-pl.col("FinishPosition")).alias("PositionChange"),
        pl.mean_horizontal("StartPosition", "Position2").alias(
            "AvgStartPosition"),
    ]).with_columns(pl.when(pl.col("StartPosition").is_null()).then(pl.lit("--"))
                    .when((pl.col("AvgStartPosition") <= 3) & (pl.col("StartPosition") <= 3)).then(pl.lit("FrontRunner"))
                    .when((pl.col("PositionChange") >= 1) & (pl.col("StartPosition") >= 6)).then(pl.lit("Closer"))
                    .otherwise(pl.lit("Pacer")).alias("RunningStyle"))

    recent_style = df['RunningStyle'][:5].mode()[0]
    df = df.with_columns(pl.lit(recent_style).alias("FavoriteRunningStyle"))

    return df


def _extract_horse_data(horse_no: str) -> pl.DataFrame:
    """Extract horse info and history from horse page
    """
    soup = _soupify_horse_page(horse_no)
    table = soup.find('table', class_='bigborder')
    horse_data = _parse_html_table(table).filter(
        pl.col('Date') != '')  # Remove empty rows
    horse_data = _classify_running_style(horse_data)

    horse_data = horse_data.with_columns(pl.lit(horse_no).alias('HorseNo'))

    return horse_data


def _clean_horse_data(df: pl.DataFrame) -> pl.DataFrame:
    """ Clean and convert horse data to suitable data types
    """
    df = df.with_columns(
        pl.col('Pla').str.split(' ').list.first().alias('Pla')
    ).filter(~pl.col('Pla').is_in(incidents))

    df = df.with_columns([
        pl.col('Pla').cast(pl.Int64, strict=False),
        pl.col('ActWt').cast(pl.Int64, strict=False),
        pl.col('DeclarHorseWt').cast(pl.Int64, strict=False),
        pl.col('Dr').cast(pl.Int64, strict=False),
        pl.col('Rtg').cast(pl.Int64, strict=False),
        pl.col('Dist').cast(pl.Int64, strict=False),
        pl.col('WinOdds').cast(pl.Float64, strict=False)
    ])

    df = (df.filter(~pl.col('FinishTime').str.starts_with('--'))
          .with_columns(
        (
            pl.col("FinishTime").str.splitn(".", 2).struct.field("field_0").cast(pl.Int64) * 60 +
            pl.col("FinishTime").str.splitn(".", 2).struct.field("field_1").cast(pl.Float64)
        ).cast(pl.Float64).round(2).alias("FinishTime")
    ))

    df = df.with_columns(
        pl.col('RCTrackCourse').str.split_exact(' / ', 2)
        .struct.rename_fields(['Venue', 'Track', 'Course'])
        .alias('RCTrackCourse')
    ).unnest('RCTrackCourse')

    df = df.with_columns(
        pl.when(pl.col('Date').str.len_chars() <= 8)
        .then(pl.col('Date').str.strptime(pl.Date, '%d/%m/%y', strict=False))
        .otherwise(pl.col('Date').str.strptime(pl.Date, '%d/%m/%Y'))
    ).with_columns(
        pl.concat_str(pl.col('Date').dt.strftime('%Y%m%d'), pl.col(
            'Venue'), pl.col('RaceIndex')).alias('RaceId')
    ).drop("VideoReplay")
    return df


def get_horse_data(horse_no: str) -> pl.DataFrame:
    df = _extract_horse_data(horse_no)
    return _clean_horse_data(df)


def _clean_race_data(df: pl.DataFrame) -> pl.DataFrame:
    """ Clean and convert horse data to suitable data types
    """
    df = df.with_columns(
        pl.col('Pla').str.split(' ').list.first().alias('Pla')
    ).filter(~pl.col('Pla').is_in(incidents))

    df = df.with_columns([
        pl.col('Pla').cast(pl.Int64, strict=False),
        pl.col('HorseNo').cast(pl.Int64, strict=False),
        pl.col('ActWt').cast(pl.Int64, strict=False),
        pl.col('DeclarHorseWt').cast(pl.Int64, strict=False),
        pl.col('Dr').cast(pl.Int64, strict=False),
        pl.col('WinOdds').cast(pl.Float64, strict=False)
    ])

    df = df.with_columns(
        (
            pl.col("FinishTime").str.splitn(":", 2).struct.field("field_0").cast(pl.Int64) * 60 +
            pl.col("FinishTime").str.splitn(":", 2).struct.field("field_1").cast(pl.Float64)
        ).cast(pl.Float64).round(2).alias("FinishTime")
    )

    return df


def _extract_race_data(date: str, venue_code: str, race_number: int) -> pl.DataFrame:
    soup = _soupify_race_page(date, venue_code, race_number)
    table = soup.find('div', class_='race_tab').find('table')
    race_data = _parse_html_table(table)

    # Extract the relevant race information
    race_id = race_data.columns[0].replace(f'RACE{race_number}', '')
    race_class = race_data.item(1, 0).split('-')[0].strip()
    race_dist = race_data.item(1, 0).split('-')[1].strip().rstrip('M')
    race_name = race_data.item(2, 0).strip()
    going = race_data.item(1, 2).strip()
    course = race_data.item(2, 2).strip()

    race_info = {'Date': date,
                 'Venue': venue_code,
                 'RaceIndex': int(race_id),
                 'RaceNumber': race_number,
                 'RaceClass': race_class,
                 'RaceDistance': race_dist,
                 'RaceName': race_name,
                 'Going': going,
                 'Course': course}

    # Extract the results table
    table = soup.find('div', class_='performance').find('table')
    race_data = (_parse_html_table(table)
                 .with_columns([
                     pl.lit(value).alias(key) for key, value in race_info.items()
                 ])
                 .with_columns(
                     pl.col("Horse").str.extract(r"\((.*?)\)")
                     .alias("HorseID")
    )
    )

    return race_data


def get_race_data(date: str, venue_code: str, race_number: int) -> pl.DataFrame:
    df = _extract_race_data(date, venue_code, race_number)
    return _clean_race_data(df)
