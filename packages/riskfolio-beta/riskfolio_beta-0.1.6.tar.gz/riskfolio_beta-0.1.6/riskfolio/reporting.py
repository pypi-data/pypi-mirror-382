# reporting.py
import pandas as pd
import matplotlib.pyplot as plt

def pretty_print(df: pd.DataFrame, floatfmt="{:.2f}") -> None:
    print(df.to_string(formatters={col: floatfmt.format for col in df.select_dtypes('float').columns}))

def plot_rwa_share(df: pd.DataFrame, group_col="desk"):
    df.plot(x=group_col, y="RWA_Share", kind="bar")
    plt.title("RWA Share by Desk")
    plt.show()