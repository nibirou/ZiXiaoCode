# 技术分析是交易者和投资者用来评估金融市场趋势的重要工具。这里我将介绍6种常用的技术分析方法,
# 并使用Python实现这些方法。这里使用`pandas`和`ta`库来计算各种技术指标。

# 以贵州茅台(股票代码:600519)举例， 分析今年至今的数据。

# 首先,让我们导入必要的库并获取股票数据:

import akshare as ak
import pandas as pd

# 获取贵州茅台的股票数据
stock_code = "600519"  # 贵州茅台的股票代码
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")

# 将日期列设置为索引
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

print(df.head())

# 现在,让我们逐一实现常用的技术分析方法:
# 我用的mac系统，字体采用STHeiti。如果你是windows系统，
# 字体可以采用SimHei 解决中文乱码。

# 1. 快慢移动平均线
# 快慢移动平均线是一种简单而有效的趋势跟踪方法。我们将使用20日均线作为快线,50日均线作为慢线。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算快慢移动平均线
df['SMA20'] = SMAIndicator(close=df['收盘'], window=20).sma_indicator()
df['SMA50'] = SMAIndicator(close=df['收盘'], window=50).sma_indicator()

# 生成交易信号
df['Signal'] = 0
df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = 1
df.loc[df['SMA20'] < df['SMA50'], 'Signal'] = -1

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['收盘'], label='收盘价')
plt.plot(df.index, df['SMA20'], label='20日均线')
plt.plot(df.index, df['SMA50'], label='50日均线')
plt.title('贵州茅台 - 快慢移动平均线')
plt.legend()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 在这个策略中,当20日均线上穿50日均线时产生买入信号,下穿时产生卖出信号。

# 2. 移动平均线 + MACD
# 这种方法结合了趋势跟踪(移动平均线)和动量指标(MACD)。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator, MACD

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算指标
df['SMA50'] = SMAIndicator(close=df['收盘'], window=50).sma_indicator()
macd = MACD(close=df['收盘'])
df['MACD'] = macd.macd()
df['MACD_Signal'] = macd.macd_signal()

# 生成交易信号
df['Signal'] = 0
df.loc[(df['MACD'] > df['MACD_Signal']) & (df['收盘'] > df['SMA50']), 'Signal'] = 1
df.loc[(df['MACD'] < df['MACD_Signal']) & (df['收盘'] < df['SMA50']), 'Signal'] = -1

# 绘制图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

ax1.plot(df.index, df['收盘'], label='收盘价')
ax1.plot(df.index, df['SMA50'], label='50日均线')
ax1.set_title('贵州茅台 - 价格和50日均线')
ax1.legend()

ax2.plot(df.index, df['MACD'], label='MACD')
ax2.plot(df.index, df['MACD_Signal'], label='MACD信号线')
ax2.bar(df.index, df['MACD'] - df['MACD_Signal'], label='MACD柱状图')
ax2.set_title('MACD')
ax2.legend()

plt.tight_layout()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 这个策略在MACD上穿信号线且价格在50日均线之上时产生买入信号,反之产生卖出信号。

# 3. RSI + 快慢移动平均线
# 这种方法结合了超买超卖指标(RSI)和趋势跟踪(移动平均线)。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算指标
df['SMA20'] = SMAIndicator(close=df['收盘'], window=20).sma_indicator()
df['SMA50'] = SMAIndicator(close=df['收盘'], window=50).sma_indicator()
df['RSI'] = RSIIndicator(close=df['收盘']).rsi()

# 生成交易信号
df['Signal'] = 0
df.loc[(df['SMA20'] > df['SMA50']) & (df['RSI'] < 70), 'Signal'] = 1
df.loc[(df['SMA20'] < df['SMA50']) & (df['RSI'] > 30), 'Signal'] = -1

# 绘制图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

ax1.plot(df.index, df['收盘'], label='收盘价')
ax1.plot(df.index, df['SMA20'], label='20日均线')
ax1.plot(df.index, df['SMA50'], label='50日均线')
ax1.set_title('贵州茅台 - 价格和移动平均线')
ax1.legend()

ax2.plot(df.index, df['RSI'], label='RSI')
ax2.axhline(y=70, color='r', linestyle='--')
ax2.axhline(y=30, color='g', linestyle='--')
ax2.set_title('RSI')
ax2.legend()

plt.tight_layout()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 这个策略在20日均线上穿50日均线且RSI低于70时产生买入信号,在20日均线下穿50日均线且RSI高于30时产生卖出信号。

# 4. 布林线和RSI
# 布林线提供了价格波动的范围,而RSI则提供了动量信息。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算指标
bollinger = BollingerBands(close=df['收盘'])
df['BB_High'] = bollinger.bollinger_hband()
df['BB_Low'] = bollinger.bollinger_lband()
df['BB_Mid'] = bollinger.bollinger_mavg()
df['RSI'] = RSIIndicator(close=df['收盘']).rsi()

# 生成交易信号
df['Signal'] = 0
df.loc[(df['收盘'] < df['BB_Low']) & (df['RSI'] < 30), 'Signal'] = 1
df.loc[(df['收盘'] > df['BB_High']) & (df['RSI'] > 70), 'Signal'] = -1

# 绘制图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

ax1.plot(df.index, df['收盘'], label='收盘价')
ax1.plot(df.index, df['BB_High'], label='布林上轨')
ax1.plot(df.index, df['BB_Low'], label='布林下轨')
ax1.plot(df.index, df['BB_Mid'], label='布林中轨')
ax1.set_title('贵州茅台 - 价格和布林带')
ax1.legend()

ax2.plot(df.index, df['RSI'], label='RSI')
ax2.axhline(y=70, color='r', linestyle='--')
ax2.axhline(y=30, color='g', linestyle='--')
ax2.set_title('RSI')
ax2.legend()

plt.tight_layout()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 这个策略在价格触及布林下轨且RSI低于30时产生买入信号,在价格触及布林上轨且RSI高于70时产生卖出信号。

# 5. ADX与快慢移动平均线
# ADX(平均趋向指标)用于衡量趋势的强度,而不是趋势的方向。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import ADXIndicator, SMAIndicator

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算指标
df['SMA20'] = SMAIndicator(close=df['收盘'], window=20).sma_indicator()
df['SMA50'] = SMAIndicator(close=df['收盘'], window=50).sma_indicator()
adx = ADXIndicator(high=df['最高'], low=df['最低'], close=df['收盘'])
df['ADX'] = adx.adx()

# 生成交易信号
df['Signal'] = 0
df.loc[(df['SMA20'] > df['SMA50']) & (df['ADX'] > 25), 'Signal'] = 1
df.loc[(df['SMA20'] < df['SMA50']) & (df['ADX'] > 25), 'Signal'] = -1

# 绘制图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

ax1.plot(df.index, df['收盘'], label='收盘价')
ax1.plot(df.index, df['SMA20'], label='20日均线')
ax1.plot(df.index, df['SMA50'], label='50日均线')
ax1.set_title('贵州茅台 - 价格和移动平均线')
ax1.legend()

ax2.plot(df.index, df['ADX'], label='ADX')
ax2.axhline(y=25, color='r', linestyle='--')
ax2.set_title('ADX')
ax2.legend()

plt.tight_layout()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 这个策略在20日均线上穿50日均线且ADX大于25时产生买入信号,在20日均线下穿50日均线且ADX大于25时产生卖出信号。

## 6. 移动平均线 + MACD + RSI
# 这种方法结合了趋势跟踪(移动平均线)、动量(MACD)和超买超卖(RSI)指标。

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator

plt.rcParams["font.sans-serif"] = ["STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

# 获取贵州茅台的股票数据
stock_code = "600519"
start_date = "20240101"
end_date = "20241018"

df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期', inplace=True)

# 计算指标
df['SMA50'] = SMAIndicator(close=df['收盘'], window=50).sma_indicator()
macd = MACD(close=df['收盘'])
df['MACD'] = macd.macd()
df['MACD_Signal'] = macd.macd_signal()
df['RSI'] = RSIIndicator(close=df['收盘']).rsi()

# 生成交易信号
df['Signal'] = 0
df.loc[(df['MACD'] > df['MACD_Signal']) & (df['收盘'] > df['SMA50']) & (df['RSI'] < 70), 'Signal'] = 1
df.loc[(df['MACD'] < df['MACD_Signal']) & (df['收盘'] < df['SMA50']) & (df['RSI'] > 30), 'Signal'] = -1

# 绘制图表
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)

ax1.plot(df.index, df['收盘'], label='收盘价')
ax1.plot(df.index, df['SMA50'], label='50日均线')
ax1.set_title('贵州茅台 - 价格和50日均线')
ax1.legend()

ax2.plot(df.index, df['MACD'], label='MACD')
ax2.plot(df.index, df['MACD_Signal'], label='MACD信号线')
ax2.bar(df.index, df['MACD'] - df['MACD_Signal'], label='MACD柱状图')
ax2.set_title('MACD')
ax2.legend()

ax3.plot(df.index, df['RSI'], label='RSI')
ax3.axhline(y=70, color='r', linestyle='--')
ax3.axhline(y=30, color='g', linestyle='--')
ax3.set_title('RSI')
ax3.legend()

plt.tight_layout()
plt.show()

# 打印信号变化点
print(df[df['Signal'] != df['Signal'].shift(1)])

# 这个策略在MACD上穿信号线、价格在50日均线之上且RSI低于70时产生买入信号,在MACD下穿信号线、价格在50日均线之下且RSI高于30时产生卖出信号。

# 通过这六种技术分析方法,我们可以从不同角度来分析贵州茅台的股价走势。每种方法都有其优缺点,在实际交易中,通常需要结合多种指标,
# 并配合基本面分析来做出决策。

# 需要注意的是,这些示例代码主要用于演示技术指标。在实际交易中,还需要考虑许多其他因素,如交易成本、滑点、风险管理等。
# 建议在使用这些策略进行实际交易之前,先在模拟环境中进行充分的测试和优化。