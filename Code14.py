# 今天有读者私信我，他说看到我写的问财涨停分析有所启发，能否分析下上一个交易日 和 最近交易日 的涨停变化，以及概念板块变化。他遇到一个问题，怎么获取上一个交易日，毕竟前一天可能是周末或节假日。

# 可能他之前没用过tushare，这里简单分享下 tushare的 trade_cal交易日历接口。

# tushare官网：https://tushare.pro/

# 1、接口：trade_cal，可以通过数据工具调试和查看数据。
# 描述：获取各大交易所交易日历数据,默认提取的是上交所
# 积分：需2000积分
import tushare as ts
import datetime
# 接口实例
pro = ts.pro_api()
df = pro.trade_cal(exchange='', start_date='20180101', end_date='20181231')

# 既然有这个接口了， 我们传递一个足够长的时间（比如10天， 我们A股的休假传统最长也不过8天吧）， 开始时间传递  今天-10天，  
# 结束时间传递今天。那么 我们根据接口倒序获取数据，最近的交易日 是不是第1天获取1的数据，  
# 上一个交易日不是第二天获取1的数据， 毕竟为0代表A股休息不上班。

# 这里简单提供下代码， 获取最近交易日

# Initialize Tushare with your token
ts.set_token('YOUR_TUSHARE_TOKEN')
pro = ts.pro_api()

def get_latest_trading_day():
    today = datetime.now().date()
    
    # Get the trading calendar for the past week
    cal_df = pro.trade_cal(exchange='', start_date=(today - timedelta(days=10)).strftime('%Y%m%d'), end_date=today.strftime('%Y%m%d'))
    
    # Filter for open trading days and sort in descending order
    open_days = cal_df[cal_df['is_open'] == 1]['cal_date'].sort_values(ascending=False)
    
    # Return the most recent trading day
    return open_days.iloc[0]

# 上一个交易日我单独抽象了下， 毕竟有些场景用得上

def get_previous_trading_day(date):
    # Get the trading calendar for the past week before the given date
    end_date = datetime.strptime(date, '%Y%m%d').date()
    start_date = end_date - timedelta(days=7)
    
    cal_df = pro.trade_cal(exchange='', start_date=start_date.strftime('%Y%m%d'), end_date=date)
    
    # Filter for open trading days and sort in descending order
    open_days = cal_df[cal_df['is_open'] == 1]['cal_date'].sort_values(ascending=False)
    
    # Return the previous trading day
    return open_days.iloc[1]  # iloc[1] because iloc[0] would be the input date itself

# 后续找个时间写一篇 分析  上一个交易日 和 最近交易日 的涨停变化，以及概念板块变化。短线研究还是需要了解这些的。