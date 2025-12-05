import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_stock_data(stock_code, start_date, end_date):
    try:
        stock_data = ak.stock_zh_a_daily(symbol=stock_code, start_date=start_date, end_date=end_date)
        stock_data.reset_index(inplace=True)
        stock_data['date'] = pd.to_datetime(stock_data['date'])
        stock_data.set_index('date', inplace=True)
        return stock_data
    except Exception as e:
        st.error(f"获取股票数据时出错: {str(e)}")
        return None


def identify_extreme_points(data, window=5):
    data['high_point'] = data['high'].rolling(window=window, center=True).apply(lambda x: x.argmax() == window // 2)
    data['low_point'] = data['low'].rolling(window=window, center=True).apply(lambda x: x.argmin() == window // 2)
    # Ensure boolean type
    data['high_point'] = data['high_point'].astype(bool)
    data['low_point'] = data['low_point'].astype(bool)
    return data


def connect_extreme_points(data):
    extreme_points = data[data['high_point'] | data['low_point']].copy()
    extreme_points['point_type'] = np.where(extreme_points['high_point'], 'high', 'low')
    extreme_points['value'] = np.where(extreme_points['high_point'], extreme_points['high'], extreme_points['low'])
    return extreme_points


def app():
    st.title("股票K线图与缠论分析")

    col1, col2 = st.columns(2)
    with col1:
        stock_code = st.text_input("输入股票代码（如 sh000001）:", "sh000001")
    with col2:
        time_period = st.selectbox("选择时间周期", ["1个月", "3个月", "6个月", "1年", "自定义"])

    if time_period == "自定义":
        start_date = st.date_input("选择开始时间:", pd.to_datetime("2024-10-08"))
        end_date = st.date_input("选择结束时间:", pd.to_datetime("2025-01-20"))
    else:
        end_date = pd.Timestamp.now()
        if time_period == "1个月":
            start_date = end_date - pd.DateOffset(months=1)
        elif time_period == "3个月":
            start_date = end_date - pd.DateOffset(months=3)
        elif time_period == "6个月":
            start_date = end_date - pd.DateOffset(months=6)
        else:  # 1年
            start_date = end_date - pd.DateOffset(years=1)

    if st.button("获取数据并分析"):
        with st.spinner("正在获取数据并进行分析..."):
            stock_data = fetch_stock_data(stock_code, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

            if stock_data is not None and not stock_data.empty:
                # 缠论分析
                stock_data = identify_extreme_points(stock_data)
                extreme_points = connect_extreme_points(stock_data)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

                # K线图
                fig.add_trace(go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['open'],
                    high=stock_data['high'],
                    low=stock_data['low'],
                    close=stock_data['close'],
                    increasing_line_color='red',
                    decreasing_line_color='green',
                    name='K线图'
                ), row=1, col=1)

                # 成交量
                # fig.add_trace(go.Bar(
                #     x=stock_data.index,
                #     y=stock_data['volume'],
                #     name='成交量',
                #     marker_color='rgba(0, 0, 255, 0.5)'
                # ), row=2, col=1)

                # 移动平均线
                #ma_periods = [5, 10, 20]
                #colors = ['blue', 'orange', 'green']

                # for period, color in zip(ma_periods, colors):
                #     ma = stock_data['close'].rolling(window=period).mean()
                #     fig.add_trace(go.Scatter(
                #         x=stock_data.index,
                #         y=ma,
                #         name=f'MA{period}',
                #         line=dict(color=color, width=1)
                #     ), row=1, col=1)

                # 缠论分析：标记最高点和最低点
                fig.add_trace(go.Scatter(
                    x=extreme_points[extreme_points['point_type'] == 'high'].index,
                    y=extreme_points[extreme_points['point_type'] == 'high']['value'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='red'),
                    name='最高点'
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=extreme_points[extreme_points['point_type'] == 'low'].index,
                    y=extreme_points[extreme_points['point_type'] == 'low']['value'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='green'),
                    name='最低点'
                ), row=1, col=1)

                # 连接最高点和最低点
                for i in range(1, len(extreme_points)):
                    fig.add_trace(go.Scatter(
                        x=[extreme_points.index[i - 1], extreme_points.index[i]],
                        y=[extreme_points['value'].iloc[i - 1], extreme_points['value'].iloc[i]],
                        mode='lines',
                        line=dict(color='purple', width=1),
                        showlegend=False
                    ), row=1, col=1)

                fig.update_layout(
                    title=f"{stock_code} K线图与缠论分析",
                    xaxis_title='日期',
                    yaxis_title='价格',
                    xaxis_rangeslider_visible=False,
                    height=800
                )

                st.plotly_chart(fig, use_container_width=True)

                #st.subheader("缠论分析结果")
                #st.write(f"识别到的极值点数量: {len(extreme_points)}")
                #st.write("极值点详情:")
                #st.dataframe(extreme_points[['point_type', 'value']])

                #st.dataframe(stock_data)
            else:
                st.error("无法获取或处理股票数据，请检查股票代码是否正确，并确保选择了有效的日期范围。")


if __name__ == "__main__":
    app()