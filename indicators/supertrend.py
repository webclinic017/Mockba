# This code uses the pandas library to load and manipulate data, and the numpy library for mathematical operations. 
# The super_trend function takes in a data frame df containing the close, high, and low values of the asset being analyzed, 
# the n value

import pandas as pd
import numpy as np

def super_trend(df, n, multiplier):
    ATR = df["high"].rolling(n).max() - df["low"].rolling(n).min()
    basic_upper_band = df["high"].rolling(n).mean() + multiplier * ATR
    basic_lower_band = df["low"].rolling(n).mean() - multiplier * ATR
    df["basic_upper_band"] = basic_upper_band
    df["basic_lower_band"] = basic_lower_band
    
    for i in range(len(df)):
        if (df.at[i, "close"] <= df.at[i, "basic_upper_band"]) & (df.at[i, "close"] >= df.at[i, "basic_lower_band"]):
            if df.at[i - 1, "close"] <= df.at[i - 1, "basic_upper_band"]:
                df.at[i, "basic_upper_band"] = df.at[i - 1, "basic_upper_band"]
            else:
                df.at[i, "basic_upper_band"] = np.NaN
                
            if df.at[i - 1, "close"] >= df.at[i - 1, "basic_lower_band"]:
                df.at[i, "basic_lower_band"] = df.at[i - 1, "basic_lower_band"]
            else:
                df.at[i, "basic_lower_band"] = np.NaN
        else:
            if df.at[i - 1, "close"] <= df.at[i - 1, "basic_upper_band"]:
                df.at[i, "basic_upper_band"] = basic_upper_band[i]
            else:
                df.at[i, "basic_upper_band"] = np.NaN
                
            if df.at[i - 1, "close"] >= df.at[i - 1, "basic_lower_band"]:
                df.at[i, "basic_lower_band"] = basic_lower_band[i]
            else:
                df.at[i, "basic_lower_band"] = np.NaN
                
    df["super_trend"] = np.where(df["close"] <= df["basic_upper_band"], df["basic_upper_band"], df["basic_lower_band"])
    df["super_trend"] = np.where(df["close"] > df["basic_upper_band"], df["basic_lower_band"], df["super_trend"])
    return df

df = pd.read_csv("sample_data.csv")
n = 14
multiplier = 3
df = super_trend(df, n, multiplier)
df.head()
