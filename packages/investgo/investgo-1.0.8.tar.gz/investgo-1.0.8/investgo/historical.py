"""
Historical data fetching functionality for InvestGo.

This module provides functions to fetch and process historical stock price data
from Investing.com with support for large date ranges and concurrent processing.
"""

import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures
from typing import Dict, Any, List, Tuple, Optional
import logging

from .exceptions import InvalidParameterError, NoDataFoundError, APIError
from .utils import get_scraper, get_default_headers

# Set up logging
logger = logging.getLogger(__name__)


def fetch_historical_prices(pair_id: str, date_from: str, date_to: str) -> Dict[str, Any]:
    """
    Fetch historical price data from Investing.com API.

    Args:
        pair_id: The Investing.com pair ID
        date_from: Start date in DDMMYYYY format
        date_to: End date in DDMMYYYY format

    Returns:
        JSON response from the API

    Raises:
        APIError: If the API request fails
    """
    scraper = get_scraper()
    url = "https://aappapi.investing.com/get_screen.php"
    params = {
        "screen_ID": 63,
        "pair_ID": pair_id,
        "lang_ID": 1,
        "date_from": date_from,
        "date_to": date_to
    }
    headers = get_default_headers()

    try:
        response = scraper.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch data for pair_id {pair_id}: {e}")
        raise APIError(f"Failed to fetch historical data for pair_id {pair_id}") from e


def json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert JSON response to a pandas DataFrame.
    
    Args:
        json_data: JSON response from the Investing.com API
        
    Returns:
        pandas.DataFrame with processed historical data, indexed by date
        
    Note:
        Returns empty DataFrame if no data is found
    """
    if 'data' not in json_data or not json_data['data']:
        logger.warning("No data found in JSON response")
        return pd.DataFrame()
    
    try:
        screen_data = json_data['data'][0]['screen_data']['data']
        
        # Process each data point
        for item in screen_data:
            # Convert timestamp to date string
            item["date"] = datetime.utcfromtimestamp(item["date"]).strftime('%d%m%Y')
            
            # Clean numeric fields with FIXED volume processing
            for key in ['price', 'open', 'high', 'low', 'vol', 'perc_chg']:
                if key in item and isinstance(item[key], str):
                    # Special handling for volume with M, K, B suffixes
                    if key == 'vol':
                        vol_str = item[key].replace(',', '').strip()
                        if vol_str.endswith('M'):
                            # Convert millions: '2.5M' -> '2500000'
                            item[key] = str(float(vol_str[:-1]) * 1_000_000)
                        elif vol_str.endswith('K'):
                            # Convert thousands: '900K' -> '900000'
                            item[key] = str(float(vol_str[:-1]) * 1_000)
                        elif vol_str.endswith('B'):
                            # Convert billions: '1.5B' -> '1500000000'
                            item[key] = str(float(vol_str[:-1]) * 1_000_000_000)
                        else:
                            # No suffix, just remove % if present
                            item[key] = vol_str.replace('%', '')
                    else:
                        # Handle other fields normally
                        cleaned_value = item[key].replace(',', '').replace('K', '000').replace('%', '')
                        item[key] = cleaned_value
        
        # Create DataFrame
        df = pd.DataFrame(screen_data)
        
        if 'date' in df.columns:
            # Set date as index
            df.set_index('date', inplace=True)
            df.index = pd.to_datetime(df.index, format='%d%m%Y')
            
            # Sort by date ascending
            df = df.sort_index(ascending=True)
            
            # Remove color column if it exists
            df.drop('color', axis=1, inplace=True, errors='ignore')
            
            # Convert to numeric
            return df.apply(pd.to_numeric, errors='coerce')
            
    except (KeyError, IndexError) as e:
        logger.error(f"Error processing JSON data: {e}")
    
    return pd.DataFrame()


def generate_date_ranges(date_from: str, date_to: str, delta_days: int = 365) -> List[Tuple[str, str]]:
    """
    Generate date ranges for chunking large date spans.
    
    Investing.com has limits on date range size, so we chunk large ranges
    into smaller pieces for reliable data retrieval.
    
    Args:
        date_from: Start date in DDMMYYYY format
        date_to: End date in DDMMYYYY format  
        delta_days: Maximum days per chunk (default: 365)
        
    Returns:
        List of (start_date, end_date) tuples in DDMMYYYY format
        
    Raises:
        InvalidParameterError: If date format is invalid
    """
    try:
        start_date = datetime.strptime(date_from, "%d%m%Y")
        end_date = datetime.strptime(date_to, "%d%m%Y")
    except ValueError as e:
        raise InvalidParameterError(f"Invalid date format. Use DDMMYYYY format: {e}") from e

    if start_date > end_date:
        raise InvalidParameterError("Start date must be before end date")
    
    delta = timedelta(days=delta_days)
    date_ranges = []
    
    while start_date < end_date:
        current_end_date = min(start_date + delta, end_date)
        date_ranges.append((
            start_date.strftime('%d%m%Y'), 
            current_end_date.strftime('%d%m%Y')
        ))
        start_date = current_end_date + timedelta(days=1)
    
    return date_ranges


def fetch_data_for_range(pair_id: str, date_range: Tuple[str, str]) -> pd.DataFrame:
    """
    Fetch data for a single date range.

    Args:
        pair_id: The Investing.com pair ID
        date_range: Tuple of (start_date, end_date) in DDMMYYYY format

    Returns:
        pandas.DataFrame with historical data for the date range
    """
    date_from, date_to = date_range
    json_data = fetch_historical_prices(pair_id, date_from, date_to)
    return json_to_dataframe(json_data)


def get_historical_prices(pair_id: str, date_from: str, date_to: str) -> pd.DataFrame:
    """
    Get historical price data for a stock with automatic date range chunking.

    This function automatically handles large date ranges by splitting them into
    smaller chunks and fetching data concurrently for better performance.

    Args:
        pair_id: The Investing.com pair ID (use get_pair_id to find this)
        date_from: Start date in DDMMYYYY format (e.g., "01012020")
        date_to: End date in DDMMYYYY format (e.g., "31122023")

    Returns:
        pandas.DataFrame with columns:
            - price: Closing price
            - open: Opening price
            - high: Daily high
            - low: Daily low
            - vol: Volume
            - perc_chg: Percentage change
        Index is datetime

    Raises:
        InvalidParameterError: If parameters are invalid
        APIError: If API requests fail

    Examples:
        >>> pair_id = get_pair_id(['AAPL'])[0]
        >>> df = get_historical_prices(pair_id, "01012023", "31122023")
        >>> print(df.head())
    """
    if not pair_id:
        raise InvalidParameterError("pair_id cannot be empty")

    # Validate dates early
    try:
        start_dt = datetime.strptime(date_from, "%d%m%Y")
        end_dt = datetime.strptime(date_to, "%d%m%Y")
        if start_dt > end_dt:
            raise InvalidParameterError("Start date must be before end date")
    except ValueError as e:
        if "Start date" not in str(e):
            raise InvalidParameterError(f"Invalid date format. Use DDMMYYYY format: {e}") from e
        raise

    logger.info(f"Fetching historical data for pair_id {pair_id} from {date_from} to {date_to}")

    # Generate date ranges for chunking
    date_ranges = generate_date_ranges(date_from, date_to)
    logger.info(f"Split into {len(date_ranges)} date ranges")

    # Fetch data concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_data_for_range, pair_id, date_range)
            for date_range in date_ranges
        ]
        results = []

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if not result.empty:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching data for date range: {e}")
    
    # Combine results
    if results:
        # Sort by date to ensure proper ordering
        results.sort(key=lambda df: df.index.min())
        combined_df = pd.concat(results)
        
        # Remove any duplicate dates that might occur at range boundaries
        combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
        
        logger.info(f"Successfully retrieved {len(combined_df)} data points")
        return combined_df
    else:
        logger.warning("No data retrieved for any date ranges")
        return pd.DataFrame()


def get_multiple_historical_prices(
    pair_ids: List[str],
    date_from: str,
    date_to: str
) -> pd.DataFrame:
    """
    Get historical data for multiple stocks concurrently.

    Args:
        pair_ids: List of Investing.com pair IDs
        date_from: Start date in DDMMYYYY format
        date_to: End date in DDMMYYYY format

    Returns:
        pandas.DataFrame with data for all stocks concatenated

    Raises:
        InvalidParameterError: If parameters are invalid

    Examples:
        >>> ids = get_pair_id(['AAPL', 'MSFT'])
        >>> df = get_multiple_historical_prices(ids, "01012023", "31122023")
    """
    if not pair_ids:
        raise InvalidParameterError("pair_ids cannot be empty")

    logger.info(f"Fetching data for {len(pair_ids)} stocks")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(get_historical_prices, pair_id, date_from, date_to)
            for pair_id in pair_ids
        ]
        results = []

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if not result.empty:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching data for stock: {e}")
    
    if results:
        return pd.concat(results, axis=0)  # Concatenate vertically by default
    else:
        logger.warning("No data retrieved for any stocks")
        return pd.DataFrame()