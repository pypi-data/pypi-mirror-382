import os
import pandas as pd
from typing import Optional, Sequence, Union


pd.set_option('display.max_columns', None)


def hello():
    print("Welcome to DataNova!")



#############################
###        NOTES
#
#     We need fastparquet, pyarrow, openpyxl, 
#
#

## All functions live here. 

import pandas as pd 
import os

def load_data(uploaded_file:str,  excel_sheet: Optional[Union[str, int]] = 0) -> pd.DataFrame:
    """
    PURPOSE: Load an Excel, CSV, or Parquet file into a Pandas DataFrame.

    Returns
    -------
    pd.DataFrame
        The loaded data.
    """

    uploaded_file = str(uploaded_file)
    _, file_extension = os.path.splitext(uploaded_file)
    file_extension = file_extension.lower()


    if file_extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, sheet_name= excel_sheet, engine=None)
        return(df)
        
    elif file_extension == ".csv":
        df = pd.read_csv(uploaded_file, engine="c", low_memory=False)
        return(df)
        
    elif file_extension == ".parquet":
        df = pd.read_parquet( uploaded_file, engine = 'auto' )
        return(df)
        
    else:
        raise ValueError(f"Unsupported file extension: '{file_extension}'")
    



def highlight_missing(val):
    """
    Color code cells in '%_Blank' based on thresholds (0-100 scale).

    95-100 %    : #b80000
    90- 95 %    : #c11e11
    85- 90 %    : #c62d19
    80- 85 %    : #ca3b21
    75- 80 %    : #cf4a2a
    70- 75 %    : #d35932
    65- 70 %    : #d8673a
    60- 65 %    : #dc7643
    55- 60 %    : #e0854b
    50- 55 %    : #e59353
    45- 50 %    : #e9a25b
    40- 45 %    : #eeb164
    35- 40 %    : #f2bf6c 
    30- 35 %    : #f7ce74
    25- 30 %    : #fbdd7c
    20- 25 %    : #ffeb84
    15- 20 %    : #d7df81
    10- 15 %    : #b0d47f
     5- 10 %    : #8ac97d
     0-  5 %    : #63be7b
    """

    if val > 95:
        color = '#b80000'
    elif val > 90:
        color = '#c11e11'
    elif val > 85:
        color = '#c62d19'
    elif val > 80:
        color = '#ca3b21'
    elif val > 75:
        color = '#cf4a2a'
    elif val > 70:
        color = '#d35932'
    elif val > 65:
        color = '#d8673a'
    elif val > 60:
        color = '#dc7643'
    elif val > 55:
        color = '#e0854b'
    elif val > 50:
        color = '#e59353'
    elif val > 45:
        color = '#e9a25b'
    elif val > 40:
        color = '#eeb164'
    elif val > 35:
        color = '#f2bf6c'
    elif val > 30:
        color = '#f7ce74'
    elif val > 25:
        color = '#fbdd7c'
    elif val > 20:
        color = '#ffeb84'
    elif val > 15:
        color = '#d7df81'
    elif val > 10:
        color = '#b0d47f'
    elif val > 5:
        color = '#8ac97d'
    else:
        color = '#63be7b'
    
    return f'background-color: {color}'


def profile( df:pd.DataFrame ) -> pd.DataFrame:
    """
    PURPOSE
    -------
    Create a data profile of a pandas DataFrame to assess data quality.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    pd.DataFrame
        A summary with column metadata, missingness, uniqueness, and numeric stats.

    """

    n_row, n_col = df.shape

    # Basic summary
    summary = pd.DataFrame({
        'Variable Name': df.columns,
        'Variable Type': df.dtypes,
        'Missing Count': df.isnull().sum(),
        '% Blank': (df.isnull().sum() / n_row * 100).round(0).astype(int),
        'Unique Values': df.nunique(),
        'Most Frequent Value': df.apply(lambda col: col.mode().iloc[0] if not col.mode().empty else pd.NA)
    })

    # Numeric summary 
    numeric_stats = (
        df.describe(include='number')
          .T
          .reset_index()
          .rename(columns={'index': 'Variable Name'})
          .round(2)  # <--- Round numeric columns to 2 decimals
    )

    # Drop & rename columns
    if 'count' in numeric_stats.columns:
        numeric_stats.drop(columns='count', inplace=True)
    
    if '50%' in numeric_stats.columns:
        numeric_stats.rename(columns={'50%': 'Median'}, inplace=True)

    if 'mean' in numeric_stats.columns:
        numeric_stats.rename(columns={'mean': 'Mean'}, inplace=True)

    if 'std' in numeric_stats.columns:
        numeric_stats.rename(columns={'std': 'Standard Deviation'}, inplace=True)

    if 'min' in numeric_stats.columns:
        numeric_stats.rename(columns={'min': 'Min'}, inplace=True)

    if 'max' in numeric_stats.columns:
        numeric_stats.rename(columns={'max': 'Max'}, inplace=True)


    # Skewness
    numeric_skew = df.skew(numeric_only=True).reset_index()
    numeric_skew.columns = ['Variable Name', 'Skewness']

    # Merge everything
    final_summary = summary.merge(numeric_stats, on='Variable Name', how='left')
    final_summary = final_summary.merge(numeric_skew, on='Variable Name', how='left')

    print('Number of Rows = ' + str(n_row) )
    print('Number of Columns = ' + str(n_col)  )

    return(final_summary)



