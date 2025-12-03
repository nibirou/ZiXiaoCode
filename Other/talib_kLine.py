import akshare as ak
import streamlit as st
import plotly.graph_objects as go
import talib
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="A股K线形态识别", layout="wide")
st.title("A股K线形态识别")

# 侧边栏参数设置
with st.sidebar:
    st.header("⚙️ 参数设置")
    symbol = st.text_input("股票代码", "600519")
    start_date = st.date_input("开始日期", datetime(2024, 10, 8))
    end_date = st.date_input("结束日期", datetime.now())
    
# 获取A股历史数据（使用stock_zh_a_history接口）
def get_stock_data(symbol, start, end):
    """获取A股前复权数据"""
    try:
        code = f"{symbol}"
        df = ak.stock_zh_a_hist(
            symbol=code, period="daily",
            start_date=start.strftime("%Y%m%d"),
            end_date=end.strftime("%Y%m%d"),
             adjust="qfq"
        )
        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date').sort_index()
    except Exception as e:
        st.error(f"数据获取失败：{str(e)}")
        return None
    
data = get_stock_data(symbol,start_date, end_date)

if data is not None:
    # 识别锤子线形态
    hammer_signals = talib.CDLHAMMER(data['open'], data['high'], data['low'], data['close'])
    signals = data[hammer_signals == 100]
    
    # 创建Plotly图表
    fig = go.Figure()
    
    # 绘制K线
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='K线',
        increasing_line_color='red',
        decreasing_line_color='green'
    ))
    
    # 标记锤子线信号
    if not signals.empty:
        fig.add_trace(go.Scatter(
            x=signals.index,
            y=signals['low'] * 0.98,
            mode='markers',
            marker=dict(
                color='rgba(0, 150, 0, 0.8)',
                size=12,
                symbol='triangle-up',
                line=dict(width=1, color='DarkSlateGrey')
            ),
            name='锤子线信号'
        ))
        
        # 图表布局优化
        fig.update_layout(
            title=f"{symbol}周期K线图 - 锤子线信号",
            xaxis=dict(
                type='date',
                rangeslider=dict(visible=False),
                title_text="日期"
            ),
            yaxis=dict(title_text="价格（前复权）"),
            hovermode="x unified",
            template="plotly_dark",
            height=600,
            margin=dict(l=50, r=50, b=50, t=100)
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示信号明细
        st.subheader("📋 信号明细")
        if not signals.empty:
            st.dataframe(
                signals.style.applymap(
                    lambda x: "background-color: #2c5f2d",
                    subset=['close']
                ),
                column_order=['open', 'high', 'low', 'close'],
                use_container_width=True
            )
        else:
            st.warning("当前参数范围内未检测到锤子线信号")