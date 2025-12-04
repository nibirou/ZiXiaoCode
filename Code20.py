# 1、问：pywencai 是不是没法用了

# 答案：可以用， 我之前写的程序用pywencai运行得好好的。

# 排查思路:

# 检查下node是否正确安装， 推荐用nvm安装 , 我用的node V18。

# 以mac为例 ，安装命令  

# brew install nvm 

# nvm i  18 

# nvm use 18 

# 2、问：通话顺wencai只能获取100只股票问题。

# 答案：  pywencai包 增加loop=True就可以了， 看github说明也有说明


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

# # Initialize Tushare with your token
# ts.set_token('XXXX')
# pro = ts.pro_api()

def get_previous_trading_day(date):
    # Get the trading calendar for the past week before the given date
    end_date = date
    start_date = end_date - timedelta(days=10)
    # Check if the selected date is Monday
    if date.weekday() == 0:  # Monday
        # Find the last Friday
        previous_date = date - pd.offsets.BusinessDay(3)
    else:
        # Find the previous trading day
        previous_date = date - pd.offsets.BusinessDay(1)

    return previous_date

# def get_previous_trading_day(date):
#     # Get the trading calendar for the past week before the given date
#     end_date = date
#     start_date = end_date - timedelta(days=10)
#
#     cal_df = pro.trade_cal(exchange='', start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
#
#     # Filter for open trading days and sort in descending order
#     open_days = cal_df[cal_df['is_open'] == 1]['cal_date'].sort_values(ascending=False)
#
#     # Return the previous trading day
#     return datetime.strptime(open_days.iloc[1], '%Y%m%d').date()  # iloc[1] because iloc[0] would be the input date itself

def get_limit_up_data(date):
    param = f"{date.strftime('%Y%m%d')}涨停，成交金额排序"
    df = pywencai.get(query=param, sort_key='成交金额', sort_order='desc', loop=True)
    selected_columns = ['股票代码', '股票简称', '最新价', '最新涨跌幅', f'首次涨停时间[{date.strftime("%Y%m%d")}]',
                        f'连续涨停天数[{date.strftime("%Y%m%d")}]', f'涨停原因类别[{date.strftime("%Y%m%d")}]',
                        f'a股市值(不含限售股)[{date.strftime("%Y%m%d")}]',
                        f'涨停类型[{date.strftime("%Y%m%d")}]']
    return df[selected_columns]

def get_concept_counts(df, date):
    concepts = df[f'涨停原因类别[{date.strftime("%Y%m%d")}]'].str.split('+').explode().reset_index(drop=True)
    concept_counts = concepts.value_counts().reset_index()
    concept_counts.columns = ['概念', '出现次数']
    return concept_counts

def app():
    st.title("A股涨停概念分析")

    # Date selection
    max_date = datetime.now().date()
    selected_date = st.date_input("选择分析日期", max_value=max_date, value=max_date)

    # Check if selected date is a trading day
    # cal_df = pro.trade_cal(exchange='', start_date=selected_date.strftime('%Y%m%d'), end_date=selected_date.strftime('%Y%m%d'))
    # is_trading_day = cal_df['is_open'].iloc[0] == 1

    # if not is_trading_day:
    #     st.warning(f"{selected_date}不是交易日。请选择一个交易日。")
    #     return
    if selected_date.weekday() == 5:
        st.write("当前为周六，无法获取数据，请选择其他日期。")
        return
    if selected_date.weekday() == 6:
        st.write("当前为周末，无法获取数据，请选择其他日期。")
        return

    previous_date = get_previous_trading_day(selected_date)

    st.write(f"分析日期: {selected_date} 和 {previous_date} (前一交易日)")

    # Fetch data for both days
    selected_df = get_limit_up_data(selected_date)
    previous_df = get_limit_up_data(previous_date)

    # Get concept counts for both days
    selected_concepts = get_concept_counts(selected_df, selected_date)
    previous_concepts = get_concept_counts(previous_df, previous_date)

    # Merge concept counts
    merged_concepts = pd.merge(selected_concepts, previous_concepts, on='概念', how='outer',
                               suffixes=('_selected', '_previous'))
    merged_concepts = merged_concepts.fillna(0)

    # Calculate change
    merged_concepts['变化'] = merged_concepts['出现次数_selected'] - merged_concepts['出现次数_previous']

    # Sort by '出现次数_selected' in descending order
    sorted_concepts = merged_concepts.sort_values('出现次数_selected', ascending=False)

    # Display total limit-up stocks for both days
    st.subheader("涨停股票数量变化")
    selected_total = len(selected_df)
    previous_total = len(previous_df)
    change = selected_total - previous_total

    col1, col2, col3 = st.columns(3)
    col1.metric("前一交易日涨停数", previous_total)
    col2.metric("选定日期涨停数", selected_total)
    col3.metric("变化", change, f"{change:+d}")

    # Display concept changes
    st.subheader("涨停概念变化")
    st.dataframe(sorted_concepts)

    # Create a bar chart for top 10 concepts
    top_10_concepts = sorted_concepts.head(10)

    fig = go.Figure(data=[
        go.Bar(name='选定日期', x=top_10_concepts['概念'], y=top_10_concepts['出现次数_selected']),
        go.Bar(name='前一交易日', x=top_10_concepts['概念'], y=top_10_concepts['出现次数_previous'])
    ])

    fig.update_layout(barmode='group', title='Top 10 涨停概念对比')
    st.plotly_chart(fig)

    # Display raw data
    st.subheader("选定日期涨停股票详情")
    st.dataframe(selected_df)

if __name__ == "__main__":
    app()