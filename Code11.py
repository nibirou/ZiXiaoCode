import akshare as ak
import backtrader as bt
import datetime
import pandas as pd

# 先说下本篇文章的初步思路：

# 1、使用Akshare获取指定股票的历史数据。

# 2、数据预处理，处理成Backtrader期望的格式

# 3、初始化Backtrader环境，设置初始资金、佣金比例，添加策略及分析器。

# 4、运行回测并输出结果，包括资金变化、回报率、夏普比率和最大回撤等。

class MA20Strategy(bt.Strategy):
    params = (
        ('ma_period', 20),
    )

    def __init__(self):
        self.ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.ma_period)
        self.crossover = bt.indicators.CrossOver(self.data.close, self.ma)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.ma[0]:
                self.buy()
        elif self.data.close[0] < self.ma[0]:
            self.sell()

def run_backtest(stock_code, start_date, end_date):
    # 使用akshare获取股票数据
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date)
    except Exception as e:
        print(f"获取股票数据时出错: {e}")
        return

    if df.empty:
        print("未获取到股票数据，请检查股票代码和日期范围。")
        return

    # 重命名列以匹配backtrader的要求
    df = df.rename(columns={
        '日期': 'date', '开盘': 'open', '收盘': 'close',
        '最高': 'high', '最低': 'low', '成交量': 'volume'
    })

    # 将日期列转换为datetime类型
    df['date'] = pd.to_datetime(df['date'])

    # 设置日期为索引
    df.set_index('date', inplace=True)

    # 创建backtrader的数据源
    data = bt.feeds.PandasData(dataname=df)

    # 初始化cerebro引擎
    cerebro = bt.Cerebro()

    # 添加数据
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 设置佣金
    cerebro.broker.setcommission(commission=0.0001)

    # 添加策略
    cerebro.addstrategy(MA20Strategy)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # 运行回测
    results = cerebro.run()

    # 打印结果
    strat = results[0]
    print(f"初始资金: {cerebro.broker.startingcash:.2f}")
    print(f"最终资金: {cerebro.broker.getvalue():.2f}")

    returns = strat.analyzers.returns.get_analysis()
    if 'rtot' in returns:
        print(f"总回报率: {returns['rtot']:.2%}")
    else:
        print("无法计算总回报率")

    sharpe = strat.analyzers.sharpe_ratio.get_analysis()
    if 'sharperatio' in sharpe and sharpe['sharperatio'] is not None:
        print(f"年化夏普比率: {sharpe['sharperatio']:.2f}")
    else:
        print("无法计算夏普比率，可能是由于数据不足或者没有交易发生")

    drawdown = strat.analyzers.drawdown.get_analysis()
    if 'max' in drawdown and 'drawdown' in drawdown['max']:
        print(f"最大回撤: {drawdown['max']['drawdown']:.2%}")
    else:
        print("无法计算最大回撤")

    # 绘制结果
    try:
        cerebro.plot()
    except Exception as e:
        print(f"绘图时出错: {e}")

if __name__ == "__main__":
    stock_code = "000001"
    start_date = "20230101"
    end_date = "20240920"

    run_backtest(stock_code, start_date, end_date)