import streamlit as st
from datetime import datetime, timedelta
import pywencai
import pandas as pd
import plotly.graph_objects as go
import pandas_market_calendars as mcal
from contextlib import contextmanager

# 设置页面配置
st.set_page_config(layout="wide", page_title="涨停股最高板分析")

# 设置页面标题
st.title('涨停股最高板分析')

@contextmanager
def st_spinner(text="处理中..."):
    try:
        with st.spinner(text):
            yield
    finally:
        pass

with st_spinner("正在获取和处理数据，请稍候..."):
    # 获取当前日期并往前推20天（增加天数以便滑动）
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=x)).strftime('%Y%m%d') for x in range(20)]

    # 获取中国的交易日历
    nyse = mcal.get_calendar('XSHG')
    trading_schedule = nyse.schedule(start_date=min(dates), end_date=max(dates))
    trading_days = trading_schedule.index.strftime('%Y%m%d').tolist()

    # 存储结果的列表
    results = []

    # 循环获取每个日期的数据，仅在交易日执行
    for date in dates:
        if date in trading_days:
            query = f"非ST，{date}连续涨停天数排序，涨停原因"
            try:
                data = pywencai.get(query=query)
                if not data.empty:
                    # 提取第一条记录（最高涨停股）
                    first_row = data.iloc[0]
                    results.append({
                        '日期': datetime.strptime(date, '%Y%m%d'),  # 转换为datetime对象
                        '股票简称': first_row['股票简称'],
                        '股票代码': first_row['股票代码'],
                        '连续涨停天数': first_row[f'连续涨停天数[{date}]'],
                        '涨停原因': first_row[f'涨停原因类别[{date}]']
                    })
            except Exception as e:
                st.error(f"查询 {date} 数据时出错: {e}")

    # 检查是否有数据
    if results:
        # 创建一个DataFrame来存储所有数据
        df_all = pd.DataFrame(results)

        # 按日期排序
        df_all = df_all.sort_values('日期')
        df_filtered = df_all

        # 绘制折线图
        fig = go.Figure()

        # 添加折线图
        fig.add_trace(go.Scatter(
            x=df_filtered['日期'],
            y=df_filtered['连续涨停天数'],
            mode='markers+lines+text',
            name='连续涨停天数',
            text=[f"{简称}"for 简称 in df_filtered['股票简称']],
            hovertext=[f"{简称}({代码})<br>涨停原因: {原因}"for 简称, 代码, 原因 in zip(df_filtered['股票简称'], df_filtered['股票代码'], df_filtered['涨停原因'])],
            hoverinfo='text',
            textposition='top center',
            marker=dict(size=12, color='red', symbol='circle'),
            line=dict(color='royalblue', width=2),
        ))

        # 更新布局
        fig.update_layout(
            title='最高涨停股连续涨停天数',
            xaxis_title='日期',
            yaxis_title='连续涨停天数',
            xaxis=dict(
                type='date',
                tickformat='%Y-%m-%d',
                tickangle=4
            ),
            hovermode='closest',
            font=dict(size=14),
            plot_bgcolor='rgba(240, 240, 240, 0.95)',
            showlegend=True,
            height=800,
            margin=dict(l=50, r=50, t=80, b=100),
        )

        # 添加自定义悬浮框样式
        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Rockwell"
            )
        )

        # 全屏展示图表
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("没有找到符合条件的数据")