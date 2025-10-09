# -*- coding: utf-8 -*-
"""
本模块功能：期权希腊值风险对比演示
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年9月1日
最新修订日期：2025年9月15日
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

# Black-Scholes formula and Greeks for European Call Option
def black_scholes_call(S, K, T, r, sigma):
    """
    功能：基于BS模型计算欧式看涨期权的希腊值（无红利情形）
    S：标的资产的当前价格（Spot Price）
        指的是期权对应的基础资产（如股票、期货等）在当前市场的价格
    K：期权的行权价格（Strike Price）
        指的是期权合约中规定的、在到期日可以买入（对于看涨期权）或卖出（对于看跌期权）标的资产的固定价格
    T：期权的到期时间（Time to Maturity）
        以年为单位表示的、从当前时刻到期权合约到期日的剩余时间
        例如，还有 3 个月到期的期权，T 值为 0.25（3/12）
    r：无风险利率（Risk-Free Interest Rate）
        以年化收益率表示的、无风险资产的收益率（通常使用国债收益率作为近似）
        注意这里使用的是连续复利的利率
    sigma：标的资产的波动率（Volatility）
        表示标的资产价格的年化波动率，衡量资产价格变动的不确定性（默认为隐含波动率）
        通常用标的资产收益率的标准差来表示，是 Black-Scholes 模型中非常关键的参数

    返回值：期权的希腊值
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    # 年数变化的影响：不除以365，否则为日数变化的影响
    #theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    
    return call_price, delta, gamma, theta, vega, rho


# Black-Scholes formula and Greeks for European put option
def black_scholes_put(S, K, T, r, sigma):
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    delta = norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    #theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    theta = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    
    return put_price, delta, gamma, theta, vega, rho

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    S_range = np.linspace(50, 150, 100) #从50到150分100份
    for S in S_range: print(S)
    
    # Fixed parameters
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2
    
    loc1="upper left"; loc2="lower right"
    
    
def greek_call_PriceNDeltaVsUnderlyingPrice(S_range, \
                                            K=100, T=1, r=0.05, sigma=0.2, \
                                            loc1="upper left",loc2="lower right"):
    """
    功能：其他条件不变时，标的资产价格变化-->看涨期权价格和Delta的影响
    S_range：标的资产价格变化范围，建议从小于行权价逐渐增加到大于行权价
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    
    price, delta, _, _, _, _ = zip(*[black_scholes_call(S, K, T, r, sigma) for S in S_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(S_range, price, 'b-', label=text_lang('看涨期权价格','Call Option Price'))
    ax2.plot(S_range, delta, 'r--', label='Delta')
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    
    ax1.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    #ax1.axvline(K, color='gray', linestyle=':',label=text_lang("行权价","Strike Price"))
    ax1.axvline(K, color='gray', linestyle=':')
    ax2.set_ylabel('Delta', color='r')
    
    titletxt_en='Option Price & Delta vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权价格和Delta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()    
    
    
    
def greek_put_PriceNDeltaVsUnderlyingPrice(S_range, \
                                            K=100, T=1, r=0.05, sigma=0.2, \
                                            loc1="center left",loc2="center right"):
    """
    功能：其他条件不变时，标的资产价格变化-->看跌期权价格和Delta的影响
    S_range：标的资产价格变化范围，建议从0.5K到1.5K，分成100份
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    
    price, delta, _, _, _, _ = zip(*[black_scholes_put(S, K, T, r, sigma) for S in S_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(S_range, price, 'b-', label=text_lang('看跌期权价格','Put Option Price'))
    ax2.plot(S_range, delta, 'r--', label='Delta')
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    
    ax1.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    #ax1.axvline(K, color='gray', linestyle=':',label=text_lang("行权价","Strike Price"))
    ax1.axvline(K, color='gray', linestyle=':')
    ax2.set_ylabel('Delta', color='r')
    
    titletxt_en='Option Price & Delta vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权价格和Delta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()    
    
    
# 看涨看跌二图合体    
def greek_PriceNDeltaVsUnderlyingPrice(S_range, \
                                       K=100, T=1, r=0.05, sigma=0.2, \
                                       loc1="upper left"):
    """
    功能：其他条件不变时，标的资产价格变化-->看涨和看跌期权Delta的影响，不绘制期权价格
    S_range：标的资产价格变化范围，建议从0.5K到1.5K，分成100份
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    _, delta_call, _, _, _, _ = zip(*[black_scholes_call(S, K, T, r, sigma) for S in S_range])
    _, delta_put, _, _, _, _ = zip(*[black_scholes_put(S, K, T, r, sigma) for S in S_range])
    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(S_range, delta_call, 'r-', label=text_lang('看涨期权Delta','Call Delta'))
    ax.plot(S_range, delta_put, 'b--', label=text_lang('看跌期权Delta','Put Delta'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    ax.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))

    ax.axvline(K, color='gray', linestyle=':')
    ax.axhline(0, color='gray', linestyle=':')
    
    ax.set_ylabel('Delta', color='k')
    
    titletxt_en='Option Delta vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权Delta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax.legend(loc=loc1)
    
    plt.show()
    plt.close()    
    
#==============================================================================
#==============================================================================
    
def greek_call_PriceNGammaVsUnderlyingPrice(S_range, \
                                            K=100, T=1, r=0.05, sigma=0.2, \
                                            loc1="center left",loc2="center right"):
    """
    功能：其他条件不变时，标的资产价格变化-->看涨期权价格和Gamma的影响
    S_range：标的资产价格变化范围，建议从小于行权价逐渐增加到大于行权价
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    
    price, _, gamma, _, _, _ = zip(*[black_scholes_call(S, K, T, r, sigma) for S in S_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(S_range, price, 'b-', label=text_lang('看涨期权价格','Call Option Price'))
    ax2.plot(S_range, gamma, 'g--', label='Gamma')
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    
    ax1.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    #ax1.axvline(K, color='gray', linestyle=':',label=text_lang("行权价","Strike Price"))
    ax1.axvline(K, color='gray', linestyle=':')
    ax2.set_ylabel('Gamma', color='g')
    
    titletxt_en='Option Price & Gamma vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权价格和Gamma的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()  

    
def greek_put_PriceNGammaVsUnderlyingPrice(S_range, \
                                            K=100, T=1, r=0.05, sigma=0.2, \
                                            loc1="center left",loc2="center right"):
    """
    功能：其他条件不变时，标的资产价格变化-->看跌期权价格和Gamma的影响
    S_range：标的资产价格变化范围，建议从0.5K到1.5K，分成100份
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    
    price, _, gamma, _, _, _ = zip(*[black_scholes_put(S, K, T, r, sigma) for S in S_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(S_range, price, 'b-', label=text_lang('看跌期权价格','Put Option Price'))
    ax2.plot(S_range, gamma, 'g--', label='Gamma')
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    
    ax1.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    #ax1.axvline(K, color='gray', linestyle=':',label=text_lang("行权价","Strike Price"))
    ax1.axvline(K, color='gray', linestyle=':')
    ax2.set_ylabel('Gamma', color='g')
    
    titletxt_en='Option Price & Gamma vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权价格和Gamma的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()  


# 看涨看跌二图合体     
def greek_PriceNGammaVsUnderlyingPrice(S_range, \
                                       K=100, T=1, r=0.05, sigma=0.2, \
                                       loc1="upper left"):
    """
    功能：其他条件不变时，标的资产价格变化-->看涨看跌期权Gamma的影响，不绘制期权价格
    S_range：标的资产价格变化范围，建议从0.5K到1.5K，分成100份
    其他条件不变：行权价K，到期年数T，无风险利率r，标的资产波动率sigma
    """
    _, _, gamma_call, _, _, _ = zip(*[black_scholes_call(S, K, T, r, sigma) for S in S_range])
    _, _, gamma_put, _, _, _ = zip(*[black_scholes_put(S, K, T, r, sigma) for S in S_range])
    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(S_range, gamma_call, 'r-', label=text_lang('看涨期权Gamma','Call Gamma'))
    ax.plot(S_range, gamma_put, 'b--', label=text_lang('看跌期权Gamma','Put Gamma'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权，行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"
    ax.set_xlabel(text_lang('标的资产价格','Underlying Price')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax.axvline(K, color='gray', linestyle=':')
    
    ax.set_ylabel('Gamma', color='k')
    
    titletxt_en='Option Gamma vs Underlying Price\n'
    titletxt_cn='标的资产价格对期权Gamma的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    ax.legend(loc=loc1)
    
    plt.show()
    plt.close()  

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    T_range = np.linspace(0.01, 2, 100) #分100份
    for T in T_range: print(T)
    
    # Fixed parameters
    S0 = 100
    S0=80
    S0=120
    
    K = 100
    r = 0.05
    sigma = 0.2
    
    loc1="auto"; loc2="auto"

def greek_call_PriceNThetaVsTimeToMaturity(T_range, \
                                           S0=100, K=100, r=0.05,sigma=0.2, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，到期年数变化-->看涨期权价格和Theta
    注意：这里的Theta是年数变化的影响
    
    到期年数变化：范围T_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        r：无风险利率
        sigma：标的资产波动率
    """
    
    price, _, _, theta, _, _ = zip(*[black_scholes_call(S0, K, T, r, sigma) for T in T_range])

    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    
    status=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    ax1.plot(T_range, price, 'b-', label=text_lang(f'看涨期权价格({status})',f'Call Option Price ({status})'))
    ax2.plot(T_range, theta, 'm--', label='Theta')
    
    ft_en=f"Note: European option, underlying price {S0}, strike price {K}, RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}, 行权价{K}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"    
    
    ax1.set_xlabel(text_lang('到期年数','Time to Maturity (Years)')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Theta', color='m')
    
    titletxt_en='Option Price & Theta vs Time to Maturity\n'
    titletxt_cn='到期时间对期权价格和Theta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="upper center"
        elif status in ['ITM','实值']:
            loc1="upper center"
        else:
            loc1="lower center"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="center right"
        elif status in ['ITM','实值']:
            loc2="lower center"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)

    plt.show()
    plt.close()   



def greek_call3_PriceNThetaVsTimeToMaturity(T_range, \
                                            K=100, r=0.05,sigma=0.2, \
                                            OTM=0.7, ITM=1.5, \
                                            loc1="lower right"):
    """
    功能：其他条件不变情况下，到期年数变化-->看涨期权Theta（虚值，平值，实值），不绘制期权价格
    注意：这里的Theta是年数变化的影响
    
    到期年数变化：范围T_range
    其他条件：
        S0：当期标的资产价格，分别为OTM*K（虚值）、K（平值）和ITM*K（实值），夸张一点！
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        r：无风险利率
        sigma：标的资产波动率
    """
    S_OTM=OTM*K
    _, _, _, theta_OTM, _, _ = zip(*[black_scholes_call(S_OTM, K, T, r, sigma) for T in T_range])

    S_ATM=K
    _, _, _, theta_ATM, _, _ = zip(*[black_scholes_call(S_ATM, K, T, r, sigma) for T in T_range])

    S_ITM=ITM*K
    _, _, _, theta_ITM, _, _ = zip(*[black_scholes_call(S_ITM, K, T, r, sigma) for T in T_range])


    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(T_range, theta_OTM, 'm--', label=text_lang(f'虚值期权Theta (S0={S_OTM})',f'OTM Theta (S0={S_OTM})'))
    ax.plot(T_range, theta_ITM, 'b-.', label=text_lang(f'实值期权Theta (S0={S_ITM})',f'ITM Theta (S0={S_ITM})'))
    ax.plot(T_range, theta_ATM, 'r-', label=text_lang(f'平值期权Theta (S0={S_ATM})',f'ATM Theta (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权, 行权价{K}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"    
    ax.set_xlabel(text_lang('到期年数','Time to Maturity (Years)')+'\n\n'+text_lang(ft_cn,ft_en))
    ax.set_ylabel('Theta', color='k')
    
    ax.axhline(0, color='gray', linestyle=':')
    
    titletxt_en='Call Option Theta vs Time to Maturity\n'
    titletxt_cn='到期时间对看涨期权Theta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    ax.legend(loc=loc1)

    plt.show()
    plt.close()   


#==============================================================================
def greek_put_PriceNThetaVsTimeToMaturity(T_range, \
                                           S0=100, K=100, r=0.05,sigma=0.2, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，到期年数变化-->看跌期权价格和Theta
    到期年数变化：范围T_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0<K（实值），若S0=K（平值），若S0>K（虚值）
        r：无风险利率
        sigma：标的资产波动率
    """
    
    price, _, _, theta, _, _ = zip(*[black_scholes_put(S0, K, T, r, sigma) for T in T_range])

    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    
    status=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    ax1.plot(T_range, price, 'b-', label=text_lang(f'看跌期权价格({status})',f'Put Option Price ({status})'))
    ax2.plot(T_range, theta, 'm--', label='Theta')
    
    ft_en=f"Note: European option, underlying price {S0}, strike price {K}, RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}, 行权价{K}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"    
    
    ax1.set_xlabel(text_lang('到期年数','Time to Maturity (Years)')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Theta', color='m')
    
    titletxt_en='Option Price & Theta vs Time to Maturity\n'
    titletxt_cn='到期时间对期权价格和Theta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="upper center"
        elif status in ['ITM','实值']:
            loc1="upper center"
        else:
            loc1="upper left"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="lower center"
        elif status in ['ITM','实值']:
            loc2="lower center"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)

    plt.show()
    plt.close()   



def greek_put3_PriceNThetaVsTimeToMaturity(T_range, \
                                           K=100, r=0.05,sigma=0.2, \
                                           ITM=0.8, OTM=1.2, \
                                           loc1="lower right"):
    """
    功能：其他条件不变情况下，到期年数变化-->看跌期权Theta（虚值，平值，实值），不绘制期权价格
    注意：这里的Theta是年数变化的影响
    
    到期年数变化：范围T_range
    其他条件：
        S0：当期标的资产价格，分别为OTM*K（虚值）、K（平值）和ITM*K（实值），夸张一点！
        K：行权价，若S0>K（虚值），若S0=K（平值），若S0<K（实值）
        r：无风险利率
        sigma：标的资产波动率
    """
    S_OTM=OTM*K
    _, _, _, theta_OTM, _, _ = zip(*[black_scholes_put(S_OTM, K, T, r, sigma) for T in T_range])

    S_ATM=K
    _, _, _, theta_ATM, _, _ = zip(*[black_scholes_put(S_ATM, K, T, r, sigma) for T in T_range])

    S_ITM=ITM*K
    _, _, _, theta_ITM, _, _ = zip(*[black_scholes_put(S_ITM, K, T, r, sigma) for T in T_range])


    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(T_range, theta_OTM, 'm--', label=text_lang(f'虚值期权Theta (S0={S_OTM})',f'OTM Theta (S0={S_OTM})'))
    ax.plot(T_range, theta_ITM, 'b-.', label=text_lang(f'实值期权Theta (S0={S_ITM})',f'ITM Theta (S0={S_ITM})'))
    ax.plot(T_range, theta_ATM, 'r-', label=text_lang(f'平值期权Theta (S0={S_ATM})',f'ATM Theta (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权, 行权价{K}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"    
    ax.set_xlabel(text_lang('到期年数','Time to Maturity (Years)')+'\n\n'+text_lang(ft_cn,ft_en))
    ax.set_ylabel('Theta', color='k')
    
    ax.axhline(0, color='gray', linestyle=':')
    
    titletxt_en='Put Option Theta vs Time to Maturity\n'
    titletxt_cn='到期时间对看跌期权Theta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    ax.legend(loc=loc1)

    plt.show()
    plt.close()   


# 看涨看跌二合一
def greek_PriceNThetaVsTimeToMaturity(T_range, \
                                      S0=100, K=100, r=0.05,sigma=0.2, \
                                      loc1="auto"):
    """
    功能：其他条件不变情况下，到期年数变化-->看涨看跌期权Theta（二合一），不绘制期权价格
    到期年数变化：范围T_range
    其他条件：
        S0：当期标的资产价格
        K：行权价
        r：无风险利率
        sigma：标的资产波动率
    """
    _, _, _, theta_call, _, _ = zip(*[black_scholes_call(S0, K, T, r, sigma) for T in T_range])
    _, _, _, theta_put, _, _ = zip(*[black_scholes_put(S0, K, T, r, sigma) for T in T_range])

    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    
    status_call=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    status_put=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    ax1.plot(T_range, theta_call, 'r-', label=text_lang(f'看涨期权Theta({status_call})',f'Call Theta ({status_call})'))
    ax1.plot(T_range, theta_put, 'b--', label=text_lang(f'看跌期权Theta({status_put})',f'Put Theta ({status_put})'))
    
    ax1.axhline(0, color='gray', linestyle=':')
    
    ft_en=f"Note: European option, underlying price {S0}, strike price {K}, RF {round(r*100,2)}%, volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}, 行权价{K}, 无风险利率{round(r*100,2)}%, 标的资产波动率{sigma}"    
    ax1.set_xlabel(text_lang('到期年数','Time to Maturity (Years)')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax1.set_ylabel('Theta', color='b')
    
    titletxt_en='Option Theta vs Time to Maturity\n'
    titletxt_cn='到期时间对期权Theta的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    if loc1.lower() == 'auto':
        if S0 < K:
            loc1="upper right"
        elif S0 > K:
            loc1="center right"
        else:
            loc1="lower right"

    ax1.legend(loc=loc1)

    plt.show()
    plt.close()   



#==============================================================================
#==============================================================================
if __name__ =="__main__":
    sigma_range = np.linspace(0.01, 1, 100) #分100份
    for s in sigma_range: print(s)
    
    # Fixed parameters
    S0 = 100
    S0=80
    S0=120
    
    K = 100
    T = 1
    r = 0.05
    
    loc1="auto"; loc2="auto"

def greek_call_PriceNVegaVsVolatility(sigma_range, \
                                           S0=100, K=100, T=1, r=0.05, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，标的资产波动率变化-->看涨期权价格和Vega
    注意：这里的Vega表示当波动率增加1个百分点（1%）时价格变化。
    
    标的资产波动率变化：范围sigma_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        T：到期年数
        r：无风险利率
    """

    price, _, _, _, vega, _ = zip(*[black_scholes_call(S0, K, T, r, sigma) for sigma in sigma_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(sigma_range, price, 'b-', label=text_lang('看涨期权价格','Call Option Price'))
    ax2.plot(sigma_range, vega, 'c--', label='Vega')
    
    status=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    
    ft_en=f"Note: European option, underlying price {S0} ({status}), strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}({status}), 行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%"
    
    ax1.set_xlabel(text_lang('标的资产波动率','Volatility')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Vega', color='c')
    
    titletxt_en='Option Price & Vega vs Volatility'
    titletxt_cn='标的资产波动率对期权价格和Vega的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))    

    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="lower center"
        elif status in ['ITM','实值']:
            loc1="lower center"
        else:
            loc1="lower center"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="center right"
        elif status in ['ITM','实值']:
            loc2="center right"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()



def greek_call3_PriceNVegaVsVolatility(sigma_range, \
                                       K=100, T=1, r=0.05, \
                                       OTM=0.8, ITM=1.2, \
                                       loc1="lower right"):
    """
    功能：其他条件不变情况下，标的资产波动率变化-->看涨期权Vega（三值合体），不绘制期权价格
    注意：这里的Vega表示当波动率增加1个百分点（1%）时价格变化。
    
    标的资产波动率变化：范围sigma_range
    其他条件：
        S0：当期标的资产价格，比例分别为OTM、1、ITM
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        T：到期年数
        r：无风险利率
    """
    S_OTM=OTM*K
    _, _, _, _, vega_OTM, _ = zip(*[black_scholes_call(S_OTM, K, T, r, sigma) for sigma in sigma_range])
    S_ATM=K
    _, _, _, _, vega_ATM, _ = zip(*[black_scholes_call(S_ATM, K, T, r, sigma) for sigma in sigma_range])
    S_ITM=ITM*K
    _, _, _, _, vega_ITM, _ = zip(*[black_scholes_call(S_ITM, K, T, r, sigma) for sigma in sigma_range])

    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(sigma_range, vega_OTM, 'c--', label=text_lang(f'虚值期权Vega (S0={S_OTM})',f'OTM Vega (S0={S_OTM})'))
    ax.plot(sigma_range, vega_ITM, 'b-.', label=text_lang(f'实值期权Vega (S0={S_ITM})',f'ITM Vega (S0={S_ITM})'))
    ax.plot(sigma_range, vega_ATM, 'r-', label=text_lang(f'平值期权Vega (S0={S_ATM})',f'ATM Vega (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%"
    ft_cn=f"注：欧式期权, 行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%"
    ax.set_xlabel(text_lang('标的资产波动率','Volatility')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax.set_ylabel('Vega', color='k')
    
    titletxt_en='Call Option Vega vs Volatility'
    titletxt_cn='标的资产波动率对看涨期权Vega的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))    

    ax.legend(loc=loc1)
    
    plt.show()
    plt.close()
    
    
#==============================================================================

def greek_put_PriceNVegaVsVolatility(sigma_range, \
                                           S0=100, K=100, T=1, r=0.05, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，标的资产波动率变化-->看跌期权价格和Vega
    注意：这里的Vega表示当波动率增加1个百分点（1%）时价格变化。
    
    标的资产波动率变化：范围sigma_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0>K（虚值），若S0=K（平值），若S0<K（实值）
        T：到期年数
        r：无风险利率
    """

    price, _, _, _, vega, _ = zip(*[black_scholes_put(S0, K, T, r, sigma) for sigma in sigma_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    ax1.plot(sigma_range, price, 'b-', label=text_lang('看跌期权价格','Put Option Price'))
    ax2.plot(sigma_range, vega, 'c--', label='Vega')
    
    status=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    
    ft_en=f"Note: European option, underlying price {S0} ({status}), strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}({status}), 行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%"
    
    ax1.set_xlabel(text_lang('标的资产波动率','Volatility')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Vega', color='c')
    
    titletxt_en='Option Price & Vega vs Volatility'
    titletxt_cn='标的资产波动率对期权价格和Vega的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))    

    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="lower center"
        elif status in ['ITM','实值']:
            loc1="lower center"
        else:
            loc1="lower center"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="center right"
        elif status in ['ITM','实值']:
            loc2="center right"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)
    
    plt.show()
    plt.close()
    

# 看涨看跌合体
def greek_PriceNVegaVsVolatility(sigma_range, \
                                 S0=100, K=100, T=1, r=0.05, \
                                 loc1="lower right"):
    """
    功能：其他条件不变情况下，标的资产波动率变化-->看涨看跌期权Vega（二合一），不绘制期权价格
    注意：这里的Vega表示当波动率增加1个百分点（1%）时价格变化。
    
    标的资产波动率变化：范围sigma_range
    其他条件：
        S0：当期标的资产价格
        K：行权价
        T：到期年数
        r：无风险利率
    """
    _, _, _, _, vega_call, _ = zip(*[black_scholes_call(S0, K, T, r, sigma) for sigma in sigma_range])
    _, _, _, _, vega_put, _ = zip(*[black_scholes_put(S0, K, T, r, sigma) for sigma in sigma_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    
    status_call=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    status_put=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    
    ax1.plot(sigma_range, vega_call, 'r-', label=text_lang(f'看涨期权Vega({status_call})',f'Call Vega ({status_call})'))
    ax1.plot(sigma_range, vega_put, 'b--', label=text_lang(f'看跌期权Vega({status_put})',f'Put Vega ({status_put})'))
    
    ft_en=f"Note: European option, underlying price {S0}, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}, 行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%"
    ax1.set_xlabel(text_lang('标的资产波动率','Volatility')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax1.set_ylabel('Vega', color='k')
    
    titletxt_en='Option Vega vs Volatility'
    titletxt_cn='标的资产波动率对期权Vega的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))    

    ax1.legend(loc=loc1)
    
    plt.show()
    plt.close()


def greek_put3_PriceNVegaVsVolatility(sigma_range, \
                                      K=100, T=1, r=0.05, \
                                      ITM=0.8, OTM=1.2, \
                                      loc1="lower right"):
    """
    功能：其他条件不变情况下，标的资产波动率变化-->看跌期权Vega（三值合体），不绘制期权价格
    注意：这里的Vega表示当波动率增加1个百分点（1%）时价格变化。
    
    标的资产波动率变化：范围sigma_range
    其他条件：
        S0：当期标的资产价格，比例分别为OTM、1、ITM
        K：行权价，若S0>K（虚值），若S0=K（平值），若S0<K（实值）
        T：到期年数
        r：无风险利率
    """
    S_OTM=OTM*K
    _, _, _, _, vega_OTM, _ = zip(*[black_scholes_put(S_OTM, K, T, r, sigma) for sigma in sigma_range])
    S_ATM=K
    _, _, _, _, vega_ATM, _ = zip(*[black_scholes_put(S_ATM, K, T, r, sigma) for sigma in sigma_range])
    S_ITM=ITM*K
    _, _, _, _, vega_ITM, _ = zip(*[black_scholes_put(S_ITM, K, T, r, sigma) for sigma in sigma_range])

    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(sigma_range, vega_OTM, 'b--', label=text_lang(f'虚值期权Vega (S0={S_OTM})',f'OTM Vega (S0={S_OTM})'))
    ax.plot(sigma_range, vega_ITM, 'c-.', label=text_lang(f'实值期权Vega (S0={S_ITM})',f'ITM Vega (S0={S_ITM})'))
    ax.plot(sigma_range, vega_ATM, 'r-', label=text_lang(f'平值期权Vega (S0={S_ATM})',f'ATM Vega (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} years(s), RF {round(r*100,2)}%"
    ft_cn=f"注：欧式期权, 行权价{K}, 到期年数{T}, 无风险利率{round(r*100,2)}%"
    ax.set_xlabel(text_lang('标的资产波动率','Volatility')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax.set_ylabel('Vega', color='k')
    
    titletxt_en='Put Option Vega vs Volatility'
    titletxt_cn='标的资产波动率对看跌期权Vega的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))    

    ax.legend(loc=loc1)
    
    plt.show()
    plt.close()
    

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    r_range = np.linspace(0.01, 0.2, 100) #分100份
    for r in r_range: print(r)
    
    # Fixed parameters
    S0 = 100
    S0=80
    S0=120
    
    K = 100
    T = 1
    sigma=0.2
    
    loc1="auto"; loc2="auto"
    
def greek_call_PriceNRhoVsRF(r_range, \
                                           S0=100, K=100, T=1, sigma=0.2, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，无风险利率变化-->看涨期权价格和Rho
    注意：这里的Rho表示当利率增加1个百分点（1%，即1个基点）时的价格变化。
    
    无风险利率变化：范围r_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        T：到期年数
        sigma：标的资产波动率
    """    
    
    price, _, _, _, _, rho = zip(*[black_scholes_call(S0, K, T, r, sigma) for r in r_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    
    ax1.plot(r_range, price, 'b-', label=text_lang('看涨期权价格','Call Option Price'))
    ax2.plot(r_range, rho, 'y--', label='Rho')
    
    status=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    
    ft_en=f"Note: European option, underlying price {S0} ({status}), strike price {K}, time to maturity {T} year(s), volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}({status}), 行权价{K}, 到期年数{T}, 标的资产波动率{sigma}"       
    
    ax1.set_xlabel(text_lang('利率','Interest Rate')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Rho', color='y')
    
    titletxt_en='Option Price & Rho vs Interest Rate\n'
    titletxt_cn='利率对期权价格和Rho的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="center left"
        elif status in ['ITM','实值']:
            loc1="upper left"
        else:
            loc1="upper left"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="center right"
        elif status in ['ITM','实值']:
            loc2="center right"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)

    plt.show()
    plt.close()    
    
    
def greek_call3_PriceNRhoVsRF(r_range, \
                              K=100, T=1, sigma=0.2, \
                              OTM=0.8, ITM=1.2, \
                              loc1="lower right"):
    """
    功能：其他条件不变情况下，无风险利率变化-->看涨期权Rho（三值合体），不绘制期权价格
    注意：这里的Rho表示当利率增加1个百分点（1%，即1个基点）时的价格变化。
    
    无风险利率变化：范围r_range
    其他条件：
        S0：当期标的资产价格，分为虚值、平值和实值
        K：行权价，若S0<K（虚值），若S0=K（平值），若S0>K（实值）
        T：到期年数
        sigma：标的资产波动率
    """    
    S_OTM=OTM*K
    _, _, _, _, _, rho_OTM = zip(*[black_scholes_call(S_OTM, K, T, r, sigma) for r in r_range])
    S_ATM=K
    _, _, _, _, _, rho_ATM = zip(*[black_scholes_call(S_ATM, K, T, r, sigma) for r in r_range])
    S_ITM=ITM*K
    _, _, _, _, _, rho_ITM = zip(*[black_scholes_call(S_ITM, K, T, r, sigma) for r in r_range])

    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(r_range, rho_OTM, 'y--', label=text_lang(f'虚值期权Rho (S0={S_OTM})',f'OTM Rho (S0={S_OTM})'))
    ax.plot(r_range, rho_ITM, 'b-.', label=text_lang(f'实值期权Rho (S0={S_ITM})',f'ITM Rho (S0={S_ITM})'))
    ax.plot(r_range, rho_ATM, 'r-', label=text_lang(f'平值期权Rho (S0={S_ATM})',f'ATM Rho (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} year(s), volatility {sigma}"
    ft_cn=f"注：欧式期权, 行权价{K}, 到期年数{T}, 标的资产波动率{sigma}"       
    ax.set_xlabel(text_lang('利率','Interest Rate')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax.set_ylabel('Rho', color='k')
    
    titletxt_en='Call Option Rho vs Interest Rate\n'
    titletxt_cn='利率对看涨期权Rho的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    ax.legend(loc=loc1)

    plt.show()
    plt.close()    
    



#==============================================================================
def greek_put_PriceNRhoVsRF(r_range, \
                                           S0=100, K=100, T=1, sigma=0.2, \
                                           loc1="auto",loc2="auto"):
    """
    功能：其他条件不变情况下，无风险利率变化-->看跌期权价格和Rho
    注意：这里的Rho表示当利率增加1个百分点（1%，即1个基点）时的价格变化。

    无风险利率变化：范围r_range
    其他条件：
        S0：当期标的资产价格
        K：行权价，若S0>K（虚值），若S0=K（平值），若S0<K（实值）
        T：到期年数
        sigma：标的资产波动率
    """    
    
    price, _, _, _, _, rho = zip(*[black_scholes_put(S0, K, T, r, sigma) for r in r_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    ax2 = ax1.twinx()
    
    ax1.plot(r_range, price, 'b-', label=text_lang('看跌期权价格','Put Option Price'))
    ax2.plot(r_range, rho, 'y--', label='Rho')
    
    status=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    
    ft_en=f"Note: European option, underlying price {S0} ({status}), strike price {K}, time to maturity {T} year(s), volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}({status}), 行权价{K}, 到期年数{T}, 标的资产波动率{sigma}"       
    
    ax1.set_xlabel(text_lang('利率','Interest Rate')+'\n\n'+text_lang(ft_cn,ft_en))
    ax1.set_ylabel(text_lang('期权价格','Option Price'), color='b')
    ax2.set_ylabel('Rho', color='y')
    
    titletxt_en='Option Price & Rho vs Interest Rate\n'
    titletxt_cn='利率对期权价格和Rho的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))
    
    if loc1.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc1="center left"
        elif status in ['ITM','实值']:
            loc1="center left"
        else:
            loc1="center left"

    if loc2.lower() == 'auto':
        if status in ['OTM','虚值']:
            loc2="center right"
        elif status in ['ITM','实值']:
            loc2="center right"
        else:
            loc2="center right"

    ax1.legend(loc=loc1); ax2.legend(loc=loc2)

    plt.show()
    plt.close()    

    
    
def greek_put3_PriceNRhoVsRF(r_range, \
                             K=100, T=1, sigma=0.2, \
                             ITM=0.8, OTM=1.2, \
                             loc1="lower right"):
    """
    功能：其他条件不变情况下，无风险利率变化-->看跌期权Rho（三值合体），不绘制期权价格
    注意：这里的Rho表示当利率增加1个百分点（1%，即1个基点）时的价格变化。
    
    无风险利率变化：范围r_range
    其他条件：
        S0：当期标的资产价格，分为虚值、平值和实值
        K：行权价，若S0>K（虚值），若S0=K（平值），若S0<K（实值）
        T：到期年数
        sigma：标的资产波动率
    """    
    S_OTM=OTM*K
    _, _, _, _, _, rho_OTM = zip(*[black_scholes_put(S_OTM, K, T, r, sigma) for r in r_range])
    S_ATM=K
    _, _, _, _, _, rho_ATM = zip(*[black_scholes_put(S_ATM, K, T, r, sigma) for r in r_range])
    S_ITM=ITM*K
    _, _, _, _, _, rho_ITM = zip(*[black_scholes_put(S_ITM, K, T, r, sigma) for r in r_range])

    
    fig, ax = plt.subplots(figsize=(12.8,6.4))
    ax.plot(r_range, rho_OTM, 'y--', label=text_lang(f'虚值期权Rho (S0={S_OTM})',f'OTM Rho (S0={S_OTM})'))
    ax.plot(r_range, rho_ITM, 'b-.', label=text_lang(f'实值期权Rho (S0={S_ITM})',f'ITM Rho (S0={S_ITM})'))
    ax.plot(r_range, rho_ATM, 'r-', label=text_lang(f'平值期权Rho (S0={S_ATM})',f'ATM Rho (S0={S_ATM})'))
    
    ft_en=f"Note: European option, strike price {K}, time to maturity {T} year(s), volatility {sigma}"
    ft_cn=f"注：欧式期权, 行权价{K}, 到期年数{T}, 标的资产波动率{sigma}"       
    ax.set_xlabel(text_lang('利率','Interest Rate')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax.set_ylabel('Rho', color='k')
    
    titletxt_en='Put Option Rho vs Interest Rate\n'
    titletxt_cn='利率对看跌期权Rho的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    ax.legend(loc=loc1)

    plt.show()
    plt.close()    
    
    
    
# 看涨看跌二合一    
def greek_PriceNRhoVsRF(r_range, \
                        S0=100, K=100, T=1, sigma=0.2, \
                        loc1="auto"):
    """
    功能：其他条件不变情况下，无风险利率变化-->看涨看跌期权Rho（二合一），不绘制期权价格
    注意：这里的Rho表示当利率增加1个百分点（1%，即1个基点）时的价格变化。

    无风险利率变化：范围r_range
    其他条件：
        S0：当期标的资产价格
        K：行权价
        T：到期年数
        sigma：标的资产波动率
    """    
    _, _, _, _, _, rho_call = zip(*[black_scholes_call(S0, K, T, r, sigma) for r in r_range])
    _, _, _, _, _, rho_put = zip(*[black_scholes_put(S0, K, T, r, sigma) for r in r_range])
    
    fig, ax1 = plt.subplots(figsize=(12.8,6.4))
    
    status_call=text_lang('虚值','OTM') if S0<K else text_lang('实值','ITM') if S0>K else text_lang('平值','ATM')
    status_put=text_lang('虚值','OTM') if S0>K else text_lang('实值','ITM') if S0<K else text_lang('平值','ATM')
    
    ax1.plot(r_range, rho_call, 'r-', label=text_lang(f'看涨期权Rho({status_call})',f'Call Rho ({status_call})'))
    ax1.plot(r_range, rho_put, 'b--', label=text_lang(f'看跌期权Rho({status_put})',f'Put Rho ({status_put})'))
    
    ax1.axhline(0, color='gray', linestyle=':')
    
    ft_en=f"Note: European option, underlying price {S0}, strike price {K}, time to maturity {T} year(s), volatility {sigma}"
    ft_cn=f"注：欧式期权, 标的资产价格{S0}, 行权价{K}, 到期年数{T}, 标的资产波动率{sigma}"       
    ax1.set_xlabel(text_lang('利率','Interest Rate')+'\n\n'+text_lang(ft_cn,ft_en))
    
    ax1.set_ylabel('Rho', color='k')
    
    titletxt_en='Option Rho vs Interest Rate\n'
    titletxt_cn='利率对期权价格和Rho的影响\n'
    plt.title(text_lang(titletxt_cn,titletxt_en))

    if loc1.lower() == 'auto':
        if S0 < K:
            loc1="center left"
        elif S0 > K:
            loc1="center left"
        else:
            loc1="lower right"

    ax1.legend(loc=loc1)

    plt.show()
    plt.close()    

    
#==============================================================================
#==============================================================================
import numpy as np

def option_exercise(S0, K, r, sigma, T, option_type="put", \
                    n=1000000, seed=123456789, printout=True):
    """
    蒙特卡洛模拟欧式期权的行权概率和预期收益（到期内在价值）
    
    参数：
    S0 : float  当前标的资产价格
    K  : float  行权价
    r  : float  无风险利率（年化，连续复利）
    sigma : float 波动率（年化）
    T  : float  到期时间（以年为单位）
    n  : int    模拟次数
    option_type : str  "call" 或 "put"
    seed : int 或 None  随机种子（确保结果可重复）
    
    返回：
    exercise_prob : float  被行权的概率
    expected_payoff : float  期权到期预期收益（未贴现）
    option_price   : float  期权现值（贴现后的预期收益）
    """
    # 设置随机种子
    if seed is not None:
        np.random.seed(seed)
    
    # 生成标准正态随机数
    Z = np.random.randn(n)
    
    # 模拟标的到期价格 (几何布朗运动)
    # 这个公式描述的是标的资产价格的随机演化，是Black–Scholes模型假设的几何布朗运动
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    
    # 计算期权 payoff
    if option_type.lower() == "call":
        payoff = np.maximum(ST - K, 0)
    elif option_type.lower() == "put":
        payoff = np.maximum(K - ST, 0)
    else:
        raise ValueError("option_type must be either 'call' or 'put'")
    
    # 被行权概率
    exercise_prob = np.mean(payoff > 0)
    
    # 到期预期收益（未贴现）
    expected_payoff = np.mean(payoff)
    
    # 到期预期标的资产价格
    if option_type.lower() == "call":
        expected_ST = expected_payoff + K
    elif option_type.lower() == "put":
        expected_ST = -expected_payoff + K
    else:
        raise ValueError("option_type must be either 'call' or 'put'")
    
    
    # 期权现值（贴现）
    option_price = np.exp(-r * T) * expected_payoff
    
    if printout:
        
        print(text_lang(f"{option_type.title()}期权：",f"{option_type.title()} Option:"))
        print(text_lang(f"  到期时标的资产价格预期：{expected_ST:.4f}",f"Expected underlying price on maturity: {expected_ST:.4f}"),)
        print(text_lang(f"  被行权概率 = {exercise_prob:.2%}","  Probability of being exercised = {exercise_prob:.2%}"))
        print(text_lang(f"  到期预期收益(未折现) = {expected_payoff:.4f}",f"  Expected payoff (undiscounted) = {expected_payoff:.4f}"))
        print(text_lang(f"  现值(期权价格，折现后) = {option_price:.4f}",f"  Present value (option price, discounted) = {option_price:.4f}"))        
    
    return exercise_prob, expected_payoff, option_price

if __name__ =="__main__":
    # 示例：标的80, 行权价100, r=5%, sigma=20%, T=1年，固定种子
    S0, K, r, sigma, T = 80, 100, 0.05, 0.2, 1
    prob_put, payoff_put, price_put = monte_carlo_option(S0, K, r, sigma, T, option_type="put")
    

#==============================================================================
#==============================================================================
# 整合函数compare_greek
def compare_greeks(indicator='Delta', direction='Both', option_price=False, \
                   S0=80, K=100, T=1, r=0.05, sigma=0.2, \
                   factor_range='auto', OTM='auto', ITM='auto', \
                   loc1="auto",loc2="auto"):
    """
    功能：对比演示期权希腊值之间的异同之处
    参数：
    indicator：希腊值指标，默认'Delta', 可选'Delta'、'Gamma'、'Theta'、'Vega'、'Rho'
    direction：期权方向，默认'Both', 可选'Both'、'Call'、'Put'
    option_price：是否同步绘制期权价格，默认否False；若选True则不进行同图对比，分图绘制
    期权要素：
        默认当期标的资产价格S0=80, 期权行权价K=100, 到期年数T=1, 无风险利率r=0.05, 标的资产波动率sigma=0.2
        indicator若选'Delta'或'Gamma'，则由factor_range（S_range）取代S0；
        indicator若选'Theta'，则由factor_range（T_range）取代T；
        indicator若选'Vega'，则由factor_range（sigma_range）取代sigma；
        indicator若选'Rho'，则由factor_range（r_range）取代r；
    factor_range：
        期权要素，形式须为np.linspace(起点值, 终点值, 取值个数)，NumPy数组（ndarray）
        默认'auto', 可根据不同的indicator自动设置为不同的期权要素数组
    OTM和ITM：
        用于对比时设置标的资产价格，基于行权价K的虚值和实值比例，默认'auto'
        即设置标的资产价格S0=K*OTM（虚值时），S0=K*ITM（实值时），S0=K（平值时）
    loc1和loc2：
        设置图例位置，默认"auto"，若位置不合适可以手动调整。
    
    """
    import numpy as np
    
    # 整理参数
    indicator=indicator.title()
    direction=direction.lower()
    if factor_range != 'auto':
        if not isinstance(factor_range, np.ndarray):
            print("  Warning: parameter factor_range must be either auto or numpy array (ndarray)")
            print("  Solution: use np.linspace(start_value, end_value, numbers) to define")
            return
    
    # Delta：标的资产价格的影响
    # Gamma：标的资产价格的二次影响
    if indicator in ['Delta','Gamma']:
        if factor_range == 'auto':
            S_range = np.linspace(50, 150, 100) #从50到150分100份
        else:
            S_range = factor_range
            
        if direction == 'call':
            if indicator == 'Delta':
                if loc1 == 'auto':  loc1="upper left"
                if loc2 == 'auto':  loc2="lower right"
                
                greek_call_PriceNDeltaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, \
                                                        loc1=loc1,loc2=loc2)
            if indicator == 'Gamma':
                if loc1 == 'auto':  loc1="center left"
                if loc2 == 'auto':  loc2="center right"

                greek_call_PriceNGammaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, \
                                                        loc1=loc1,loc2=loc2)
                    
        elif direction == 'put':
            if indicator == 'Delta':
                if loc1 == 'auto':  loc1="center left"
                if loc2 == 'auto':  loc2="center right"

                greek_put_PriceNDeltaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, \
                                                       loc1=loc1,loc2=loc2)
            if indicator == 'Gamma':
                if loc1 == 'auto':  loc1="center left"
                if loc2 == 'auto':  loc2="center right"

                greek_put_PriceNGammaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, \
                                                       loc1=loc1,loc2=loc2)
                    
        else: # 看涨看跌二图合体
            if indicator == 'Delta':
                if loc1 == 'auto':  loc1="upper left"
                greek_PriceNDeltaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, loc1=loc1)
                
            if indicator == 'Gamma':
                if loc1 == 'auto':  loc1="upper left"
                greek_PriceNGammaVsUnderlyingPrice(S_range, K=K, T=T, r=r, sigma=sigma, loc1=loc1)
        
    # Theta：到期时间的影响
    if indicator in ['Theta']:
        if factor_range == 'auto':
            T_range = np.linspace(0, 2, 100)
        else:
            T_range = factor_range
            
        if option_price and (direction == 'call'):
            greek_call_PriceNThetaVsTimeToMaturity(T_range, S0=S0, K=K, r=r, sigma=sigma, \
                                                   loc1=loc1, loc2=loc2)
        if option_price and (direction == 'put'):
            greek_put_PriceNThetaVsTimeToMaturity(T_range, S0=S0, K=K, r=r, sigma=sigma, \
                                                   loc1=loc1, loc2=loc2)
            
        if (not option_price) and (direction == 'call'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=0.7
            if ITM == 'auto': ITM=1.5
            greek_call3_PriceNThetaVsTimeToMaturity(T_range, K=K, r=r, sigma=sigma, \
                                                    OTM=OTM, ITM=ITM, loc1=loc1)
            
        if (not option_price) and (direction == 'put'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=1.2
            if ITM == 'auto': ITM=0.8
            greek_put3_PriceNThetaVsTimeToMaturity(T_range, K=K, r=r, sigma=sigma, \
                                                    OTM=OTM, ITM=ITM, loc1=loc1)

        if direction == 'both':
            greek_PriceNThetaVsTimeToMaturity(T_range, S0=S0, K=K, r=r, sigma=sigma, loc1=loc1)
        
    # Vega：标的资产波动率的影响
    if indicator in ['Vega']:
        if factor_range == 'auto':
            sigma_range = np.linspace(0.01, 1, 100) #分100份
        else:
            sigma_range = factor_range
            
        if option_price and (direction == 'call'):
            greek_call_PriceNVegaVsVolatility(sigma_range, S0=S0, K=K, T=T, r=r, \
                                              loc1=loc1, loc2=loc2)
        if option_price and (direction == 'put'):
            greek_put_PriceNVegaVsVolatility(sigma_range, S0=S0, K=K, T=T, r=r, \
                                             loc1=loc1, loc2=loc2)
            
        if (not option_price) and (direction == 'call'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=0.8
            if ITM == 'auto': ITM=1.2
            greek_call3_PriceNVegaVsVolatility(sigma_range, K=K, T=T, r=r, \
                                               OTM=OTM, ITM=ITM, \
                                               loc1=loc1)
            
        if (not option_price) and (direction == 'put'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=1.2
            if ITM == 'auto': ITM=0.8
            greek_put3_PriceNVegaVsVolatility(sigma_range, K=K, T=T, r=r, \
                                              ITM=ITM, OTM=OTM, \
                                                  loc1=loc1)

        if direction == 'both':
            if loc1 == 'auto': loc1="lower right"
            greek_PriceNVegaVsVolatility(sigma_range, S0=S0, K=K, T=T, r=r, \
                                         loc1=loc1)
        
    # Rho：利率的影响
    if indicator in ['Rho']:
        if factor_range == 'auto':
           r_range = np.linspace(0.01, 0.2, 100)
        else:
            r_range = factor_range
            
        if option_price and (direction == 'call'):
            greek_call_PriceNRhoVsRF(r_range, S0=S0, K=K, T=T, sigma=sigma, \
                                     loc1=loc1, loc2=loc2)
        if option_price and (direction == 'put'):
            greek_put_PriceNRhoVsRF(r_range, S0=S0, K=K, T=T, sigma=sigma, \
                                    loc1=loc1, loc2=loc2)
            
        if (not option_price) and (direction == 'call'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=0.8
            if ITM == 'auto': ITM=1.2
            greek_call3_PriceNRhoVsRF(r_range, K=K, T=T, sigma=sigma, \
                                      OTM=OTM, ITM=ITM, \
                                          loc1=loc1)
            
        if (not option_price) and (direction == 'put'):
            if loc1 == 'auto': loc1="lower right"
            if OTM == 'auto': OTM=1.2
            if ITM == 'auto': ITM=0.8
            greek_put3_PriceNRhoVsRF(r_range, K=K, T=T, sigma=sigma, \
                                     ITM=ITM, OTM=OTM, \
                                         loc1=loc1)

        if direction == 'both':
            greek_PriceNRhoVsRF(r_range, S0=S0, K=K, T=T, sigma=sigma, \
                                loc1=loc1)

    return



#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================

