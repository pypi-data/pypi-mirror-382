# -*- coding: utf-8 -*-
"""
本模块功能：期权希腊值风险趋势演示
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年9月13日
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

#==============================================================================
import numpy as np
from scipy.stats import norm

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
    
    if check_language() == "English":
        #设置英文字体
        plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 设置默认字体
        mpfrc={'font.family': 'Times New Roman'}
        
if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 

#==============================================================================
#==============================================================================

if __name__ =="__main__":
    S_range = np.linspace(50, 150, 100)
    # Parameters
    K = 100
    T = 0.5  # in years
    r = 0.01
    sigma = 0.2

# Black-Scholes formulas for Greeks and option prices
def black_scholes_greeks(S, K, T, r, sigma, option_type):
    from scipy.stats import norm
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 365
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 100

    return price, delta, gamma, theta, vega, rho

# Plotting function
def plot_dual_axis(x, y1, y2, y1_label, y2_label, title, K, \
                   notes='', option_direction='call', \
                   loc1='auto', loc2='auto'):
    """
    功能：绘制标的资产价格变化对期权价格和各种希腊值的影响
    参数：
    x：标的资产价格数组，例如np.linspace(50, 150, 100)，numpy数组ndarray类型
    y1：期权价格列表
    y2：希腊值列表
    y1_label：期权价格的标签
    y2_label：希腊值的标签
    title：绘图标题
    K：期权的行权价
    loc1：期权价格标签图例的位置
    loc2：希腊值标签图例的位置
    
    """
    print('') #空一行
    
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(x, y1, 'b-', label=y1_label)
    
    xlabeltxt=text_lang('标的资产价格','Underlying Price')
    if notes != '':
        xlabeltxt=xlabeltxt + '\n\n' + str(notes)
    ax1.set_xlabel(xlabeltxt)
    
    ax1.set_ylabel(y1_label, color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    ax2 = ax1.twinx()
    ax2.plot(x, y2, 'r--', label=y2_label)
    ax2.set_ylabel(y2_label, color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Annotate ITM, ATM, OTM
    ax1.axvline(K, color='gray', linestyle='--')
    
    if option_direction == 'call':
        """
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x < K), hatch='/', \
                         color='green', alpha=0.1, \
                             label=text_lang('实值区间(看跌期权)/虚值区间(看涨期权)','ITM (Put) / OTM (Call)'))
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x > K), hatch='.', \
                         color='blue', alpha=0.1, \
                             label=text_lang('实值区间(看涨期权)/虚值区间(看跌期权)','ITM (Call) / OTM (Put)'))
        """
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x < K), hatch='/', \
                         color='green', alpha=0.1, \
                             label=text_lang('虚值区间','OTM Zone'))
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x > K), hatch='.', \
                         color='blue', alpha=0.1, \
                             label=text_lang('实值区间','ITM Zone'))
    else: # put
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x < K), hatch='/', \
                         color='green', alpha=0.1, \
                             label=text_lang('实值区间','ITM Zone'))
        ax1.fill_between(x, ax1.get_ylim()[0], ax1.get_ylim()[1], where=(x > K), hatch='.', \
                         color='blue', alpha=0.1, \
                             label=text_lang('虚值区间','OTM Zone'))
        
        
    #ax1.text(K, ax1.get_ylim()[1]*0.95, text_lang('平值','ATM'), horizontalalignment='center', color='black')
    ax1.text(K, ax1.get_ylim()[0]*0.95, text_lang('平值','ATM'), horizontalalignment='center', color='black')

    #fig.suptitle(title, fontsize=14)
    plt.title(title+'\n', fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    
    ax1.legend(loc=loc1)
    ax2.legend(loc=loc2)
    
    plt.show(fig)
    plt.close(fig)
    

def greek_trend(K=100, T=1, r=0.05, sigma=0.2, \
                indicator='Delta',direction='call', \
                S_range='auto', \
                loc1='auto', loc2='auto'):
    """
    功能：绘制标的资产价格变化对于期权价格和各种希腊值的影响
    参数：
    K：期权行权价
    T：到期年数
    r：无风险利率
    sigma：标的资产波动率
    indicator：希腊风险指标，默认'Delta', 可选'Delta'、'Gamma'、'Theta'、'Vega'、'Rho'
    direction：期权方向，默认'call', 可选'call'、'put'、'both'
    S_range：标的资产价格数组，形式为np.linespace(起点值, 终点值, 个数)，numpy数组，默认'auto'
    
    """
    indicator=indicator.title()
    direction=direction.lower()
    if S_range == 'auto':
        S_range = np.linspace(50, 150, 100)
    
    # Generate data and plots
    if direction in ['call','both']:
        call_data = [black_scholes_greeks(S, K, T, r, sigma, 'call') for S in S_range]
        call_price, call_delta, call_gamma, call_theta, call_vega, call_rho = zip(*call_data)
    if direction in ['put','both']:
        put_data = [black_scholes_greeks(S, K, T, r, sigma, 'put') for S in S_range]
        put_price, put_delta, put_gamma, put_theta, put_vega, put_rho = zip(*put_data)
    
    # 脚注
    notes_en=f"Notes: strike price {K}, year(s) to maturity {T}, RF {r:.2%}, volatility {sigma}"
    notes_cn=f"注：行权价{K}, 到期年数{T}, 无风险利率{r:.2%}, 标的资产波动率{sigma}"
    notes=text_lang(notes_cn, notes_en)
    
    # 看涨期权
    if direction in ['call','both']:
        y1label=text_lang('看涨期权价格','Call Price')
        
        if indicator == 'Delta':
            #确定图例的最佳位置
            if loc1 == 'auto': locA='center left'
            if loc2 == 'auto': locB='center right'
            
            titletxt=text_lang('看涨期权：价格变化与Delta走势','Call Option: Price vs Delta')
            plot_dual_axis(S_range, call_price, call_delta, y1label, 'Delta', \
                           titletxt, K, notes, 'call', locA, locB)
        
        if indicator == 'Gamma':
            if loc1 == 'auto': locA='upper left'
            if loc2 == 'auto': locB='center right'
            
            titletxt=text_lang('看涨期权：价格变化与Gamma走势','Call Option: Price vs Gamma')
            plot_dual_axis(S_range, call_price, call_gamma, y1label, 'Gamma', \
                           titletxt, K, notes, 'call', locA, locB)
        
        if indicator == 'Theta':
            if loc1 == 'auto': locA='center'
            if loc2 == 'auto': locB='center right'
            
            titletxt=text_lang('看涨期权：价格变化与Theta走势','Call Option: Price vs Theta')
            plot_dual_axis(S_range, call_price, call_theta, y1label, 'Theta', \
                           titletxt, K, notes, 'call', locA, locB)
        
        if indicator == 'Vega':
            if loc1 == 'auto': locA='upper left'
            if loc2 == 'auto': locB='center'
            
            titletxt=text_lang('看涨期权：价格变化与Vega走势','Call Option: Price vs Vega')
            plot_dual_axis(S_range, call_price, call_vega, y1label, 'Vega', \
                           titletxt, K, notes, 'call', locA, locB)
        
        if indicator == 'Rho':
            if loc1 == 'auto': locA='center left'
            if loc2 == 'auto': locB='center right'
            
            titletxt=text_lang('看涨期权：价格变化与Rho走势','Call Option: Price vs Rho')
            plot_dual_axis(S_range, call_price, call_rho, y1label, 'Rho', \
                           titletxt, K, notes, 'call', locA, locB)


    # 看跌期权
    if direction in ['put','both']:
        y1label=text_lang('看跌期权价格','Put Price')
        
        if indicator == 'Delta':
            if loc1 == 'auto': locA='center right'
            if loc2 == 'auto': locB='upper right'
            
            titletxt=text_lang('看跌期权：价格变化与Delta走势','Put Option: Price vs Delta')
            plot_dual_axis(S_range, put_price, put_delta, y1label, 'Delta', \
                           titletxt, K, notes, 'put', locA, locB)
        
        if indicator == 'Gamma':
            if loc1 == 'auto': locA='center right'
            if loc2 == 'auto': locB='center'
            
            titletxt=text_lang('看跌期权：价格变化与Gamma走势','Put Option: Price vs Gamma')
            plot_dual_axis(S_range, put_price, put_gamma, y1label, 'Gamma', \
                           titletxt, K, notes, 'put', locA, locB)
        
        if indicator == 'Theta':
            if loc1 == 'auto': locA='center right'
            if loc2 == 'auto': locB='center'
            
            titletxt=text_lang('看跌期权：价格变化与Theta走势','Put Option: Price vs Theta')
            plot_dual_axis(S_range, put_price, put_theta, y1label, 'Theta', \
                           titletxt, K, notes, 'put', locA, locB)
        
        if indicator == 'Vega':
            if loc1 == 'auto': locA='upper right'
            if loc2 == 'auto': locB='center'
            
            titletxt=text_lang('看跌期权：价格变化与Vega走势','Put Option: Price vs Vega')
            plot_dual_axis(S_range, put_price, put_vega, y1label, 'Vega', \
                           titletxt, K, notes, 'put', locA, locB)
        
        if indicator == 'Rho':
            if loc1 == 'auto': locA='lower left'
            if loc2 == 'auto': locB='center right'
            
            titletxt=text_lang('看跌期权：价格变化与Rho走势','Put Option: Price vs Rho')
            plot_dual_axis(S_range, put_price, put_rho, y1label, 'Rho', \
                           titletxt, K, notes, 'put', locA, locB)

    return
