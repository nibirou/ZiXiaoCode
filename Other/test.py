import akshare as ak


df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20241015",
    end_date="20241016",
    adjust="qfq"
)
print(df)