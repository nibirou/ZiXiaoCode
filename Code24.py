# 在这个瞬息万变的股市中，如何让你的投资决策更科学、更有效？量化股票交易为我们提供了一个全新的视角。通过数据分析和模型计算，我们可以更清晰地了解投资的风险和收益。今天，我们就来聊聊量化股票中的两个重要指标：最大回撤率和总收益率。

# 量化投资不仅仅是数字的游戏。它背后蕴含着对市场的深刻理解和对数据的敏锐洞察。每一个数字背后，都有无数投资者的故事与情感。我们需要的不仅是冷冰冰的计算，更是对市场的热爱与追求。

# 最大回撤率：投资的“安全绳” 最大回撤率是衡量投资风险的重要指标。它表示在一段时间内，投资组合从最高点到最低点的最大跌幅。简单来说，就是你在这段时间内可能面临的最大损失。

# 想象一下，你的投资账户在某个时期的价值达到了100万元。接着，由于市场波动，账户的价值下滑到80万元。这时，你的最大回撤率就是20%。这个数字告诉你，面对市场的波动，你的资金可能会面临多大的风险。

# 在量化投资中，了解最大回撤率可以帮助我们设定合理的止损点。它让我们在面对市场波动时，能够保持冷静，避免情绪化的决策。毕竟，投资就像一场马拉松，保持稳定的步伐比一时的冲刺更为重要。

# 总收益率：投资的“成绩单” 总收益率是衡量投资回报的重要指标。它反映了你在一定时间内的投资收益情况。计算总收益率的方法很简单：用期末资产价值减去期初资产价值，再除以期初资产价值，最后乘以100%即可。

# 比如，你在某个时间点投资了50万元，经过一段时间的努力，你的投资价值变成了70万元。那么你的总收益率就是(70-50)/50 * 100% = 40%。这个数字不仅是你投资的成果，更是你对市场理解的体现。

# 总收益率的计算可以帮助我们评估不同投资策略的有效性。通过对比不同策略的收益率，我们可以找到最适合自己的投资方式。量化投资的魅力在于，它能够让我们通过数据分析，找到最优的投资决策。

# 如何计算这两个指标？ 在量化投资中，我们可以通过编程来计算最大回撤率和总收益率。使用Python等编程语言，可以轻松实现这些计算。以下是一个简单的示例代码，帮助你理解如何计算这两个指标：

import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
def fetch_stock_data(stock_code, start_date, end_date):
    # 获取股票历史数据
    stock_data = ak.stock_zh_a_daily(symbol=stock_code, start_date=start_date, end_date=end_date)
    stock_data.reset_index(inplace=True)  # 重置索引
    stock_data['date'] = pd.to_datetime(stock_data['date'])  # 转换日期格式
    stock_data.set_index('date', inplace=True)  # 将日期设置为索引
    return stock_data

def calculate_max_drawdown(prices):
    cumulative_returns = (1 + prices).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()  # 最大回撤
    return max_drawdown

def main():
    st.title("股票回测与K线图")

    # 输入股票代码
    stock_code = st.text_input("输入股票代码（如 sh600000）:", "sh600000")

    # 输入开始和结束时间
    start_date = st.date_input("选择开始时间:", pd.to_datetime("2024-10-08"))
    end_date = st.date_input("选择结束时间:", pd.to_datetime("2024-12-27"))

    if st.button("获取数据"):
        # 获取股票数据
        stock_data = fetch_stock_data(stock_code, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

        # 计算每日收益率
        stock_data['returns'] = stock_data['close'].pct_change()

        # 计算最大回撤率
        max_drawdown = calculate_max_drawdown(stock_data['returns'].fillna(0))  # 填充NaN值
        st.write(f"最大回撤率: {max_drawdown:.2%}")

        # 计算总收益率
        total_return = (stock_data['close'].iloc[-1] / stock_data['close'].iloc[0]) - 1
        st.write(f"总收益率: {total_return:.2%}")


        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

        # 绘制K线图
        fig.add_trace(go.Candlestick(x=stock_data.index,
                                               open=stock_data['open'],
                                               high=stock_data['high'],
                                               low=stock_data['low'],
                                               close=stock_data['close'],
                                               increasing_line_color='red',
                                               decreasing_line_color='green',
                                               name='K线图'))
        fig.add_trace(go.Bar(
            x=stock_data.index,
            y=stock_data['volume'],
            name='成交量',
            marker_color='rgba(0, 0, 255, 0.5)'
        ), row=2, col=1)

        ma5 = stock_data['close'].rolling(window=5).mean()
        ma10 = stock_data['close'].rolling(window=10).mean()
        ma20 = stock_data['close'].rolling(window=20).mean()

        fig.add_trace(go.Scatter(x=stock_data.index, y=ma5, name='MA5', line=dict(color='blue', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=ma10, name='MA10', line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=stock_data.index, y=ma20, name='MA20', line=dict(color='green', width=1)), row=1, col=1)

        fig.update_layout(title=f"{stock_code} K线图",
                          xaxis_title='日期',
                          yaxis_title='价格',
                          xaxis_rangeslider_visible=False)

        st.plotly_chart(fig)

if __name__ == "__main__":
    main()