import streamlit as st
from datetime import datetime, timedelta
import pywencai
import pandas as pd
import plotly.graph_objects as go
import pandas_market_calendars as mcal

# 设置页面标题
st.title('涨停股最高板分析')

# 获取当前日期并往前推7天
end_date = datetime.now()
dates = [(end_date - timedelta(days=x)).strftime('%Y%m%d') for x in range(10)]

# 获取中国的交易日历
nyse = mcal.get_calendar('XSHG')
trading_schedule = nyse.schedule(start_date=min(dates), end_date=max(dates))
trading_days = trading_schedule.index.strftime('%Y%m%d').tolist()

# 存储结果的列表
results = []

# 循环获取每个日期的数据，仅在交易日执行
for date in dates:
    if date in trading_days:
        query = f"非ST，{date}连续涨停天数排序"
        try:
            data = pywencai.get(query=query)
            if not data.empty:
                # 提取第一条记录（最高涨停股）
                first_row = data.iloc[0]
                results.append({
                    '日期': date,
                    '股票简称': first_row['股票简称'],
                    '股票代码': first_row['股票代码'],
                    '连续涨停天数': first_row[f'连续涨停天数[{date}]']
                })
        except Exception as e:
            st.write(f"查询 {date} 数据时出错: {e}")

# 检查是否有数据
if results:
    # 创建一个DataFrame来存储所有数据
    df_all = pd.DataFrame(results)

    # 绘制折线图
    fig = go.Figure()

    # 添加折线图
    fig.add_trace(go.Scatter(
        x=df_all['日期'],
        y=df_all['连续涨停天数'],
        mode='markers+lines+text',  # 添加标记和文本显示
        name='连续涨停天数',
        text=df_all['股票简称'] + ' (' + df_all['股票代码'] + ')',  # 显示股票简称和代码
        textposition='top center',  # 文本位置
        marker=dict(size=10, color='blue', symbol='circle'),  # 设置标记样式
        line=dict(color='royalblue', width=2),  # 设置线条颜色和宽度
    ))

    # 更新布局
    fig.update_layout(
        title='最近10天最高涨停股连续涨停天数',
        xaxis_title='日期',
        yaxis_title='连续涨停天数',
        xaxis=dict(tickmode='array', tickvals=df_all['日期'], ticktext=df_all['日期']),
        hovermode='x unified',
        font=dict(size=12),  # 设置字体大小
        plot_bgcolor='rgba(240, 240, 240, 0.95)',  # 设置背景颜色
        showlegend=True,
        height=600  # 设置图表高度
    )

    # 添加网格线
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')

    # 全屏展示图表
    st.plotly_chart(fig, use_container_width=True)  # 设置为全宽
else:
    st.write("没有找到符合条件的数据")

# 上面的代码通过使用Streamlit、PyWencai、Pandas和Plotly等工具，实现了一个交互式的涨停股分析应用。
# 龙头选手可以直观地查看最近几天的最高涨停股及其连续涨停天数，帮助投资者做出更明智的决策。代码上面附上了， 
# 如果想偷懒直接要文件的，可以加我微信。

# 主要依赖库

# Streamlit：用于构建Web应用，提供简单的界面和交互功能。

# PyWencai：用于获取股票市场的数据。

# Pandas：用于数据处理和分析。

# Plotly：用于创建交互式图表。

# Pandas Market Calendars：用于获取中国股市的交易日历。


# 为什么上面的方案不是最佳方案呢？ 因为pywencai.get调用频次太高，可能会有问题。 
# 其实最好的方式是把每日的涨停最高板入库， 然后取出进行折线图排列。

# 说实话，我本来不想写这篇文章的。  毕竟我不是龙头选手，看到最高板我基本不会选择。
# 像同花顺、东方财富 各种软件 都有xx最高板，分析得非常六。 自己这个实现实属有点粗糙了