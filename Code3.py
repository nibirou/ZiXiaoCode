
from datetime import datetime
import matplotlib.pyplot as plt
import akshare as ak  # 升级到最新版
import pandas as pd
import mplfinance as mpf


# 解决中文乱码

plt.rcParams["font.sans-serif"] = ["STHeiti"]

plt.rcParams["axes.unicode_minus"] = False

def kline(symbol, start_time, end_time, stock_name):
    # 利用 AKShare 获取股票的后复权数据，这里只获取前 6 列
    stock_hfq_df = ak.stock_zh_a_hist(symbol, adjust="hfq").iloc[:, :6]

    # 处理字段命名
    stock_hfq_df.columns = [
        'date',
        'open',
        'close',
        'high',
        'low',
        'volume',
    ]
    # 把 date 作为日期索引
    stock_hfq_df.index = pd.to_datetime(stock_hfq_df['date'])
    stock_hfq_df = stock_hfq_df[start_time:end_time]

    #print(stock_hfq_df)
    # 创建一个marketcolors对象,并设置颜色参数
    marketcolors = mpf.make_marketcolors(up='r', down='g', volume='inherit')

    # 创建一个style对象,并将marketcolors对象传递给它
    style = mpf.make_mpf_style( marketcolors=marketcolors, edgecolor='k', rc={'font.family': 'STHeiti'})

    # 添加图表
    mpf.plot(stock_hfq_df, type='candle', style=style, title= stock_name + "K线图" ,
             ylabel="价格",
             ylabel_lower="成交量",
             mav=(5, 10, 20), volume=True, show_nontrading=False)


if __name__ == '__main__':
    kline("603348", "2024-01-01", "2024-04-26", "文灿股份")