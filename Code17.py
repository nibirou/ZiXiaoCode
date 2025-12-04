# 昨天的文章 介绍了 通过AI大模型询问 相关概念股， AI大模型基本是依赖网络被普及的内容， 不一定靠谱。 

# 怎么理解这句话呢？  经过网络的发酵，很多人发了XXX是某某概念股， AI大模型理解 这只股就是了。

# 备注：上次我搜索一段股票相关技术代码，然后推荐出来一篇文章， 我看着怎么有点眼熟呢，这不是我之前写的么， 
# 然后就原封不动出现在别人的自建博客上。一看就是通过网络爬虫抓取的，离了个大谱。

# 我们做技术需要实事求是， 那怎么抓取原始数据呢。  这里我们采用技术的手段，还是借助Python的 akshare库来完成。

# 以20241025智谱发布AutoGLM为例，  那我以智谱为关键字， 就搜索当天的公告，看一下哪家公司实锤了不就好了。

# 下面给出简单的代码示例：


import pandas as pd

# Setting up pandas display options
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_colwidth', 100)


def search_keyword(df, keyword):
    # Search for the keyword in the 'title' column
    matched_rows = df[df['公告标题'].str.contains(keyword, case=False)]
    return matched_rows


# Main execution
date = "20241025"
try:
    # Try to import akshare, if available
    import akshare as ak
    df = ak.stock_notice_report(symbol="全部", date=date)
except ImportError:
    print("akshare not available")


# Save to Excel
spath = f"./{date}公告.xlsx"
df.to_excel(spath, engine='xlsxwriter', index=False)
print(f"Data saved to {spath}")

# Search for a keyword
keyword = "智谱"
result = search_keyword(df, keyword)

print(f"\nRows containing the keyword '{keyword}':")
print(result[['代码','名称','公告标题','网址']])

# 最近重组题材比较火热，我们是不是可以利用重组去筛选实锤的公司，
# 比如我们把这段时间的公告爬下来，通过技术手段匹配对应某些关键字。  不然你看到的都是别人科普的二手消息了。

