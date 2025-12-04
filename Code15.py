# 看着上面的效果，你会想到什么？

# 1、涨停数变少，说明投机情绪在逐渐退潮

# 2、概念涨停变化，比如 风电、军工、光伏 涨停数多起来了，说明了资金开始切换到了相对低位。

# 3、越早涨停的，说明资金越认可。尽量观察 越早涨停的股，相对更强势。

# 程序我准备用streamlit构建应用界面， tushare获取交易日历数据，  wencai获取涨停数分析。

# 另外程序运行时间可能要考虑的点：

# 比如今天是交易日，那么9点30之前执行， 基本是考虑10月22日、10月23日的涨停对比吧。   
# 交易时间段执行 判断当天什么时候题材概念比较火热。


import streamlit as st
import pywencai
import pandas as pd
from datetime import datetime, timedelta
import tushare as ts
import plotly.graph_objects as go

# Setting up pandas display options
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_colwidth', 100)

# Initialize Tushare with your token
ts.set_token('YOUR_TUSHARE_TOKEN')
pro = ts.pro_api()

def get_latest_trading_day():
    now = datetime.now()
    today = now.date()

    # Get the trading calendar for the past week
    cal_df = pro.trade_cal(exchange='', start_date=(today - timedelta(days=10)).strftime('%Y%m%d'), end_date=today.strftime('%Y%m%d'))

    # Filter for open trading days and sort in descending order
    open_days = cal_df[cal_df['is_open'] == 1]['cal_date'].sort_values(ascending=False)

    # Check if today is a trading day
    is_trading_day = cal_df[cal_df['cal_date'] == today.strftime('%Y%m%d')]['is_open'].iloc[0] == 1

    if is_trading_day:
        # If it's before 9：30 AM on a trading day, use the previous trading day
        if now.time() < datetime.strptime('09:30', '%H:%M').time():
            return open_days.iloc[1]
        else:
            return open_days.iloc[0]
    else:
        # If today is not a trading day, use the most recent trading day
        return open_days.iloc[0]

def get_previous_trading_day(date):
    # Get the trading calendar for the past week before the given date
    end_date = datetime.strptime(date, '%Y%m%d').date()
    start_date = end_date - timedelta(days=10)

    cal_df = pro.trade_cal(exchange='', start_date=start_date.strftime('%Y%m%d'), end_date=date)

    # Filter for open trading days and sort in descending order
    open_days = cal_df[cal_df['is_open'] == 1]['cal_date'].sort_values(ascending=False)

    # Return the previous trading day
    return open_days.iloc[1]  # iloc[1] because iloc[0] would be the input date itself

def get_limit_up_data(date):
    param = f"{date}涨停，非涉嫌信息披露违规且非立案调查且非ST，非科创板，非北交所"
    df = pywencai.get(query=param, sort_key='成交金额', sort_order='desc')
    selected_columns = ['股票代码', '股票简称', '最新价', '最新涨跌幅', f'首次涨停时间[{date}]', 
                        f'连续涨停天数[{date}]', f'涨停原因类别[{date}]', f'a股市值(不含限售股)[{date}]', 
                        f'涨停类型[{date}]']
    return df[selected_columns]

def get_concept_counts(df, date):
    concepts = df[f'涨停原因类别[{date}]'].str.split('+').explode().reset_index(drop=True)
    concept_counts = concepts.value_counts().reset_index()
    concept_counts.columns = ['概念', '出现次数']
    return concept_counts

def main():
    st.title("A股涨停概念分析")

    today = get_latest_trading_day()
    yesterday = get_previous_trading_day(today)

    st.write(f"分析日期: {today} (最新交易日) 和 {yesterday} (前一交易日)")

    # Fetch data for both days
    today_df = get_limit_up_data(today)
    yesterday_df = get_limit_up_data(yesterday)

    # Get concept counts for both days
    today_concepts = get_concept_counts(today_df, today)
    yesterday_concepts = get_concept_counts(yesterday_df, yesterday)

    # Merge concept counts
    merged_concepts = pd.merge(today_concepts, yesterday_concepts, on='概念', how='outer', suffixes=('_today', '_yesterday'))
    merged_concepts = merged_concepts.fillna(0)

    # Calculate change
    merged_concepts['变化'] = merged_concepts['出现次数_today'] - merged_concepts['出现次数_yesterday']

    # Sort by '出现次数_today' in descending order
    sorted_concepts = merged_concepts.sort_values('出现次数_today', ascending=False)

    # Display total limit-up stocks for both days
    st.subheader("涨停股票数量变化")
    today_total = len(today_df)
    yesterday_total = len(yesterday_df)
    change = today_total - yesterday_total

    col1, col2, col3 = st.columns(3)
    col1.metric("昨日涨停数", yesterday_total)
    col2.metric("今日涨停数", today_total)
    col3.metric("变化", change, f"{change:+d}")

    # Display concept changes
    st.subheader("涨停概念变化")
    st.dataframe(sorted_concepts)

    # Create a bar chart for top 10 concepts
    top_10_concepts = sorted_concepts.head(10)

    fig = go.Figure(data=[
        go.Bar(name='今日', x=top_10_concepts['概念'], y=top_10_concepts['出现次数_today']),
        go.Bar(name='昨日', x=top_10_concepts['概念'], y=top_10_concepts['出现次数_yesterday'])
    ])

    fig.update_layout(barmode='group', title='Top 10 涨停概念对比')
    st.plotly_chart(fig)

    # Display raw data
    st.subheader("今日涨停股票详情")
    st.dataframe(today_df)

if __name__ == "__main__":
    main()