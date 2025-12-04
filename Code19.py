# 前阵子自己利用streamlit构建了不少股票简单例子，比如涨停分析，比如个股分析等。 

# 昨天晚上，我临时有个想法， 每个例子太过孤立了。要不把这些例子结合在一个应用中。

# 先简单上图，大体的想法, 让AI帮我写的。

# 为什么有这个想法呢， 主要是我之前一些代码逻辑已经有了，准备复用， 也可以让每个例子保持页面的独立性 和可扩展性。

# 对于streamlit用过的同学，这个其实很简单。这里就抛砖引玉下

# 简单代码如下：

# main.py  入口页

import streamlit as st
import home
import zhangting
import jingjia
import gegu
import junxian

st.set_page_config(page_title="股票分析应用")

PAGES = {
    "主页": home,
    "涨停分析": zhangting,
    "竞价分析": jingjia,
    "均线分析": junxian,
    "个股分析": gegu,
}

def main():
    st.sidebar.title("股票分析导航")
    selection = st.sidebar.radio("跳转到", list(PAGES.keys()))

    page = PAGES[selection]
    page.app()

if __name__ == "__main__":
    main()

# home.py    主页

import streamlit as st

def app():
    st.title("欢迎来到股票分析应用")
    st.write("使用左侧的导航菜单来浏览不同的页面。")

# 这种结构的工作原理如下：

# 1. `main.py` 是应用的入口点。它导入所有页面模块并处理导航。

# 2. 每个页面都有自己的 Python 文件（`home.py`, `page1.py`, `page2.py`），包含一个 `app()` 函数来定义该页面的内容。

# 3. 在 `main.py` 中，我们创建了一个 `PAGES` 字典，将页面名称映射到相应的模块。

# 4. 使用 `st.sidebar.radio` 创建导航菜单，允许用户选择页面。

# 5. 根据用户的选择，调用相应页面模块的 `app()` 函数来显示内容。

# 要运行这个应用，您只需要执行 `main.py`：

# streamlit run main.py

# 这种方法的优点是：

# - 每个页面都有自己的文件，使得代码更加模块化和易于维护。

# - 可以轻松地添加新页面或修改现有页面，而不会影响其他部分。

# - 主文件 `main.py` 保持简洁，主要负责导航和页面切换逻辑。

# 如果您想添加新的页面，只需创建一个新的 Python 文件
# （例如 `page3.py`），定义 `app()` 函数，然后在 `main.py` 中导入它并将其添加到 `PAGES` 字典中。