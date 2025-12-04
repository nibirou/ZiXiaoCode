# 1、获取股票基本信息
def get_stock_info(stock_code):
    """获取股票详细信息"""
    try:
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        return stock_info
    except Exception as e:
        st.error(f"获取股票信息时出错: {str(e)}")
        return None
    
# 2、画K线图
def get_stock_data(stock_code):
    """获取股票数据并绘制K线图"""
    try:
        # 获取3个月K线图
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

        # 使用akshare获取股票数据
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")

        # 创建K线图
        fig = go.Figure(data=[go.Candlestick(x=df['日期'],
                                             open=df['开盘'],
                                             high=df['最高'],
                                             low=df['最低'],
                                             close=df['收盘'],
                                             increasing_line_color = 'red',  # Red for positive changes
                                             decreasing_line_color = 'green'),  # Green for negative changes
        ])

        # 更新布局
        fig.update_layout(title=f'{stock_code} 股票K线图', xaxis_title='日期', yaxis_title='价格')

        return fig, df
    except Exception as e:
        st.error(f"获取股票数据时出错: {str(e)}")
        return None, None

# 3、获取新闻信息

def get_stock_news(stock_code):
    """获取股票相关新闻"""
    try:
        stock_news_em_df = ak.stock_news_em(symbol=stock_code)
        return stock_news_em_df.head(10)  # 返回最新的5条新闻
    except Exception as e:
        st.error(f"获取新闻数据时出错: {str(e)}")
        return None
    
# 4、AI大模型获取投资建议

def analyze_stock_trend(stock_code, df, stock_info, news_df):
    """使用LangChain和OpenAI模型分析股票走势并给出投资建议"""
    # 计算一些基本指标
    latest_price = df['收盘'].iloc[-1]
    price_change = df['收盘'].iloc[-1] - df['收盘'].iloc[0]
    price_change_percent = (price_change / df['收盘'].iloc[0]) * 100

    # 准备股票信息
    info_str = "\n".join([f"{row['item']}: {row['value']}" for _, row in stock_info.iterrows()])

    # 准备新闻信息
    news_str = "\n".join([f"- {row['新闻标题']}" for _, row in news_df.iterrows()])

    # 创建提示模板
    template = """
    分析以下股票数据并给出走势分析和投资建议：

    股票代码：{stock_code}
    最新收盘价：{latest_price}
    年度价格变化：{price_change} ({price_change_percent}%)
    最高价：{high_price}
    最低价：{low_price}
    平均成交量：{avg_volume}

    股票信息：
    {stock_info}

    相关新闻：
    {news}

    请提供以下信息：
    1. 总体趋势分析
    2. 可能的支撑位和阻力位
    3. 成交量分析
    4. 短期和长期预测
    5. 潜在风险和机会
    6. 基于技术分析和新闻的投资建议
    """

    prompt = PromptTemplate(
        input_variables=["stock_code", "latest_price", "price_change", "price_change_percent",
                         "high_price", "low_price", "avg_volume", "stock_info", "news"],
        template=template
    )

    # 创建LLM链
    llm =  ChatOpenAI(
        temperature=0.95,
        model="glm-4-flash",
        openai_api_key= "xxxxx",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    # 运行链
    result = chain.run({
        "stock_code": stock_code,
        "latest_price": f"{latest_price:.2f}",
        "price_change": f"{price_change:.2f}",
        "price_change_percent": f"{price_change_percent:.2f}",
        "high_price": f"{df['最高'].max():.2f}",
        "low_price": f"{df['最低'].min():.2f}",
        "avg_volume": f"{df['成交量'].mean():.2f}",
        "stock_info": info_str,
        "news": news_str
    })

    return result

# 基于上面的代码片段 ，懂点Python技术就可以做出上面的效果了。

# 我这里用的智谱AI大模型，可以通过我的链接进行注册