# 1、计算5日线思路

# 很多券商软件的MA5价格是近5个交易日收盘的平均价， 其实对我来说，没什么鸟用。我需要的是强势股回踩5日线提醒，
# 我自己设计的公式思路，根据股票code获取最近4个交易日收盘价 +当日开盘价，除以5，计算5日线价格。

# def get_5day_average(stock_code):
#     try:
#         end_date = datetime.now().strftime('%Y%m%d')
#         start_date = (datetime.now() - pd.Timedelta(days=10)).strftime('%Y%m%d')
#         df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="")

#         if len(df) < 5:
#             return None, f"Error: Not enough data available for {stock_code}. Only {len(df)} days found."

#         latest_open = df.iloc[-1]['开盘']
#         previous_closes = df.iloc[-5:-1]['收盘'].tolist()

#         five_day_values = previous_closes + [latest_open]
#         five_day_average = sum(five_day_values) / 5

#         return five_day_average, None

#     except Exception as e:
#         return None, f"Error occurred for {stock_code}: {str(e)}"

# 2、交易时间判断，上午9点半-11点半， 下午1点-3点
# def is_trading_time():
#     now = datetime.now().time()
#     morning_start = time(9, 30)
#     morning_end = time(11, 30)
#     afternoon_start = time(13, 0)
#     afternoon_end = time(15, 0)
    
#     return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

# 3、利用akshare获取实时价格，  为了保证接口的正常顺利调用， 最好换个数据源。
# real_time_data = ak.stock_zh_a_spot()

# 4、钉钉通知报警

# 钉钉机器人配置
# DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN"

# 钉钉怎么玩，可以借助钉钉APP面对面建群，输入4个数字建一个单人群聊，  单人群里搞个 钉钉机器人就可以了。