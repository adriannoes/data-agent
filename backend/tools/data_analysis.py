"""Data analysis tools for processing CSV files."""

import pandas as pd
from typing import Dict, Any, Optional
import os


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with the loaded data
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    return pd.read_csv(filepath)


def get_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get basic statistics summary of a DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_dict() if not df.select_dtypes(include=['number']).empty else {},
    }
    return summary


def filter_data(df: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter DataFrame based on conditions.
    
    Args:
        df: DataFrame to filter
        conditions: Dictionary with column names as keys and filter values
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, value in conditions.items():
        if column in filtered_df.columns:
            if isinstance(value, (int, float)):
                filtered_df = filtered_df[filtered_df[column] == value]
            elif isinstance(value, str):
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
            elif isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
    
    return filtered_df


def get_column_info(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific column.
    
    Args:
        df: DataFrame
        column: Column name
        
    Returns:
        Dictionary with column information
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    col_info = {
        "name": column,
        "dtype": str(df[column].dtype),
        "null_count": df[column].isnull().sum(),
        "unique_count": df[column].nunique(),
    }
    
    if df[column].dtype in ['int64', 'float64']:
        col_info["min"] = float(df[column].min())
        col_info["max"] = float(df[column].max())
        col_info["mean"] = float(df[column].mean())
        col_info["median"] = float(df[column].median())
    else:
        col_info["sample_values"] = df[column].dropna().head(10).tolist()
    
    return col_info

