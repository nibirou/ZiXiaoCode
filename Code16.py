
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tushare as ts
import pywencai
from datetime import datetime, timedelta

# Initialize Tushare with your token
ts.set_token('Tushare with your token')
pro = ts.pro_api()


def get_limit_up_stocks(date):
    query = f"{date}涨停"
    df = pywencai.get(query=query, sort_key='涨跌幅', sort_order='desc')
    return df[['股票代码', '股票简称', '最新价', '最新涨跌幅']]


def get_next_trading_day(date):
    next_day = (datetime.strptime(date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
    while True:
        df = pro.trade_cal(exchange='', start_date=next_day, end_date=next_day)
        if df.iloc[0]['is_open'] == 1:
            return next_day
        next_day = (datetime.strptime(next_day, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')


def get_stock_data(stock_code, start_date, end_date):
    df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date')
    return df


def calculate_next_day_performance(limit_up_stocks, date):
    next_trading_day = get_next_trading_day(date)

    results = []
    for _, row in limit_up_stocks.iterrows():
        stock_code = row['股票代码']
        stock_name = row['股票简称']

        df = get_stock_data(stock_code, date, next_trading_day)

        if len(df) >= 2:
            limit_up_price = df.iloc[0]['close']
            next_day_price = df.iloc[1]['close']
            change_pct = (next_day_price - limit_up_price) / limit_up_price * 100

            results.append({
                '股票代码': stock_code,
                '股票简称': stock_name,
                '涨停价': limit_up_price,
                '次日收盘价': next_day_price,
                '次日涨跌幅': change_pct
            })

    return pd.DataFrame(results)


def display_stock_analysis(stock_code, selected_date):
    # Date range for data
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    start_date = (datetime.strptime(selected_date, '%Y%m%d') - timedelta(days=60)).strftime('%Y%m%d')

    # Fetch stock data
    df = get_stock_data(stock_code, start_date, end_date)

    if not df.empty:
        # Convert selected_date to datetime for comparison
        selected_datetime = pd.to_datetime(selected_date)

        # Create stock trend chart
        fig = go.Figure()

        # Add candlestick chart with red for positive changes and green for negative changes
        fig.add_trace(go.Candlestick(
            x=df['trade_date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='red',  # Red for positive changes
            decreasing_line_color='green',  # Green for negative changes
            name="股价"
        ))

        # Add marker for selected date
        selected_price = df[df['trade_date'] == selected_datetime]['close'].values[0]
        fig.add_trace(go.Scatter(
            x=[selected_datetime],
            y=[selected_price],
            mode='markers',
            marker=dict(size=10, color='blue', symbol='star'),
            name="选择日期"
        ))

        # Update layout
        fig.update_layout(
            title=f"{stock_code} 近期走势",
            xaxis_title="日期",
            yaxis_title="价格",
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
        )

        st.plotly_chart(fig)
    else:
        st.error("无法获取股票数据，请检查股票代码是否正确。")


def main():
    st.title("涨停股票分析")

    # Date selection with default set to October 8, 2024
    default_date = datetime(2024, 10, 8).date()
    selected_date = st.date_input("选择日期", value=default_date, min_value=datetime(2020, 1, 1).date(),
                                  max_value=datetime.now().date())
    date_str = selected_date.strftime('%Y%m%d')

    # Fetch limit-up stocks
    limit_up_stocks = get_limit_up_stocks(date_str)

    # Calculate next day performance
    next_day_performance = calculate_next_day_performance(limit_up_stocks, date_str)

    # Display limit-up stocks table with next day performance
    st.subheader(f"{date_str} 涨停股票及次日表现")

    # Custom styling function for the dataframe
    def style_negative(v, props=''):
        return props if v < 0 else None

    def style_positive(v, props=''):
        return props if v > 0 else None

    # Apply the styling to the dataframe
    styled_df = next_day_performance.style.format({
        '涨停价': '{:.2f}',
        '次日收盘价': '{:.2f}',
        '次日涨跌幅': '{:.2f}%'
    }).applymap(style_negative, props='color:green;', subset=['次日涨跌幅']) \
        .applymap(style_positive, props='color:red;', subset=['次日涨跌幅'])

    st.dataframe(styled_df)

    # Stock selection for detailed analysis
    selected_stock = st.selectbox("选择股票进行详细分析",
                                  next_day_performance['股票代码'] + ' - ' + next_day_performance['股票简称'])

    if selected_stock:
        stock_code = selected_stock.split(' - ')[0]
        display_stock_analysis(stock_code, date_str)


if __name__ == "__main__":
    main()

# 默认时间我设置20241008， 防止后续没有交易日数据。

# 使用方法：

# 1、确保安装了所有必需的库：

# pip install streamlit pandas plotly tushare pywencai

# 2、将'YOUR_TUSHARE_TOKEN'替换为你的实际Tushare API令牌。

# 将代码保存到文件（例如`limit_up_analysis.py`）。

# 运行Streamlit应用：

# streamlit run limit_up_analysis.py