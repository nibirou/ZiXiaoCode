

import pywencai
import xlsxwriter
import pandas as pd

# 最近A股市场不好，今天又是3000多只待涨， 市场一片哀鸿遍野。
# 打开同花顺问财看了一眼，顿时索然无味。 原本没什么灵感， 
# 突然有了写作思路，要不把wencai数据简单抓取分析下。
# 之前写过一篇 【Python技术】使用akshare、pandas高效复盘每日涨停板行业分析   ， 
# 之前用的akshare， 这里换个数据源。
# 先说实现思路：  
# 1、先用pywencai包抓取数据， 我这个人偷懒，就直接用开源的项目来做。
# 项目地址： https://github.com/zsrl/pywencai
# a、环境依赖由于程序中执行了js代码，
# 请先保证已安装了Node.js，需要版本v16+。未安装请自行安装。
# 我电脑中之前已经安装过Node，这步直接忽略。
# b、安装pip install pywencai
# 2、开始写代码抓取并pandas分析下面是简单demo。 今天2024年8月21日，
# 我为了方便查看之前某一天的涨停数据，特意设置了一个变量。

# 其中代码里的param，可以改成你自己想定义的策略。
# 我由于个人原因，把ST、科创板、以及有明面上风险的排除了。
# 上面的代码用之前文章快速改的， 5分钟搞定。写得比较粗糙。

# 列名与数据对其显示
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

pd.set_option('display.max_rows', None)  # 设置显示无限制行
pd.set_option('display.max_columns', None)  # 设置显示无限制列

pd.set_option('display.expand_frame_repr', False) #设置不折叠数据
pd.set_option('display.max_colwidth', 100)


date ="20240821"
param = "{date}涨停，非涉嫌信息披露违规且非立案调查且非ST，非科创板，非北交所"
df = pywencai.get(query= param ,sort_key='成交金额', sort_order='desc')


spath = f"./{date}涨停wencai.xlsx"
#print(df)
df.to_excel(spath, engine='xlsxwriter')

selected_columns = ['股票代码', '股票简称', '最新价','最新涨跌幅', '首次涨停时间['+date + ']', '连续涨停天数['+date + ']','涨停原因类别['+date + ']','a股市值(不含限售股)['+date + ']','涨停类型['+date + ']']
jj_df = df[selected_columns]
#print(jj_df)
#
# # 按照'连板数'列进行降序排序
sorted_temp_df = jj_df.sort_values(by='连续涨停天数['+date + ']', ascending=False)
# 输出排序后的DataFrame
print(sorted_temp_df)
sorted_temp_df_path = f"./{date}涨停排序wencai.xlsx"
sorted_temp_df.to_excel(sorted_temp_df_path, engine='xlsxwriter')