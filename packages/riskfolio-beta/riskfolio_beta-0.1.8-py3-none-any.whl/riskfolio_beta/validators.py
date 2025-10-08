# validators.py
import pandas as pd

REQUIRED_COLUMNS = {"notional", "product", "desk"}

def validate_portfolio_df(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")