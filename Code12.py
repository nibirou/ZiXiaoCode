
import akshare as ak
import pandas as pd
from datetime import datetime, time, date
import time as time_module
import requests
import schedule
import json

# 钉钉机器人配置
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN"

# 股票代码数组
STOCK_CODES = ["000001", "399001"]  # 上证指数、深证成指

# 用于跟踪每日报警状态的字典
daily_alerts = {}

def send_dingtalk_message(message):
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "text",
        "text": {"content": message}
    }
    response = requests.post(DINGTALK_WEBHOOK, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"Failed to send message to DingTalk: {response.text}")

def get_5day_average(stock_code):
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - pd.Timedelta(days=10)).strftime('%Y%m%d')
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="")

        if len(df) < 5:
            return None, f"Error: Not enough data available for {stock_code}. Only {len(df)} days found."

        latest_open = df.iloc[-1]['开盘']
        previous_closes = df.iloc[-5:-1]['收盘'].tolist()

        five_day_values = previous_closes + [latest_open]
        five_day_average = sum(five_day_values) / 5

        return five_day_average, None

    except Exception as e:
        return None, f"Error occurred for {stock_code}: {str(e)}"

def is_trading_time():
    now = datetime.now().time()
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

def reset_daily_alerts():
    global daily_alerts
    daily_alerts = {code: False for code in STOCK_CODES}

def check_stock_prices():
    global daily_alerts
    today = date.today()
    
    if today not in daily_alerts:
        reset_daily_alerts()

    if is_trading_time():
        try:
            # 获取所有股票的实时数据
            real_time_data = ak.stock_zh_a_spot()

            for stock_code in STOCK_CODES:
                if daily_alerts[stock_code]:
                    continue  # 如果今天已经报警过，跳过这只股票

                # 获取5日均线
                five_day_average, error = get_5day_average(stock_code)
                if error:
                    print(error)
                    continue

                # 获取实时价格
                stock_data = real_time_data[real_time_data['代码'] == stock_code]
                
                if stock_data.empty:
                    print(f"No real-time data found for stock {stock_code}")
                    continue

                current_price = stock_data.iloc[0]['最新价']
                stock_name = stock_data.iloc[0]['名称']

                # 比较实时价格与5日均线
                if current_price < five_day_average and not daily_alerts[stock_code]:
                    message = f"警报：{stock_name}（{stock_code}）当前价格 {current_price:.2f} 低于5日均线 {five_day_average:.2f}"
                    print(message)
                    send_dingtalk_message(message)
                    daily_alerts[stock_code] = True
                else:
                    print(f"{stock_name}（{stock_code}）当前价格 {current_price:.2f}，5日均线 {five_day_average:.2f}")

        except Exception as e:
            print(f"Error checking stock prices: {str(e)}")
    else:
        print("当前不在交易时间，跳过检查")

def is_weekday():
    return datetime.now().weekday() < 5

def main():
    # 初始化每日报警状态
    reset_daily_alerts()

    # 设置每分钟执行一次检查，但只在工作日的指定时间段内运行
    schedule.every(1).minutes.do(check_stock_prices).tag('monitoring')

    # 设置每天零点重置报警状态
    schedule.every().day.at("00:00").do(reset_daily_alerts).tag('reset')

    print(f"开始监控股票 {', '.join(STOCK_CODES)}，将在交易时间内每分钟检查一次...")
    
    while True:
        if is_weekday():
            schedule.run_pending()
        else:
            print("今天是周末，不执行监控")
            # 清除所有预定的任务，确保下一个工作日重新开始
            schedule.clear('monitoring')
            # 重新设置任务
            schedule.every(1).minutes.do(check_stock_prices).tag('monitoring')
            # 等待到下一个工作日
            time_module.sleep(24 * 60 * 60)  # 睡眠24小时
        time_module.sleep(1)

if __name__ == "__main__":
    main()