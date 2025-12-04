import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    df['MACD'] = macd
    df['Signal'] = signal_line
    df['Histogram'] = histogram
    return df


def detect_divergence(df, window=10):
    df['Price_High'] = df['close'].rolling(window=window, center=True).max()
    df['Price_Low'] = df['close'].rolling(window=window, center=True).min()
    df['MACD_High'] = df['MACD'].rolling(window=window, center=True).max()
    df['MACD_Low'] = df['MACD'].rolling(window=window, center=True).min()

    df['Bullish_Divergence'] = (df['close'] == df['Price_Low']) & (df['MACD'] > df['MACD_Low'])
    df['Bearish_Divergence'] = (df['close'] == df['Price_High']) & (df['MACD'] < df['MACD_High'])

    return df


def plot_stock_with_macd(df):
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

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=2,
                  col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal', line=dict(color='orange')), row=2,
                  col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Histogram'], name='Histogram'), row=2, col=1)

    # Divergence points
    bullish_divergence = df[df['Bullish_Divergence']]
    bearish_divergence = df[df['Bearish_Divergence']]

    fig.add_trace(go.Scatter(x=bullish_divergence.index, y=bullish_divergence['low'], mode='markers',
                             name='底背离', marker=dict(symbol='triangle-up', size=10, color='green')), row=1, col=1)
    fig.add_trace(go.Scatter(x=bearish_divergence.index, y=bearish_divergence['high'], mode='markers',
                             name='顶背离', marker=dict(symbol='triangle-down', size=10, color='red')), row=1, col=1)

    fig.update_layout(title='股票K线图、MACD指标和背离', xaxis_rangeslider_visible=False, height=800)
    fig.update_xaxes(title_text='日期', row=2, col=1)
    fig.update_yaxes(title_text='价格', row=1, col=1)
    fig.update_yaxes(title_text='MACD', row=2, col=1)

    return fig


def main():
    st.title('股票顶背离和底背离分析')

    stock_code = st.text_input('请输入股票代码（例如：sh000001表示上证指数）:', 'sh000001')

    if st.button('分析'):
        try:
            with st.spinner('正在获取股票数据...'):
                end_date = datetime.now()
                #end_date = datetime(2024, 12, 2)
                start_date = end_date - timedelta(days=90)  # 获取最近90天的数据

                if stock_code.startswith('sh') or stock_code.startswith('sz'):
                    df = ak.stock_zh_index_daily(symbol=stock_code)
                else:
                    df = ak.stock_zh_a_daily(symbol=stock_code)

            df = df.rename(columns={
                "date": "Date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close"
            })

            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df = df.loc[start_date:end_date]

            df = calculate_macd(df)
            df = detect_divergence(df)

            st.plotly_chart(plot_stock_with_macd(df))

            st.subheader('最近的背离信号：')
            recent_divergences = df[df['Bullish_Divergence'] | df['Bearish_Divergence']].tail(5)
            for date, row in recent_divergences.iterrows():
                if row['Bullish_Divergence']:
                    st.write(f"{date.date()}: 底背离 (价格: {row['close']:.2f}, MACD: {row['MACD']:.4f})")
                elif row['Bearish_Divergence']:
                    st.write(f"{date.date()}: 顶背离 (价格: {row['close']:.2f}, MACD: {row['MACD']:.4f})")

        except Exception as e:
            st.error(f'发生错误: {str(e)}')
            st.error('请确保输入了正确的股票代码。对于上证指数，请使用sh000001；对于个股，请使用类似sh600000的格式。')


if __name__ == "__main__":
    main()

# 那上面说的11.26底背离的信号， 什么时候才会计算出来。 不好意思 12.2收盘才能得到这个答案。
# 熟悉代码的同学会发现， MACD其实是一个滞后指标：它基于移动平均线计算，本质上反映的是过去的价格变动。
# 背离的确认需要时间：通常需要几个交易日来确认价格和MACD的背离模式。

# 信号的计算和显示：取决于用于检测背离的算法，可能需要额外的确认周期。

# 这里从4个方面总结下KDJ和MACD指标的区别。 

# 1、指标特性：

# KDJ是一个快速反应的动量指标，它基于最近N天（通常是9天）的最高价、最低价和收盘价计算。

# MACD则是基于两个不同周期（通常是12天和26天）的指数移动平均线（EMA）计算得出。

# 2、计算方法：

# KDJ的计算涉及较短的时间周期，因此对价格变化的反应更快。

# MACD由于使用了较长的移动平均线，对价格变化的反应相对较慢。

# 3、信号生成：

# KDJ的金叉死叉是由K线和D线的交叉产生的，这两条线的变动相对较快。

#  MACD的金叉死叉是由MACD线和信号线的交叉产生的，这两条线的变动相对较慢。

# 4、灵敏度：

# KDJ能够更快地捕捉到短期的价格动量变化，因此在短期交易中更受欢迎。

#  MACD则更适合捕捉中长期的趋势变化，信号相对较少但可能更可靠。



# 优缺点：

# KDJ的高灵敏度意味着它可以提供更多的交易机会，但也可能产生更多的假信号。

# MACD的信号相对较少，但可能更能反映重要的趋势转折点。

