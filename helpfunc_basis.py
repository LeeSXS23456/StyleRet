from rqdatac import *
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
srcdir = os.path.join(BASE_DIR, "data_base", "basis","index_future_basics.pkl")

def add_basis_data(st,ed):
    df_future = all_instruments(type='Future')
    df_index = df_future[df_future["product"]=="Index"]
    df_index_real = df_index[df_index["maturity_date"]!="0000-00-00"]
    df_index_real.to_pickle(srcdir)

    contracts = df_index_real["order_book_id"].tolist()
    df_info = futures.get_basis(contracts, start_date=st, end_date=ed, fields=["settlement","close_index"], frequency='1d', dividend_adjusted=False, market='cn')
    df_info = df_info.reset_index(level=1)

    # 计算基础指标
    df_info["basis"] = df_info["settlement"] - df_info["close_index"]
    df_info["abs_ratio"] = df_info["basis"] / df_info["close_index"]

    df_index_real.set_index(["order_book_id"], inplace=True)
    df_info_m = df_info.merge(df_index_real[["listed_date","maturity_date"]], on=["order_book_id"], how="left")
    # 统一转为日期格式
    df_info_m["maturity_date"] = pd.to_datetime(df_info_m["maturity_date"])
    df_info_m["date"] = pd.to_datetime(df_info_m["date"])
    # 再计算间隔天数
    df_info_m["residual_day"] = np.where(
        (df_info_m["maturity_date"] - df_info_m["date"]).dt.days == 0,
        np.nan,
        (df_info_m["maturity_date"] - df_info_m["date"]).dt.days
    )

    df_info_m["ana_cost"] = df_info_m["abs_ratio"] / df_info_m["residual_day"] * 365

    return df_info_m