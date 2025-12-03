import akshare as ak
import pandas as pd

# 获取当日A股市场现货数据（包含涨跌幅字段）
stock_zh_a_spot_df = ak.stock_zh_a_spot_em()

# 通常情况下，某些API返回的涨跌幅会以百分比形式表示，我们这里假设字段名称为'涨跌幅'，该字段已是百分比形式
# 如果是小数形式，则需要将其乘以100

# 定义涨跌幅区间
bins = [-100, -10, -3, 0, 3, 10, 100]
labels = ['跌幅10%以上', '跌幅3%-10%', '跌幅0%-3%', '涨幅3%以内', '涨3%-10%之间', '涨幅10%以上']

# 对股票涨跌幅进行分类
stock_zh_a_spot_df['category'] = pd.cut(stock_zh_a_spot_df['涨跌幅'], bins=bins, labels=labels)

# 对分类进行汇总统计
category_count = stock_zh_a_spot_df['category'].value_counts().sort_index()

# 打印统计结果
print(category_count)