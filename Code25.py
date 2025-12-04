# 有没有什么指标能够来判断变盘信号。
# 我们可以用KDJ来判断大盘信号。 金叉买入，死叉卖出。

# 趁着周末有空，写一个例子供大家参考。 先看实际效果

import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def calculate_kdj(df, n=9, m1=3, m2=3):
    low_list = df['low'].rolling(window=n, min_periods=1).min()
    high_list = df['high'].rolling(window=n, min_periods=1).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100

    df['K'] = pd.DataFrame(rsv).ewm(com=m1 - 1, adjust=False).mean()
    df['D'] = df['K'].ewm(com=m2 - 1, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    return df


def detect_crosses(df):
    df['Golden_Cross'] = (df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1))
    df['Death_Cross'] = (df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1))
    return df


def plot_candlestick_kdj(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 increasing_line_color='red',
                                 decreasing_line_color='green',
                                 name='K线'), row=1, col=1)

    # KDJ lines
    fig.add_trace(go.Scatter(x=df.index, y=df['K'], mode='lines', name='K', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['D'], mode='lines', name='D', line=dict(color='orange')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['J'], mode='lines', name='J', line=dict(color='purple')), row=2, col=1)

    # Golden crosses
    golden_crosses = df[df['Golden_Cross']]
    fig.add_trace(go.Scatter(x=golden_crosses.index, y=golden_crosses['K'], mode='markers',
                             name='金叉', marker=dict(symbol='triangle-up', size=10, color='red')), row=2, col=1)

    # Death crosses
    death_crosses = df[df['Death_Cross']]
    fig.add_trace(go.Scatter(x=death_crosses.index, y=death_crosses['K'], mode='markers',
                             name='死叉', marker=dict(symbol='triangle-down', size=10, color='green')), row=2, col=1)

    fig.update_layout(title='股票K线图和KDJ指标（最近3个月）', xaxis_rangeslider_visible=False, height=800)
    fig.update_xaxes(title_text='日期', row=2, col=1)
    fig.update_yaxes(title_text='价格', row=1, col=1)
    fig.update_yaxes(title_text='KDJ值', row=2, col=1)

    return fig


def main():
    st.title('股票KDJ金叉死叉预警系统')

    # 用户输入股票代码
    stock_code = st.text_input('请输入股票代码（例如：sh000001 表示上证指数）:', 'sh000001')

    if st.button('分析'):
        try:
            # 使用 AKShare 获取股票数据
            with st.spinner('正在获取股票数据...'):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)  # 获取最近3个月的数据

                if stock_code.startswith('sh') or stock_code.startswith('sz'):
                    df = ak.stock_zh_index_daily(symbol=stock_code)
                else:
                    df = ak.stock_zh_a_daily(symbol=stock_code)

            # 重命名列
            df = df.rename(columns={
                "date": "Date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close"
            })

            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

            # 筛选最近3个月的数据
            df = df.loc[start_date:end_date]

            # 计算KDJ指标
            df = calculate_kdj(df)
            df = detect_crosses(df)

            # 绘制K线图和KDJ图
            st.plotly_chart(plot_candlestick_kdj(df))

            # 输出最近的金叉和死叉
            recent_crosses = df[df['Golden_Cross'] | df['Death_Cross']].tail(5)

            st.subheader('最近的KDJ交叉信号：')
            for date, row in recent_crosses.iterrows():
                if row['Golden_Cross']:
                    st.write(f"{date.date()}: 金叉 (K: {row['K']:.2f}, D: {row['D']:.2f})")
                elif row['Death_Cross']:
                    st.write(f"{date.date()}: 死叉 (K: {row['K']:.2f}, D: {row['D']:.2f})")

            # 检查最新的数据点是否接近交叉
            latest = df.iloc[-1]
            if abs(latest['K'] - latest['D']) < 1:  # 你可以调整这个阈值
                st.warning(f"警告：最新数据点 ({latest.name.date()}) 接近交叉！")
                st.write(f"K: {latest['K']:.2f}, D: {latest['D']:.2f}")

            st.subheader(f'当前KDJ值 (日期: {latest.name.date()}):')
            st.write(f"K: {latest['K']:.2f}")
            st.write(f"D: {latest['D']:.2f}")
            st.write(f"J: {latest['J']:.2f}")

        except Exception as e:
            st.error(f'发生错误: {str(e)}')
            st.error('请确保输入了正确的股票代码。对于上证指数，请使用 sh000001；对于个股，请使用类似 sh600000 的格式。')


if __name__ == "__main__":
    main()

# 下面是KDJ技术指标的科普。
# KDJ指标简介
# KDJ指标，也称为随机指标（Stochastic Oscillator），是由乔治·莱恩（George Lane）在20世纪50年代开发的。这个指标基于一个简单的观察：在上涨趋势中，收盘价往往接近当日最高价；而在下跌趋势中，收盘价往往接近当日最低价。

# KDJ指标由三条线组成：

# K线：快速线，反映股价最近的变化趋势
# D线：慢速线，K线的移动平均，用于确认K线的变动
# J线：用于观察股价的超买超卖状态
# KDJ指标的计算方法
# KDJ指标的计算过程如下：

# 计算RSV（Raw Stochastic Value）： RSV = (收盘价 - N日内最低价) / (N日内最高价 - N日内最低价) × 100

# 其中N通常取9，称为9日KDJ。

# 计算K值： 当日K值 = 2/3 × 前一日K值 + 1/3 × 当日RSV

# 计算D值： 当日D值 = 2/3 × 前一日D值 + 1/3 × 当日K值

# 计算J值： J = 3K - 2D

# 金叉和死叉的形成
# KDJ指标中的金叉和死叉是投资者常用的交易信号：

# 金叉：当K线从下向上穿过D线时形成，被认为是买入信号。
# 死叉：当K线从上向下穿过D线时形成，被认为是卖出信号。
# KDJ金叉死叉预测股票走势的理论基础
# KDJ指标预测股票走势的理论基础主要有以下几点：

# 动量理论：KDJ指标反映了股价的动量。金叉形成时，表明上涨动能增强；死叉形成时，表明下跌动能增强。

# 超买超卖理论：当K、D值接近100时，被认为是超买状态，股价可能会回落；当K、D值接近0时，被认为是超卖状态，股价可能会反弹。

# 趋势确认：金叉和死叉的形成可以被视为趋势的确认信号。金叉确认上涨趋势，死叉确认下跌趋势。

# 价格与指标背离：当股价创新高而KDJ指标没有创新高，或股价创新低而KDJ指标没有创新低时，可能预示着趋势即将反转。

# KDJ金叉死叉预测的合理性分析
# 技术面反映：KDJ指标综合考虑了一段时期内的最高价、最低价和收盘价，能够较好地反映股价的波动情况和市场情绪。

# 趋势跟踪：金叉和死叉信号有助于投资者跟踪市场趋势，特别是在明确的上升或下降趋势中，这些信号的准确性较高。

# 超买超卖判断：KDJ指标可以帮助投资者识别可能的超买或超卖状态，从而预测潜在的价格反转。

# 市场情绪指示：KDJ指标的变化可以反映市场参与者的情绪变化，有助于投资者把握市场心理。

# 多周期确认：通过在不同时间周期（如日线、周线、月线）上观察KDJ指标，可以得到更可靠的交易信号。

# KDJ金叉死叉预测的局限性
# 尽管KDJ指标在技术分析中广受欢迎，但它也存在一些局限性：

# 滞后性：作为一个跟随型指标，KDJ的金叉和死叉信号往往出现在价格变动之后，可能导致错过最佳入场或出场时机。

# 震荡市中的假信号：在横盘整理或者小幅震荡的市场中，KDJ可能产生频繁的金叉死叉信号，导致过度交易。

# 单一指标的局限性：仅依赖KDJ指标进行交易决策可能忽视其他重要的市场因素，如基本面、宏观经济环境等。

# 参数敏感性：KDJ指标的表现受其参数（如周期选择）的影响较大，不同的参数设置可能导致不同的信号。

# 无法预测黑天鹅事件：突发性的重大事件可能导致股价剧烈波动，这是KDJ指标无法预测的。

# 市场效率假说的挑战：如果市场是完全有效的，那么过去的价格信息（KDJ指标所基于的）就不应该对未来价格产生影响。