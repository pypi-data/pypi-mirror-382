import polars as pl
from typing import List, Union
from datetime import datetime as dt
import bs4
import re


def _validate_date(date_str: str) -> bool:
    # validate date format
    try:
        dt.strptime(date_str, "%Y-%m-%d")
    except Exception:
        raise ValueError("Date must be in 'YYYY-MM-DD' format")
    return True


def _validate_venue_code(venue_code: str) -> bool:
    if venue_code not in ['HV', 'ST']:
        raise ValueError(
            "Venue code must be 'HV' (Happy Valley) or 'ST' (Sha Tin)")
    return True


def _parse_html_table(table: bs4.element.Tag, skip_header=False) -> pl.DataFrame:
    """Parse an HTML table (HKJC format) into a Polars DataFrame
    """
    if table is None:
        raise ValueError("No table found in HTML tag")

    # Extract headers
    headers = []
    if not skip_header:
        header_row = table.find('thead')
        if header_row:
            headers = [td.get_text(strip=True) for td in header_row.find_all('td')]
        else:
            # If no thead, try first tr
            first_row = table.find('tr')
            if first_row:
                headers = [th.get_text(strip=True)
                        for th in first_row.find_all('th')]
                if not headers:
                    # If no th tags, use td tags from first row as headers
                    headers = [td.get_text(strip=True)
                            for td in first_row.find_all('td')]

    # Extract data rows
    data = []
    tbody = table.find('tbody')
    rows = tbody.find_all('tr') if tbody else table.find_all('tr')

    # Skip first row if it was used for headers
    start_idx = 1 if not tbody and headers else 0

    for row in rows[start_idx:]:
        cells = row.find_all(['td', 'th'])
        row_data = [cell.get_text(separator=' ',strip=True) for cell in cells]
        if row_data:  # Skip empty rows
            data.append(row_data)

    # Create DataFrame
    if not headers:
        # Generate default column names if no headers found
        headers = [f"column_{i}" for i in range(len(data[0]))] if data else []

    # Ensure all rows have the same number of columns
    if data:
        max_cols = len(headers)
        data = [row + [''] * (max_cols - len(row)) if len(row)
                < max_cols else row[:max_cols] for row in data]

    df = pl.DataFrame(data, schema=headers, orient='row')
    # Clean column names by removing special characters
    df.columns = [re.sub(r'[^\w]', '', col)
                         for col in df.columns]
    return df


def pareto_filter(
    df: pl.DataFrame,
    groupby: List[str],
    by: List[str],
    maximize: Union[bool, List[bool]] = True
) -> pl.DataFrame:
    """
    Filter dataframe to only include Pareto optimal rows within each group.

    Args:
        df: Input dataframe
        groupby: Columns to group by (empty list for global filter)
        by: Columns to consider for Pareto optimality
        maximize: Whether to maximize (True) or minimize (False) each 'by' column

    Returns:
        DataFrame containing only Pareto optimal rows
    """
    if df.is_empty() or not by:
        return df

    # Normalize maximize to list
    maximize_list = [maximize] * \
        len(by) if isinstance(maximize, bool) else maximize

    if len(maximize_list) != len(by):
        raise ValueError(
            f"Length of 'maximize' ({len(maximize_list)}) must equal length of 'by' ({len(by)})")

    # Single objective: simple min/max filter
    if len(by) == 1:
        opt_expr = pl.col(by[0]).max(
        ) if maximize_list[0] else pl.col(by[0]).min()
        if groupby:
            opt_expr = opt_expr.over(groupby)
        return df.filter(pl.col(by[0]) == opt_expr)

    # Two objectives: efficient skyline algorithm
    if len(by) == 2:
        temp_cols = ["__obj_0", "__obj_1"]

        # Transform to maximization problem
        df_temp = df.with_columns([
            (pl.col(by[i]) * (1 if maximize_list[i] else -1)
             ).alias(temp_cols[i])
            for i in range(2)
        ])

        # Sort by first objective descending, then second descending (for stability)
        groupby = groupby or []
        sort_cols = (groupby if groupby else []) + temp_cols
        sorted_df = df_temp.sort(sort_cols, descending=[
                                 False] * len(groupby) + [True, True])

        # Keep rows where second objective is not dominated by any previous row in group
        if groupby:
            max_so_far = pl.col(temp_cols[1]).cum_max().shift(
                1, fill_value=float("-inf")).over(groupby)
        else:
            max_so_far = pl.col(temp_cols[1]).cum_max().shift(
                1, fill_value=float("-inf"))

        mask = pl.col(temp_cols[1]) > max_so_far
        return sorted_df.filter(mask).drop(temp_cols)

    # N objectives (N > 2): pairwise dominance check
    df_with_id = df.with_row_index("__id")

    # Self-join to compare all pairs
    left = df_with_id.lazy()
    right = df_with_id.lazy()

    if groupby:
        pairs = left.join(right, on=groupby, suffix="_r")
    else:
        pairs = left.join(right, how="cross", suffix="_r")

    # Only compare different rows
    pairs = pairs.filter(pl.col("__id") != pl.col("__id_r"))

    # Build dominance conditions
    dominance_conditions = []
    for col, is_max in zip(by, maximize_list):
        if is_max:
            # right dominates left if right[col] >= left[col] for all cols
            dominance_conditions.append(pl.col(f"{col}_r") >= pl.col(col))
        else:
            dominance_conditions.append(pl.col(f"{col}_r") <= pl.col(col))

    # Strict dominance: all >= and at least one >
    strict_conditions = []
    for col, is_max in zip(by, maximize_list):
        if is_max:
            strict_conditions.append(pl.col(f"{col}_r") > pl.col(col))
        else:
            strict_conditions.append(pl.col(f"{col}_r") < pl.col(col))

    is_dominated = pl.all_horizontal(
        dominance_conditions) & pl.any_horizontal(strict_conditions)

    # Find IDs of dominated rows
    dominated_ids = (
        pairs.filter(is_dominated)
        .select("__id")
        .unique()
        .collect()
        .get_column("__id")
    )

    # Return non-dominated rows
    return df_with_id.filter(~pl.col("__id").is_in(dominated_ids)).drop("__id")
