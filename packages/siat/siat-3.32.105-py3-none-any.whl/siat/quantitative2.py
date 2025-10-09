# -*- coding: utf-8 -*-
"""
本模块功能：量化分析之证券价格高低趋势
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年9月16日
最新修订日期：2025年9月17日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.security_trend2 import *

#==============================================================================
import pandas as pd
import numpy as np

#==============================================================================
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300

plt.rcParams['figure.facecolor']='white' #背景颜色

plt.rcParams['axes.grid']=False

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    #设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    
    """
    if check_language() == "English":
        #设置英文字体
        plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 设置默认字体
        mpfrc={'font.family': 'Times New Roman'}
    """
    
if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 

# 设置绘图风格字体大小
title_txt_size=16
ylabel_txt_size=12
xlabel_txt_size=12
legend_txt_size=12
annotate_size=11

if check_language() == "English":
    title_txt_size=20
    ylabel_txt_size=16
    xlabel_txt_size=16
    legend_txt_size=16
    annotate_size=13

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'
    
    ticker='513030.SS'
    
    start='MRY'; end='today'
    window=252; price_type='Close'; facecolor='whitesmoke'


def security_trend_highlow(ticker, start='MRY', end='today', \
                   window=21, price_type='Close', facecolor='white'):
    """
    功能：
        绘制证券价格曲线，辅之以最近windowge交易日内的最高最低收盘价曲线
        目的是评估当期价格是否已经接近区间内的最高或最低价
    
    参数：
        ticker：证券代码
        start：开始日期，默认'MRM'
        end：截至日期，默认'today'
        window：观察区间交易日天数，默认252个交易日（52周）
        price_type：证券价格类型，默认收盘价'Close', 可选前复权价'Adj Close'
        facecolor：背景颜色，默认灰白色'whitesmoke'
    """
    import matplotlib.dates as mdates
    
    # 延伸开始日期
    start,end=start_end_preprocess(start,end)    
    start1=date_adjust(start, adjust=-window *2)
    
    # 抓取证券价格
    prices,found=get_price_1ticker(ticker,start1,end)
    if not (found == 'Found'):
        print(f"  #Warning: either {ticker} not found or no data available")
        return None
    
    # 检查价格类型
    collist=['Open','High','Low','Close','Adj Close']
    if not (price_type in collist):
        print(f"  #Warning: unsupported price type {price_type}")
        print(f"  Supported price type: {collist}")
        return None
    
    price1=prices[[price_type]]
    
    # 计算 rolling high/low
    price1["High_Close"] = price1[price_type].rolling(window).max()
    price1["Low_Close"] = price1[price_type].rolling(window).min()
    
    # 截取区间数据
    df=price1[start:end]
    
    high_end=df["High_Close"].values[-1]
    low_end=df["Low_Close"].values[-1]
    close_end=df[price_type].values[-1]
    
    # 绘图
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 三条曲线（颜色 + 不同线型）
    ax.plot(df.index, df[price_type], color="black", linewidth=2.2, linestyle="-")       # 实线
    ax.plot(df.index, df["High_Close"], color="red", alpha=0.6, linewidth=1.2, linestyle="--")   # 虚线
    ax.plot(df.index, df["Low_Close"], color="blue", alpha=0.6, linewidth=1.2, linestyle="-.")   # 点划线
    
    # 填充区域：高-收盘（斜线 ///）
    ax.fill_between(
        df.index, df[price_type], df["High_Close"],
        where=(df["High_Close"] >= df[price_type]),
        color="red", alpha=0.1, hatch="///", edgecolor="red"
    )
    
    # 填充区域：低-收盘（点阵 ...）
    ax.fill_between(
        df.index, df[price_type], df["Low_Close"],
        where=(df["Low_Close"] <= df[price_type]),
        color="blue", alpha=0.1, hatch="...", edgecolor="blue"
    )
    
    # 在曲线末尾标注 + 箭头
    last_date = df.index[-1]
    
    ax.annotate(ectranslate(price_type)+f"({srounds(close_end)})", 
                xy=(last_date, df[price_type].iloc[-1]), 
                xytext=(25, 0), textcoords="offset points", 
                color="black", fontsize=annotate_size, fontweight="bold", va="center",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))
    
    ax.annotate(text_lang(f"{window}日最高点({srounds(high_end)})",f"{window} days highest({srounds(high_end)})"), 
                xy=(last_date, df["High_Close"].iloc[-1]), 
                xytext=(25, 12), textcoords="offset points",   # 往上偏移
                color="red", fontsize=annotate_size, va="bottom",
                arrowprops=dict(arrowstyle="->", color="red", lw=1, alpha=0.6))
    
    ax.annotate(text_lang(f"{window}日最低点({srounds(low_end)})",f"{window} days lowest({srounds(low_end)})"), 
                xy=(last_date, df["Low_Close"].iloc[-1]), 
                xytext=(25, -12), textcoords="offset points",  # 往下偏移
                color="blue", fontsize=annotate_size, va="top",
                arrowprops=dict(arrowstyle="->", color="blue", lw=1, alpha=0.6))
    
    # 横轴日期格式化为 "YYYY-MM"
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=30)
    
    tname=ticker_name(ticker)
    #titletxt_cn=f"证券价格高低点趋势分析：{ticker_name(ticker)}，近期{window}个(交易)日"
    titletxt_cn=f"价格高低点范围与趋势分析：{tname}"
    #titletxt_en=f"Security Price High-Low Trend: {ticker_name(ticker)}, Recent {window} (Trading) Days"
    titletxt_en=f"Price High-Low Range & Trend: {tname}"
    titletxt=text_lang(titletxt_cn,titletxt_en)
    plt.title('\n'+titletxt+'\n',fontweight='bold',fontsize=title_txt_size)
    
    import datetime; todaydt = datetime.date.today()
    sourcetxt=text_lang("注：基于交易日天数。数据来源：新浪/Stooq/雅虎","Note: based on trading days. Data source: Sina/Stooq/Yahoo")
    footnote=sourcetxt+', '+str(todaydt)
    plt.xlabel('\n'+footnote+'\n',fontsize=xlabel_txt_size,ha='center') #空一行，便于截图底行留白
    
    plt.gca().set_facecolor(facecolor)
    
    plt.tight_layout()
    plt.show()
    plt.close()
    
    return df
