import akshare as ak
import pandas as pd


def fetch_and_save_concept_stocks(name):
    """
    获取指定股票概念的成分股，并保存至Excel文件。

    :param name: 股票概念名称
    """
    # 获取所有股票概念及其成分股信息
    concept_stocks_df = ak.stock_board_concept_name_em()
    spath = f"./概念板块.xlsx"
    concept_stocks_df.to_excel(spath, index=False)

    # 检查指定概念是否存在
    if name not in concept_stocks_df['板块名称'].values:
        print(f"未找到板块名称'{name}'，请检查输入是否正确。")
        return

    # 筛选出指定概念的成分股
    df = ak.stock_board_concept_cons_em(name)

    # 保存至Excel文件
    spath = f"./{name}.xlsx"
    df.to_excel(spath, index=False)

    print(f"成功将股票概念'{name}'的成分股保存至'{spath}'。")


# 示例：获取并保存“低空经济”概念的成分股
fetch_and_save_concept_stocks("低空经济")