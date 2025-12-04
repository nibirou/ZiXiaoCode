
import pywencai
import xlsxwriter
import pandas as pd

# 本文具体讲下怎么通过代码 来详细分析，先讲下思路。

# 1、从问财接口获取符合特定条件的涨停股票数据，并按成交金额降序排列，将数据写入Excel文件，
# 选择想要的指定列并根据连续涨停天数降序排序。这一步也是上一篇文章的主要内容。

# 2、从涨停原因类别中通过+分隔符分析涨停原因类别，统计各概念出现次数。计算每只股票的主要涨停原因及其出现次数。

# 3、最后根据主要涨停原因出现次数、涨停原因、连续涨停天数再次排序，并重新输出至Excel文件。


# 列名与数据对其显示
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

pd.set_option('display.max_rows', None)  # 设置显示无限制行
pd.set_option('display.max_columns', None)  # 设置显示无限制列

pd.set_option('display.expand_frame_repr', False) #设置不折叠数据
pd.set_option('display.max_colwidth', 100)


date ="20240823"
param = "{date}涨停，非涉嫌信息披露违规且非立案调查且非ST，非科创板，非北交所"
df = pywencai.get(query= param ,sort_key='成交金额', sort_order='desc')


spath = f"./{date}涨停wencai.xlsx"
#print(df)
df.to_excel(spath, engine='xlsxwriter')

selected_columns = ['股票代码', '股票简称', '最新价','最新涨跌幅', '首次涨停时间['+date + ']', '连续涨停天数['+date + ']','涨停原因类别['+date + ']','a股市值(不含限售股)['+date + ']','涨停类型['+date + ']']
jj_df = df[selected_columns]
#print(jj_df)

# # 按照'连板数'列进行降序排序
sorted_temp_df = jj_df.sort_values(by='连续涨停天数['+date + ']', ascending=False)
# 输出排序后的DataFrame
#print(sorted_temp_df)
#sorted_temp_df_path = f"./{date}涨停排序wencai.xlsx"
#sorted_temp_df.to_excel(sorted_temp_df_path, engine='xlsxwriter')


# 按照 '+' 分割涨停原因类别
concepts = sorted_temp_df['涨停原因类别['+date+']'].str.split('+').explode().reset_index(drop=True)

# 统计每个概念的出现次数
concept_counts = concepts.value_counts().reset_index()
concept_counts.columns = ['概念', '出现次数']

# 输出结果
print(concept_counts)

# 获取每个股票的主要涨停原因
sorted_temp_df['涨停主要原因'] = sorted_temp_df['涨停原因类别['+date+']'].apply(
    lambda x: concept_counts.loc[concept_counts['概念'].isin(x.split('+'))]['概念'].iloc[0]
    if len(x.split('+')) > 0 else None
)
sorted_temp_df['涨停主要原因出现次数'] = sorted_temp_df['涨停主要原因'].map(concept_counts.set_index('概念')['出现次数'])

# 根据涨停主要原因出现次数和连续涨停天数排序
sorted_final_df = sorted_temp_df.sort_values(by=['涨停主要原因出现次数','涨停主要原因', '连续涨停天数['+date + ']'], ascending=[False, True, False])


# 输出结果
print(sorted_final_df)
sorted_final_df_path = f"./{date}涨停排序wencai.xlsx"
sorted_final_df.to_excel(sorted_final_df_path, engine='xlsxwri