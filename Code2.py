
import akshare as ak
import xlsxwriter
# 获取2024业绩预告
df = ak.stock_yjyg_em("202403")
spath = r"./2024一季度业绩预告.xlsx"
#print(df)
df.to_excel(spath, engine='xlsxwriter')