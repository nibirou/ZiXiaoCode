import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import plotly.express as px

def fetch_market_data():
    try:
        # 使用AKShare获取A股市场现货数据
        stock_zh_a_spot_df = ak.stock_zh_a_spot_em()

        return stock_zh_a_spot_df
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None, None, None

def calculate_market_overview(df):
    total_stocks = len(df)
    up_stocks = len(df[df['涨跌幅'] > 0])
    down_stocks = len(df[df['涨跌幅'] < 0])
    flat_stocks = total_stocks - up_stocks - down_stocks

    overview = {
        '总成交额(亿)': round(df['成交额'].sum() / 100000000, 2),
        '上涨家数': up_stocks,
        '下跌家数': down_stocks,
        '平盘家数': flat_stocks,
        '涨跌比': round(up_stocks / (down_stocks + 1e-5), 2),  # 防止除以零
        '平均涨跌幅': round(df['涨跌幅'].mean(), 2)
    }
    return overview

def calculate_stock_distribution(df):
    bins = [-np.inf, -10, -7, -5, -3, 0, 3, 5, 7, 10, np.inf]
    labels = ['跌幅10%以上', '跌幅7%-10%', '跌幅5%-7%', '跌幅3%-5%', '跌幅0%-3%',
              '涨幅0%-3%', '涨幅3%-5%', '涨幅5%-7%', '涨幅7%-10%', '涨幅10%以上']
    df['distribution'] = pd.cut(df['涨跌幅'], bins=bins, labels=labels)
    distribution = df['distribution'].value_counts().sort_index()
    return distribution

def plot_distribution(distribution):
    fig = px.bar(
        x=distribution.index,
        y=distribution.values,
        labels={'x': '涨跌幅区间', 'y': '股票数量'},
        title="市场涨跌分布"
    )
    fig.update_traces(marker_color=['red'if'涨'in x else'green'for x in distribution.index],
                      text=distribution.values,  # 在条形上显示数量
                      textposition='auto')  # 自动放置文本位置
    return fig

# 主应用逻辑
def app():
    # 设置页面配置
    st.set_page_config(page_title="A股市场概况", layout="wide")

    # 标题
    st.title("A股市场概况")

    with st.spinner("正在获取数据..."):
        stock_zh_a_spot_df = fetch_market_data()

    if stock_zh_a_spot_df is not None:
        # 计算市场概览
        overview = calculate_market_overview(stock_zh_a_spot_df)

        # 计算股票分布
        distribution = calculate_stock_distribution(stock_zh_a_spot_df)

        # 显示市场概览
        st.subheader("市场概览")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总成交额(亿)", overview['总成交额(亿)'])
        col2.metric("涨跌比", overview['涨跌比'])
        col3.metric("平均涨跌幅", f"{overview['平均涨跌幅']}%")
        col4.metric("上涨占比",
                    f"{round(overview['上涨家数'] / (overview['上涨家数'] + overview['下跌家数']) * 100, 2)}%")

        # 显示市场涨跌分布
        st.subheader("市场涨跌分布")
        fig_dist = plot_distribution(distribution)
        st.plotly_chart(fig_dist, use_container_width=True)

        # 导出数据为Excel
        st.subheader("导出数据")
        if st.button("下载当天所有股票数据"):
            # 合并所有数据
            all_data = pd.concat([stock_zh_a_spot_df], axis=0)
            # 导出为Excel
            excel_file = "A股市场数据.xlsx"
            all_data.to_excel(excel_file, index=False)
            st.success("数据已导出为 Excel 文件。")

            # 提供下载链接
            with open(excel_file, "rb") as f:
                st.download_button("点击下载 Excel 文件", f, file_name=excel_file)

if __name__ == "__main__":
    app()

# 有同学微信问我， 怎么下载A股全量交易数据。  其实这个很简单，用akshare直接就可以搞定，或者直接抓取东方财富网公开数据就可以。
# 我记得自己当初学Python爬虫练手就用了这个，当时没直接用akshare。
# 另外说下， 历史某天的全量数据实现，虽然公开的免费API没有，既然市场5000多只股票都获取到了，那么每支股票code 很容易获取到了，那么我们可以开多个线程去获取 单只股票的某一时间段的数据并进行入库处理。 
# 这样查询某一天的全量数据不就有了。其实我前面介绍的开源项目Stock代码里就有实现。 感兴趣可以翻一翻。