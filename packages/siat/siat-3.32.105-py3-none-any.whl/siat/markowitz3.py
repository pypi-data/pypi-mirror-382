# -*- coding: utf-8 -*-
"""
本模块功能：证券投资组合理论优化分析，手动输入RF版
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年4月19日
最新修订日期：2024年4月19日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")   
#==============================================================================
  
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.stock import *
from siat.markowitz2 import *
from siat.grafix import *
#from siat.fama_french import *

import pandas as pd
import numpy as np
import datetime
#==============================================================================
import seaborn as sns
import matplotlib.pyplot as plt
#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
#plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=13
xlabel_txt_size=13
legend_txt_size=13

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    sns.set_style('whitegrid',{'font.sans-serif':['simhei','Arial']})

if czxt in ['darwin','linux']: #MacOSX
    #plt.rcParams['font.family'] = ['Arial Unicode MS'] #用来正常显示中文标签
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}
    sns.set_style('whitegrid',{'font.sans-serif':['Arial Unicode MS','Arial']})


# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
#全局变量定义
RANDOM_SEED=1234567890

#==============================================================================
#==============================================================================

#==============================================================================
if __name__=='__main__':
    #测试1
    Market={'Market':('US','^GSPC')}
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.3,'MSFT':.15,'AMZN':.15,'GOOG':.01}
    Stocks2={'XOM':.02,'JNJ':.02,'JPM':.01,'TSLA':.3,'SBUX':.03}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    #测试2
    Market={'Market':('China','000300.SS','养猪1号组合')}
    porkbig={'000876.SZ':0.20,#新希望
             '300498.SZ':0.15,#温氏股份
            }
    porksmall={'002124.SZ':0.10,#天邦股份
               '600975.SS':0.10,#新五丰
               '603477.SS':0.10,#巨星股份
               '000735.SZ':0.07,#罗牛山
              }
    portfolio=dict(Market,**porkbig,**porksmall)    

    #测试3
    Market={'Market':('China','000300.SS','股债基组合')}
    Stocks={'600519.SS':0.3,#股票：贵州茅台
            'sh010504':[0.5,'bond'],#05国债⑷
            '010504.SS':('fund',0.2),#招商稳兴混合C基金
            }
    portfolio=dict(Market,**Stocks)

    printout=True 
    graph=False
    
    indicator='Adj Close'
    adjust='qfq'; source='auto'; ticker_type='bond'
    thedate='2024-6-19'
    pastyears=2

    
    #测试3
    Market={'Market':('China','000300.SS','股债基组合')}
    Stocks={'600519.SS':0.3,#股票：贵州茅台
            'sh010504':[0.5,'bond'],#05国债⑷
            '010504.SS':('fund',0.2),#招商稳兴混合C基金
            }
    portfolio=dict(Market,**Stocks)

    #测试4
    portfolio,RF=portfolio_define(
        name="银行概念基金1号",
        market='CN',market_index='000001.SS',
        members={
            '601939.SS':.4,#中国建设银行
            '600000.SS':.3, #浦东发展银行
            '601998.SS':.2,#中信银行
            '601229.SS':.1,#上海银行
            }
        )

    indicator='Adj Close'
    adjust=''; source='auto'; ticker_type='auto'
    thedate='2025-7-1'
    pastyears=1
    printout=False 
    graph=False
    facecolor='papayawhip'
    DEBUG=False
    
    pf_info=portfolio_build2(portfolio,thedate,pastyears,graph=False,printout=False)

def portfolio_build2(portfolio,thedate='today',pastyears=3, \
                    indicator='Adj Close', \
                    source='auto',ticker_type='auto', \
                    printout=False,graph=False,facecolor='papayawhip', \
                        annotate=False,annotate_value=False,
                    DEBUG=False):    
    """
    功能：收集投资组合成份股数据，绘制收益率趋势图，并与等权和期间内流动性加权策略组合比较
    注意：
    1. 此处无需RF，待到优化策略时再指定
    2. printout=True控制下列内容是否显示：
        获取股价时的信息
        是否显示原始组合、等权重组合和交易金额加权组合的成分股构成
        是否显示原始组合、等权重组合和交易金额加权组合的收益风险排名
    3. pastyears=3更有可能生成斜向上的椭圆形可行集，短于3形状不佳，长于3改善形状有限。
        需要与不同行业的证券搭配。同行业证券相关性较强，不易生成斜向上的椭圆形可行集。
    4. 若ticker_type='fund'可能导致无法处理股票的复权价！
    5. 若要指定特定的证券为债券，则需要使用列表逐一指定证券的类型（股票，债券，基金）
    6. 默认采用前复权计算收益率，更加平稳
    """
    import numpy as np
    import pandas as pd

    #判断复权标志
    indicator_list=['Close','Adj Close']
    if indicator not in indicator_list:
        print("  Warning(portfolio_build): invalid indicator",indicator)
        print("  Supported indicator:",indicator_list)
        indicator='Adj Close'
    
    import datetime
    stoday = datetime.date.today()
    if thedate.lower == 'today':
        thedate=str(stoday)
    else:
        if not check_date(thedate):
            print("  #Warning(portfolio_build): invalid date",thedate)
            return None
    
    print(f"  Searching portfolio info for recent {pastyears} years ...")
    # 解构投资组合
    scope,mktidx,tickerlist,sharelist0,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)

    #如果持仓份额总数不为1，则将其转换为总份额为1
    totalshares=np.sum(sharelist0)
    if abs(totalshares - 1) >= 0.00001:
        print("  #Warning(portfolio_build): total weights is",totalshares,"\b, expecting 1.0 here")
        print("  Action taken: automatically converted into total weights 1.0")
        sharelist=list(sharelist0/totalshares) 
    else:
        sharelist=sharelist0

    #..........................................................................    
    # 计算历史数据的开始日期
    start=get_start_date(thedate,pastyears)
    
    #..........................................................................
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    # 抓取投资组合股价
    if printout:
        #债券优先
        prices,found=get_price_mticker(tickerlist,start,thedate, \
                              adjust='qfq',source=source,ticker_type=ticker_type,fill=True)
        market,found2=get_price_1ticker(mktidx,start,thedate, \
                              adjust='qfq',source=source,ticker_type=ticker_type,fill=True)
            
    else:
        with HiddenPrints():
            prices,found=get_price_mticker(tickerlist,start,thedate, \
                                  adjust='qfq',source=source,ticker_type=ticker_type,fill=True)
            market,found2=get_price_1ticker(mktidx,start,thedate, \
                                  adjust='qfq',source=source,ticker_type=ticker_type,fill=True)
    
    # 处理部分成分股数据可能缺失，将所有成分股的开始日期对齐
    # 假设 prices 的列 MultiIndex 的第二层是股票代码
    # 如果股票代码在第一层，请调整 level 参数
    first_valid_dates = prices.apply(pd.Series.first_valid_index)
    
    # first_valid_dates 是一个 Series，索引是股票代码，值是各自的首个有效日期
    # 找到所有股票中最晚的那个上市日期
    cutoff_date = first_valid_dates.max()
    
    # 从 cutoff_date 开始截取数据
    prices = prices.loc[cutoff_date:]   
    market =  market.loc[cutoff_date:]
    
    if len(prices) == 0:
        found = 'Empty'
                
    if found == 'Found':
        got_tickerlist=list(prices['Close'])
        nrecords=len(prices)

        diff_tickerlist = list(set(tickerlist) - set(got_tickerlist))
        if len(diff_tickerlist) > 0:
            print(f"  However, failed to access the prices of securities {diff_tickerlist}")
            return None
    else:    
        print(f"  #Error(portfolio_build): failed to get portfolio member prices for {pname}")
        return None
                
    if found2 != 'Found':
        print(f"  #Error(portfolio_build): failed to get market index {mktidx} for {pname}")
        return None
        
        
    # 取各个成份股的收盘价：MultiIndex，第1层为价格，结构为('Adj Close','AAPL')
    member_prices=prices[indicator][tickerlist].copy()

    # 将原投资组合的权重存储为numpy数组类型，为了合成投资组合计算方便
    portfolio_weights = np.array(sharelist)
    #portfolio_value = member_prices.dot(portfolio_weights)
    portfolio_value = member_prices.mul(portfolio_weights).sum(axis=1)
    
    # 计算投资组合的日收益率，并丢弃缺失值
    portfolio_dret=pd.DataFrame()
    portfolio_dret['Portfolio'] =portfolio_value.pct_change().dropna()
    #..........................................................................
    
    # 绘制原投资组合的收益率曲线，以便使用收益率%来显示
    if graph:
        portfolio_dret['Portfolio'].plot(label=pname)
        plt.axhline(y=0,ls=":",c="red")
        
        title_txt=text_lang("投资组合: 日收益率的变化趋势","Investment Portfolio: Daily Return")
        ylabel_txt=text_lang("日收益率","Daily Return")
        source_txt=text_lang("来源: 综合新浪/东方财富/Stooq/雅虎等, ","Data source: Sina/EM/Stooq/Yahoo, ")
        
        plt.title('\n'+title_txt+'\n')
        plt.ylabel(ylabel_txt)
        
        stoday = datetime.date.today()
        plt.xlabel('\n'+source_txt+str(stoday))
        
        plt.gca().set_facecolor(facecolor)
        
        plt.legend(); plt.show(); plt.close()
        #..........................................................................
        
    # 计算并存储原始投资组合的结果
    StockReturns=pd.DataFrame()
    # 计算投资组合的持有期收益率
    StockReturns['Portfolio'] =portfolio_value / portfolio_value.iloc[0] - 1
    
    #绘制持有收益率曲线
    if graph:
        # 计算原投资组合的持有收益率，并绘图
        name_list=["Portfolio"]
        label_list=[pname]
        
        titletxt=text_lang("投资组合: 持有收益率的变化趋势","Investment Portfolio: Holding Period Return%")
        #titletxt=text_lang(f"投资组合: {pname}","Investment Portfolio: {pname}")
        ylabeltxt=text_lang("持有收益率","Holding Period Return%")
        xlabeltxt1=text_lang("数据来源: 综合新浪/东方财富/Stooq/雅虎等, ","Data source: Sina/EM/Stooq/Yahoo, ")
        xlabeltxt=xlabeltxt1+str(stoday)
        
        cumulative_returns_plot(portfolio_dret,name_list,titletxt,ylabeltxt,xlabeltxt,label_list, \
                                facecolor=facecolor,annotate=True,annotate_value=True)
    #..........................................................................
    
    # 构造等权重组合Portfolio_EW的持有收益率
    numstocks = len(tickerlist)
    # 平均分配每一项的权重
    portfolio_weights_ew = np.repeat(1/numstocks, numstocks)
    # 合成等权重组合的收益，按行横向加总
    portfolio_value_ew = member_prices.dot(portfolio_weights_ew)
    portfolio_dret['Portfolio_EW'] =portfolio_value_ew.pct_change().dropna()
    StockReturns['Portfolio_EW'] =portfolio_value_ew / portfolio_value_ew.iloc[0] - 1
    #..........................................................................
    
    # 创建流动性加权组合：按照成交金额计算期间内交易额均值。债券和基金信息中无成交量！
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        tamount=prices['Close']*prices['Volume']
        tamountlist=tamount.mean(axis=0)    #求列的均值
        tamountlist_array = np.array(tamountlist)
        # 计算成交金额权重
        portfolio_weights_lw = tamountlist_array / np.sum(tamountlist_array)
        # 计算成交金额加权的组合收益
        portfolio_value_lw = member_prices.dot(portfolio_weights_lw)
        portfolio_dret['Portfolio_LW'] =portfolio_value_lw.pct_change().dropna()
        StockReturns['Portfolio_LW'] =portfolio_value_lw / portfolio_value_lw.iloc[0] - 1

    #绘制累计收益率对比曲线
    title_txt=text_lang("投资组合策略：业绩对比","Portfolio Strategies: Performance")
    Portfolio_EW_txt=text_lang("等权重策略","Equal-weighted")
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        Portfolio_LW_txt=text_lang("流动性加权策略","Liquidity-weighted")
    
        name_list=['Portfolio', 'Portfolio_EW', 'Portfolio_LW']
        label_list=[pname, Portfolio_EW_txt, Portfolio_LW_txt]
    else: #没有成交量数据无法实施流动性策略
        name_list=['Portfolio', 'Portfolio_EW']
        label_list=[pname, Portfolio_EW_txt]
        
        
    titletxt=title_txt
    
    #绘制各个投资组合的持有收益率曲线
    if graph:
        cumulative_returns_plot(portfolio_dret,name_list,titletxt,ylabeltxt,xlabeltxt,label_list, \
                                facecolor=facecolor,annotate=annotate,annotate_value=annotate_value)

    #打印各个投资组合的持股比例
    portfolio_info=portfolio_expectation_universal1(pname,StockReturns['Portfolio'],portfolio_weights,member_prices,ticker_type,printout=printout)
    portfolio_info_ew=portfolio_expectation_universal1(Portfolio_EW_txt,StockReturns['Portfolio_EW'],portfolio_weights_ew,member_prices,ticker_type,printout=printout)
    portfolio_info_list=[portfolio_info,portfolio_info_ew]
        
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        portfolio_info_lw=portfolio_expectation_universal1(Portfolio_LW_txt,StockReturns['Portfolio_LW'],portfolio_weights_lw,member_prices,ticker_type,printout=printout)
        portfolio_info_list= portfolio_info_list+[portfolio_info_lw]
            
    #返回投资组合的综合信息
    portfolio_returns=StockReturns[name_list]
    
    #投资组合名称改名
    portfolio_returns=cvt_portfolio_name(pname,portfolio_returns)
    
    #打印现有投资组合策略的排名
    prr2=portfolio_ranks2(portfolio_info_list,pname,facecolor=facecolor,printout=printout)
    
    print(f"  Successfully built investment portfolio {pname} with {len(tickerlist)} securities")
    # 输出信息结构pf_info: 
    # 投资组合构造信息portfolio，评估日期thedate，各个成分股价格历史member_prices
    # 已有投资组合的持有期收益率历史portfolio_returns，已有投资组合的年化收益率和标准差prr2
    pf_info=[portfolio,thedate,member_prices,market,portfolio_returns,portfolio_info_list]
    return pf_info
        

if __name__=='__main__':
    X=portfolio_build(portfolio,'2021-9-30')

if __name__=='__main__':
    pf_info=portfolio_build(portfolio,'2021-9-30')


#==============================================================================
    
    
def portfolio_correlate2(pf_info,facecolor='papayawhip'):
    """
    功能：绘制投资组合成份股之间相关关系的热力图
    """
    portfolio,thedate,member_prices_original,_,_,_=pf_info
    pname=portfolio_name(portfolio)
    
    member_prices=member_prices_original.copy()
    # 计算日收益率：(当日价格/前一日价格) - 1
    stock_return = (member_prices / member_prices.shift(1)) - 1    
    
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))
        
    sr=stock_return.copy()
    collist=list(sr)
    for col in collist:
        #投资组合中名称翻译以债券优先处理，因为几乎没有人把基金作为成分股
        sr.rename(columns={col:ticker_name(col,'bond')},inplace=True)

    # 计算相关矩阵
    correlation_matrix = sr.corr()
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(correlation_matrix,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 16})
    
    titletxt_en=f"\n{pname}: Correlation Coefficient Among Member Security\'s Returns\n"
    titletxt_cn=f"\n{pname}: 成份证券收益率之间的相关系数\n"
    plt.title(text_lang(titletxt_cn,titletxt_en))
    plt.ylabel(text_lang("成份证券","Member Security"))
    
    footnote1cn="观察期间: "+hstart+'至'+hend
    footnote1en=f"Period: from {hstart} to {hend}"
    footnote1=text_lang(footnote1cn,footnote1en)
    
    import datetime as dt; stoday=dt.date.today()    
    footnote2cn="数据来源：Sina/EM/stooq，"+str(stoday)
    footnote2en=f"Data source: Sina/EM/Stooq, {str(stoday)}"
    footnote2=text_lang(footnote2cn,footnote2en)
    
    plt.xlabel('\n'+footnote1+'; '+footnote2)
    plt.xticks(rotation=90); plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor(facecolor)
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_correlate(pf_info)
#==============================================================================
if __name__=='__main__':
    
    portfolio_covar(pf_info)
    
def portfolio_covar2(pf_info,facecolor='papayawhip'):
    """
    功能：计算投资组合成份股之间的协方差
    """
    portfolio,thedate,member_prices_original,_,_,_=pf_info
    pname=portfolio_name(portfolio)
    
    member_prices=member_prices_original.copy()
    # 计算日收益率：(当日价格/前一日价格) - 1
    stock_return = (member_prices / member_prices.shift(1)) - 1    
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))

    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵，252个交易日
    cov_mat_annual = cov_mat * 252
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(cov_mat_annual,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 13})
    plt.title(pname+text_lang(": 成份证券收益率之间的协方差","Covariance Among Member Security\'s Returns")+'\n')
    plt.ylabel(text_lang("成份证券","Member Security"))
    
    footnote1cn="观察期间: "+hstart+'至'+hend
    footnote1en=f"Period: from {hstart} to {hend}"
    footnote1=text_lang(footnote1cn,footnote1en)
    
    import datetime as dt; stoday=dt.date.today()    
    footnote2cn="数据来源：Sina/EM/stooq，"+str(stoday)
    footnote2en=f"Data source: Sina/EM/Stooq, {str(stoday)}"
    footnote2=text_lang(footnote2cn,footnote2en)
    
    plt.xlabel('\n'+footnote1+'; '+footnote2)
    
    plt.xticks(rotation=90)
    plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor(facecolor)
    plt.show()

    return 


#==============================================================================
def portfolio_expectation_universal1(pname,portfolio_returns,portfolio_weights,member_prices, \
                                    ticker_type,printout=True):
    """
    功能：计算给定成份股收益率和持股权重的投资组合年均收益率和标准差
    输入：投资组合名称，成份股历史收益率数据表，投资组合权重series
    输出：年化收益率和标准差
    用途：求出MSR、GMV等持仓策略后计算投资组合的年化收益率和标准差
    """
    import numpy as np
    
    #观察期
    hstart0=portfolio_returns.index[0]
    #hstart=str(hstart0.date())
    hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=portfolio_returns.index[-1]
    #hend=str(hend0.date())
    hend=str(hend0.strftime("%Y-%m-%d"))
    tickerlist=list(member_prices)
    
    # 计算持有天数
    days_held = (hend0 - hstart0).days
    trading_days=252
    
    #合成投资组合的历史收益率：portfolio_returns为投资组合的持有期收益率
    preturns=portfolio_returns.copy() #避免改变输入的数据

    total_return = preturns.iloc[-1]  # 最后一个数据点是整个期间的总持有期收益率
    
    # 计算年化收益率 = (1 + 总持有期收益率)^(365/持有天数) - 1
    annual_return = (1 + total_return) ** (trading_days / days_held) - 1  
    
    #计算年化标准差
    # 计算日收益率：从累计持有期收益率推导
    # 日收益率 = (当日累计收益率 + 1) / (前一日累计收益率 + 1) - 1
    daily_returns = (1 + preturns) / (1 + preturns.shift(1)) - 1
    # 移除第一个NaN值（因为没有前一天的数据）
    daily_returns = daily_returns.dropna()
    # 计算日收益率的标准差，然后年化
    # 年化标准差 = 日标准差 * sqrt(252)，252是一年的交易日数量
    daily_std = daily_returns.std()
    annual_std = daily_std * np.sqrt(trading_days)  # 使用252个交易日进行年化
    
    #计算一手投资组合的价格，最小持股份额的股票需要100股
    import numpy as np
    min_weight=np.min(portfolio_weights)
    # 将最少持股的股票份额转换为1
    portfolio_weights_1=portfolio_weights / min_weight * 1
    portfolio_values=member_prices.mul(portfolio_weights_1,axis=1).sum(axis=1)
    portfolio_value_thedate=portfolio_values[-1:].values[0]

    if printout:
        lang=check_language()
        import datetime as dt; stoday=dt.date.today()    
        if lang == 'Chinese':
            print("\n  ======= 投资组合的收益与风险 =======")
            print("  投资组合:",pname)
            print("  分析日期:",str(hend))
        # 投资组合中即使持股比例最低的股票每次交易最少也需要1手（100股）
            print("  1手组合单位价值:","约"+str(round(portfolio_value_thedate/10000*100,2))+"万")
            print("  观察期间:",hstart+'至'+hend)
            print("  年化收益率:",round(annual_return,4))
            print("  年化标准差:",round(annual_std,4))
            print("  ***投资组合持仓策略***")
            print_tickerlist_sharelist(tickerlist,portfolio_weights,leading_blanks=4,ticker_type=ticker_type)
           
            print("  *数据来源：Sina/EM/Stooq/Yahoo，"+str(stoday)+"统计")
        else:
            print("\n  ======= Investment Portfolio: Return and Risk =======")
            print("  Investment portfolio:",pname)
            print("  Date of analysis:",str(hend))
            print("  Value of portfolio:","about "+str(round(portfolio_value_thedate/1000,2))+"K/portfolio unit")
            print("  Period of sample:",hstart+' to '+hend)
            print("  Annualized return:",round(annual_return,4))
            print("  Annualized std of return:",round(annual_std,4))
            print("  ***Portfolio Constructing Strategy***")
            print_tickerlist_sharelist(tickerlist,portfolio_weights,4)
           
            print("  *Data source: Sina/EM/Stooq/Yahoo, "+str(stoday))

    return pname,annual_return,annual_std

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')

    [[portfolio,thedate,member_returns,_,_],[_,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    
    portfolio_expectation2(pname,member_returns, portfolio_weights)


#==============================================================================
if __name__=='__main__':
    portfolio_annual_return_std(member_prices,portfolio_weights)


def portfolio_annual_return_std(member_prices_original,portfolio_weights_original):
    """计算投资组合的年化收益率和年化标准差
    输入参数：
        member_prices_original：数据框，投资组合各个成分证券的历史价格，可为收盘价或调整收盘价
        portfolio_weights_original：建议为np.array，各个成分证券在投资组合中的股数比例
            其个数应该与member_prices_original的成分证券个数一致
    输出：投资组合的年化收益率，年化收益率标准差，日收益率历史序列，不带百分号
    """
    
    # 不破坏原始数据
    member_prices=member_prices_original.copy()
    portfolio_weights=portfolio_weights_original.copy()

    # 在金融计算中，年化收益率使用 365 日而年化标准差使用 252 日
    trading_days=252
    
    import numpy as np
    if isinstance(portfolio_weights,list):
        portfolio_weights = np.array(portfolio_weights)
    
    # 合成投资组合价值
    portfolio_value = member_prices.dot(portfolio_weights)
    # 计算投资组合的日收益率
    dreturn=portfolio_value / portfolio_value.shift(1) - 1
    dreturn=dreturn.dropna()
    
    # 计算年化收益率
    annual_return = (1 + dreturn).prod()**(trading_days/len(dreturn)) - 1
    
    #计算年化标准差
    annual_std = dreturn.std() * np.sqrt(trading_days)  # 使用252个交易日进行年化    

    return annual_return,annual_std,dreturn


#==============================================================================

def portfolio_ranks2(portfolio_info_list,pname,facecolor='papayawhip',printout=True):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序，中文/英文
    """
    import pandas as pd
    
    #临时保存，避免影响原值
    pr=portfolio_info_list.copy()
    
    #统一核定小数位数
    ndecimals=2
    
    #以pname组合作为基准
    for l in portfolio_info_list:
        if l[0] == pname:
            annual_return_pname = l[1]*100
            annual_std_pname = l[2]*100
    
    prr=pd.DataFrame(columns=["名称","年化收益率%","收益率变化","年化标准差%","标准差变化","收益率/标准差"])    
    for l in portfolio_info_list:
        
        #年化收益率
        annual_return = l[1]*100
        return_chg=round((annual_return - annual_return_pname),ndecimals)
        
        #收益率变化    
        if return_chg==0:
            return_chg_str=text_lang("基准","Benchmark")
        elif return_chg > 0:
            return_chg_str='+'+str(return_chg)
        else:
            return_chg_str='-'+str(-return_chg)
    
        #年化标准差
        annual_std = l[2]*100
        std_chg=round((annual_std - annual_std_pname),ndecimals)
        
        sharpe_ratio=round((annual_return) / annual_std,ndecimals+2)
        
        #标准差变化
        if std_chg==0:
            std_chg_str=text_lang("基准","Benchmark")
        elif std_chg > 0:
            std_chg_str='+'+str(std_chg)
        else:
            std_chg_str='-'+str(-std_chg)
        
        row=pd.Series({"名称":l[0],"年化收益率%":annual_return, \
                       "收益率变化":return_chg_str, \
                       "年化标准差%":annual_std,"标准差变化":std_chg_str,"收益率/标准差":sharpe_ratio})
        try:
            prr=prr.append(row,ignore_index=True)
        except:
            prr=prr._append(row,ignore_index=True)
    
    #先按风险降序排名，高者排前面
    prr.sort_values(by="年化标准差%",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['风险排名']=prr.index+1
    
    #再按收益降序排名，高者排前面
    prr.sort_values(by="年化收益率%",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['收益排名']=prr.index+1    
    
    #prr2=prr[["名称","收益排名","风险排名","年化收益率","年化标准差","收益率变化","标准差变化","收益/风险"]]
    prr2=prr[["名称","收益排名","年化收益率%","收益率变化", \
              "风险排名","年化标准差%","标准差变化", \
                  "收益率/标准差"]]
    prr2.sort_values(by="年化收益率%",ascending=False,inplace=True)
    #prr2.reset_index(inplace=True)
    
    #打印
    #一点改造
    print('') #空一行
    prr2.index=prr2.index + 1
    prr2.rename(columns={'名称':'投资组合名称/策略'},inplace=True)
    for c in list(prr2):
        try:
            prr2[c]=prr2[c].apply(lambda x: str(round(x,4)) if isinstance(x,float) else str(x))
        except: pass
    
    titletxt=text_lang('投资组合策略排名：平衡收益与风险','Investment Portfolio Strategies: Performance, Balancing Return and Risk')
    
    prr2.rename(columns={"投资组合名称/策略":text_lang("投资组合名称/策略","Strategy"), \
                         "收益排名":text_lang("收益排名","Return#"), \
                         "年化收益率%":text_lang("年化收益率%","pa Return%"), \
                         "收益率变化":text_lang("收益率变化","Return%+/-"), \
                         "风险排名":text_lang("风险排名","Risk#"), \
                         "年化标准差%":text_lang("年化标准差%","pa Std%"), \
                         "标准差变化":text_lang("标准差变化","Std%+/-"), \
                         "收益率/标准差":text_lang("收益/风险性价比","Return/Std")}, \
                inplace=True)
    
    #重新排名：相同的值赋予相同的序号
    prr2[text_lang("年化收益率%","pa Return%")]=prr2[text_lang("年化收益率%","pa Return%")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("收益排名","Return#")]=prr2[text_lang("年化收益率%","pa Return%")].rank(ascending=False,method='dense')
    prr2[text_lang("收益排名","Return#")]=prr2[text_lang("收益排名","Return#")].apply(lambda x: int(x) if not pd.isna(x) else '-')
    
    prr2[text_lang("年化标准差%","pa Std%")]=prr2[text_lang("年化标准差%","pa Std%")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("风险排名","Risk#")]=prr2[text_lang("年化标准差%","pa Std%")].rank(ascending=False,method='dense')
    prr2[text_lang("风险排名","Risk#")]=prr2[text_lang("风险排名","Risk#")].apply(lambda x: int(x) if not pd.isna(x) else '-')
    
    prr2[text_lang("收益/风险性价比","Return/Std")]=prr2[text_lang("收益/风险性价比","Return/Std")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("性价比排名","Ret/Std#")]=prr2[text_lang("收益/风险性价比","Return/Std")].rank(ascending=False,method='dense')
    prr2[text_lang("性价比排名","Ret/Std#")]=prr2[text_lang("性价比排名","Ret/Std#")].apply(lambda x: int(x) if not pd.isna(x) else '-')
    
    if printout:
        df_display_CSS(prr2,titletxt=titletxt,footnote='',facecolor=facecolor,decimals=ndecimals, \
                           first_col_align='left',second_col_align='center', \
                           last_col_align='center',other_col_align='center', \
                           titile_font_size='15px',heading_font_size='13px', \
                           data_font_size='13px')
    
    return prr2   

if __name__=='__main__':
    portfolio_ranks2(portfolio_returns,pname)




#==============================================================================

import numpy as np
import pandas as pd
import statsmodels.api as sm

def performance_metrics(dreturn, rf_daily, mreturn):
    """
    计算股票的各类绩效指标
    
    参数:
    dreturn: pandas.Series, 股票日收益率
    rf_daily: float 或 pandas.Series, 日无风险利率
    mreturn: pandas.Series, 市场日收益率
    trading_days: int, 一年交易日数，默认252
    
    返回:
    dict: 包含夏普比率、索提诺比率、阿尔法、特雷诺比率、年化收益率、年化标准差
    """
    # 对齐索引
    data = pd.concat([dreturn, mreturn], axis=1, join="inner").dropna()
    dreturn = data.iloc[:,0]
    mreturn = data.iloc[:,1]
    
    # 无风险利率处理
    if isinstance(rf_daily, (int, float)):
        rf = pd.Series(rf_daily, index=dreturn.index)
    else:
        rf = rf_daily.loc[dreturn.index]
    
    trading_days=252
    # 超额收益
    excess_return = dreturn - rf
    excess_market = mreturn - rf
    
    # 年化收益率
    ann_return = (1 + dreturn).prod()**(trading_days/len(dreturn)) - 1
    
    # 年化标准差
    ann_std = dreturn.std() * np.sqrt(trading_days)
    
    # 夏普比率(年化)
    sharpe_ratio = (excess_return.mean() / dreturn.std()) * np.sqrt(trading_days)
    
    # 索提诺比率（只考虑下行波动）
    downside_std = dreturn[dreturn < 0].std() * np.sqrt(trading_days)
    sortino_ratio = (excess_return.mean() * trading_days) / downside_std if downside_std != 0 else np.nan
    
    # 回归计算Alpha和Beta
    X = sm.add_constant(excess_market)
    model = sm.OLS(excess_return, X).fit()
    alpha_daily, beta = model.params
    # 年化Alpha
    alpha_ann = alpha_daily * trading_days
    
    # 特雷诺比率（年化）
    treynor_ratio = (excess_return.mean() * trading_days) / beta if beta != 0 else np.nan
    
    metrics={
        "annual_return": ann_return,
        "annual_std": ann_std,
        "sharpe": sharpe_ratio,
        "sortino": sortino_ratio,
        "alpha": alpha_ann,
        "treynor": treynor_ratio
    }

    return metrics


#==============================================================================
if __name__=='__main__':
    
    # 定义投资组合
    portfolio,RF=portfolio_define(
        name="银行概念基金1号",
        market='CN',market_index='000001.SS',
        members={
            '601939.SS':.3,#中国建设银行
            '600000.SS':.2, #浦东发展银行
            '601998.SS':.1,#中信银行
            '601229.SS':.4,#上海银行
            }
        )    
    
    # 建立投资组合
    pf_info=portfolio_build(portfolio,
                            thedate="2025-7-1",
                            pastyears=1,indicator="Adj Close",
                            graph=False,printout=False)

    # 建立可行集
    fs_info=portfolio_feasible(pf_info,simulation=2000)
    
    # 寻找有效边界
    es_info=portfolio_efficient(fs_info)
    
    # 优化投资组合
    optimized_result=portfolio_optimize(es_info,RF=RF)
    
    
def portfolio_optimize2(es_info, \
                       ratio=['treynor','sharpe','sortino','alpha'], \
                       RF=0, \
                       graph=True, \
                       facecolor='papayawhip'):
    """
    功能：集成式投资组合优化策略
    注意：实验发现RF较小时对于结果的影响极其微小难以观察，默认设为不使用无风险利率调整收益
    但RF较大时对于结果的影响明显变大，已经不能忽略！
    若可行集形状不佳，优先尝试：减少成分股数量至3~4个，pastyears=3，simulation=50000。
    simulation数值过大时将导致速度太慢。
    """   
    # 防止原始数据被修改
    pf_info_original,RandomPortfolios_original,efficient_indices_original,efficient_frontier_coordinates=es_info
    
    pf_info=pf_info_original.copy()
    portfolio,thedate,member_prices,market,portfolio_returns,portfolio_info_list=pf_info
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    base_name=portfolio_name(portfolio)
    ntickers=len(tickerlist)
    
    RandomPortfolios=RandomPortfolios_original.copy()
    efficient_indices=efficient_indices_original.copy()
    
    rf_daily=RF/365
    
    _,_,_,market,_,_=pf_info
    mreturn=market['Close'] / market['Close'].shift(1) - 1
    mreturn=mreturn.dropna()
     
    _,_,stocklist,_,_=decompose_portfolio(portfolio)
    ntickers=len(stocklist)
    
    # 记录有效边界上每个投资组合的编号、成分股构成、年化收益率、年化标准差、夏普比率、索提诺比率、阿尔法指标和特雷诺比率
    metrics_indices={}
    for ei in efficient_indices:
        # 第ei个投资组合的价值序列
        dreturn=RandomPortfolios.iloc[ei]['dreturn'].copy()
        sharelist=RandomPortfolios.iloc[ei].head(ntickers).copy()
        metrics=performance_metrics(dreturn, rf_daily, mreturn)
        
        metrics_indices[ei]=[sharelist,metrics]
        
    # RAR比率最高的投资组合
    max_rar_indices={}
    for r in ratio:
        r_value=-999; r_ei=-1
        for ei in efficient_indices:
            temp_value=metrics_indices[ei][1][r]
            if temp_value > r_value: 
                r_value=temp_value
                r_ei=ei
                
        max_rar_indices[r]=[r_ei,r_value]
    
    # 收益率最高的投资组合
    max_ret_indices=[]
    ret_value=-999; std_value=-999; ret_ei=-1
    for ei in efficient_indices:
        temp_value=metrics_indices[ei][1]['annual_return']
        if temp_value > ret_value:
            ret_value=temp_value
            std_value=metrics_indices[ei][1]['annual_std']
            ret_ei=ei
    max_ret_indices=[ret_ei,ret_value,std_value]
    
    # 风险最低且收益率为正的投资组合         
    min_std_indices=[]
    ret_value=-999; std_value=999; ret_ei=-1
    for ei in efficient_indices:
        temp_std=metrics_indices[ei][1]['annual_std']
        temp_ret=metrics_indices[ei][1]['annual_return']
        if (temp_std < std_value) and (temp_ret > 0):
            std_value=temp_std
            ret_value=temp_ret
            ret_ei=ei
    min_std_indices=[ret_ei,ret_value,std_value]

    # 打印各个投资组合==========================================================
    # 最高RAR组合
    for pname in ratio:
        ei,pvalue=max_rar_indices[pname]
        portfolio_weights,metrics=metrics_indices[ei]
        annual_return=metrics['annual_return']
        annual_std=metrics['annual_std']
        
        portfolio_rar=portfolio_expectation_universal2(ei,pname,pvalue, \
                        annual_return,annual_std,member_prices,portfolio_weights, \
                                        ticker_type,printout=True)
        portfolio_info_list=portfolio_info_list+[portfolio_rar]
    
    pname='hiret'
    ei=max_ret_indices[0]
    portfolio_weights,metrics=metrics_indices[ei]
    pvalue=max_ret_indices[1]
    annual_return=max_ret_indices[1]
    annual_std=max_ret_indices[2]
    portfolio_hiret=portfolio_expectation_universal2(ei,pname,pvalue, \
                    annual_return,annual_std,member_prices,portfolio_weights, \
                                    ticker_type,printout=True)
    portfolio_info_list=portfolio_info_list+[portfolio_hiret]
        
    pname='lorisk'
    ei=min_std_indices[0]
    portfolio_weights,metrics=metrics_indices[ei]
    pvalue=min_std_indices[2]
    annual_return=min_std_indices[1]
    annual_std=min_std_indices[2]
    portfolio_lorisk=portfolio_expectation_universal2(ei,pname,pvalue, \
                    annual_return,annual_std,member_prices,portfolio_weights, \
                                    ticker_type,printout=True)
    portfolio_info_list=portfolio_info_list+[portfolio_lorisk]

    #打印现有投资组合策略的排名
    prr2=portfolio_ranks2(portfolio_info_list,base_name,facecolor=facecolor,printout=True)

    optimized_result=[pf_info,RandomPortfolios,efficient_frontier_coordinates,portfolio_info_list]

    return optimized_result

#==============================================================================
if __name__=='__main__':
    
    # 定义投资组合
    portfolio,RF=portfolio_define(
        name="银行概念基金1号",
        market='CN',market_index='000001.SS',
        members={
            '601939.SS':.3,#中国建设银行
            '600000.SS':.2, #浦东发展银行
            '601998.SS':.1,#中信银行
            '601229.SS':.4,#上海银行
            }
        )    
    
    # 建立投资组合
    pf_info=portfolio_build(portfolio,
                            thedate="2025-7-1",
                            pastyears=1,indicator="Adj Close",
                            graph=False,printout=False)

    # 建立可行集
    fs_info=portfolio_feasible(pf_info,simulation=2000)
    
    # 寻找有效边界
    es_info=portfolio_efficient(fs_info)
    
    # 优化投资组合
    optimized_result=portfolio_optimize(es_info,RF=RF)
    
    portfolio_optimize_plot(optimized_result)
    
def portfolio_optimize_plot(optimized_result,
                            points=['MSR','MSO','MAR','MTR','HiRet','LoRisk'],
                            facecolor='papayawhip'):
    """在有效边界上绘制投资组合的优化结果
    
    """
    pf_info,RandomPortfolios,efficient_frontier_coordinates,portfolio_info_list=optimized_result
    
    portfolio,thedate,_,_,_,_=pf_info
    base_name=portfolio_name(portfolio)
    
    titletxt_cn=f"投资组合优化策略示意图：{base_name}，@{thedate}"
    titletxt_en=f"Portfolio Optimization Strategy: {base_name}, @{thedate}"
    plt.title(text_lang(titletxt_cn,titletxt_en)+'\n',fontsize=title_txt_size)
    
    plt.ylabel(text_lang("年化收益率","Annualized Return"),fontsize=ylabel_txt_size)
    plt.xlabel(text_lang("年化收益率标准差","Annualized Std"),fontsize=xlabel_txt_size)
    
    # 绘制可行集散点图
    pf_ratio = np.array(RandomPortfolios['annual_return'] / RandomPortfolios['annual_std'])
    pf_returns = np.array(RandomPortfolios['annual_return'])
    pf_volatilities = np.array(RandomPortfolios['annual_std'])
    
    plt.scatter(pf_volatilities,pf_returns,c=pf_ratio,cmap='RdYlGn',edgecolors='black',marker='o')     
    
    
    # 绘制有效边界
    eff_x, eff_y=efficient_frontier_coordinates
    plt.plot(eff_x, eff_y, 'r--', label=text_lang("有效边界","Efficient Frontier"), lw=3, alpha=0.5)
    #plt.scatter(eff_x,eff_y,c='k',s=200,alpha=0.5)    
    
    # 绘制优化点：适用最多6个端点情形
    marker_list=['D','s','o','*','v','^','>','<']
    marker_color_list=['magenta','g','b','y','m','c','k']
    marker_size=200
    
    for pi in portfolio_info_list:
        pi_name,pi_y,pi_x=pi[0],pi[1],pi[2]
        for pts in points:
            pos=points.index(pts)
            if pts in pi[0]:
                plt.scatter(pi_x,pi_y,marker=marker_list[pos],label=pts, \
                            s=marker_size,c=marker_color_list[pos], 
                            edgecolors='black',linewidths=2,
                            alpha=0.5,
                            )
                
    plt.legend(loc='best')
    plt.gca().set_facecolor(facecolor)
    plt.show(); plt.close()        
    
    
#==============================================================================
def portfolio_expectation_universal2(ei,pname,pvalue,annual_return,annual_std, \
                                     member_prices,portfolio_weights, \
                                     ticker_type,printout=True):
    """
    功能：计算给定成份股收益率和持股权重的投资组合年均收益率和标准差
    输入：投资组合名称，成份股历史收益率数据表，投资组合权重series
    输出：年化收益率和标准差
    用途：求出MSR、GMV等持仓策略后计算投资组合的年化收益率和标准差
    """
    import numpy as np
    
    #观察期
    hstart0=member_prices.index[0]
    #hstart=str(hstart0.date())
    hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=member_prices.index[-1]
    #hend=str(hend0.date())
    hend=str(hend0.strftime("%Y-%m-%d"))
    tickerlist=list(member_prices)
    
    #计算一手投资组合的价格，最小持股份额的股票需要100股
    import numpy as np
    min_weight=np.min(portfolio_weights)
    # 将最少持股的股票份额转换为1
    portfolio_weights_1=portfolio_weights / min_weight * 1
    portfolio_weights_1.index = portfolio_weights_1.index.str.replace("_weight", "", regex=False)

    aligned_prices=member_prices[portfolio_weights_1.index]
    portfolio_values=(aligned_prices * portfolio_weights_1).sum(axis=1)
    portfolio_value_thedate=portfolio_values[-1:].values[0]
    
    if pname == 'sharpe':
        pname=text_lang("MSR(最高夏普比率组合)","MSR(Maximum Sharpe Ratio Portfolio)")
        pvalue_name=text_lang("夏普比率","Sharpe ratio")
    elif pname == 'sortino':
        pname=text_lang("MSO(最高索替诺比率组合)","MSO(Maximum Sortino Ratio Portfolio)")
        pvalue_name=text_lang("索替诺比率","Sortino ratio")
    elif pname == 'treynor':
        pname=text_lang("MTR(最高特雷诺比率组合)","MTR(Maximum Treynor Ratio Portfolio)")
        pvalue_name=text_lang("特雷诺比率","Treynor ratio")
    elif pname == 'alpha':
        pname=text_lang("MAR(最高阿尔法指标组合)","MAR(Maximum Alpha Index Portfolio)")
        pvalue_name=text_lang("阿尔法指标","Alpha index")
    elif pname == 'hiret':
        pname=text_lang("HiRet(最高收益率组合)","HiRet(Maximum Rate of Return Portfolio)")
        pvalue_name=''
    elif pname == 'lorisk':
        pname=text_lang("LoRisk(收益率为正的最小风险组合)","LoRisk(Minimum Rate of Risk Portfolio)")
        pvalue_name=''
    else:
        print(f"  Sorry, no idea on what sort of portfolio to print out")
        pass


    if printout:
        lang=check_language()
        import datetime as dt; stoday=dt.date.today()    
        if lang == 'Chinese':
            print("\n  ======= 投资组合的收益与风险 =======")
            print("  投资组合:",pname)
            print("  可行集投资组合编号:",ei)
            if pvalue_name != '':
                print(f"  {pvalue_name}：{srounds(pvalue)}")
            print("  分析日期:",str(hend))
        # 投资组合中即使持股比例最低的股票每次交易最少也需要1手（100股）
            print("  1手组合单位价值:","约"+str(round(portfolio_value_thedate/10000*100,2))+"万")
            print("  观察期间:",hstart+'至'+hend)
            print("  年化收益率:",round(annual_return,4))
            print("  年化标准差:",round(annual_std,4))
            print("  ***投资组合持仓策略***")
            print_tickerlist_sharelist(tickerlist,portfolio_weights,leading_blanks=4,ticker_type=ticker_type)
           
            print("  *数据来源：Sina/EM/Stooq/Yahoo，"+str(stoday)+"统计")
        else:
            print("\n  ======= Investment Portfolio: Return and Risk =======")
            print("  Investment portfolio:",pname)
            print("  Feasible set portfolio no.:",ei)
            if pvalue_name != '':
                print(f"  {pvalue_name}: {srounds(pvalue)}")

            print("  Date of analysis:",str(hend))
            print("  Value of portfolio:","about "+str(round(portfolio_value_thedate/1000,2))+"K/portfolio unit")
            print("  Period of sample:",hstart+' to '+hend)
            print("  Annualized return:",round(annual_return,4))
            print("  Annualized std of return:",round(annual_std,4))
            print("  ***Portfolio Constructing Strategy***")
            print_tickerlist_sharelist(tickerlist,portfolio_weights,4)
           
            print("  *Data source: Sina/EM/Stooq/Yahoo, "+str(stoday))

    return pname,annual_return,annual_std


#==============================================================================
if __name__ =="__main__":
    
    portfolio,RF=portfolio_define(
        name="银行概念基金1号",
        market='CN',market_index='000001.SS',
        members={
            '601939.SS':.3,#中国建设银行
            '600000.SS':.2, #浦东发展银行
            '601998.SS':.1,#中信银行
            '601229.SS':.4,#上海银行
            }
        )

    indicator='Adj Close'
    thedate='2025-7-1'
    pastyears=1    
    
    pf_info=portfolio_build(portfolio,thedate,pastyears,graph=False,printout=False)
    
    fs_info=portfolio_feasible(pf_info,simulation=2000)
    
    
    
def portfolio_feasible2(pf_info,simulation=2000,facecolor='papayawhip', \
                       DEBUG=False,MORE_DETAIL=False):
    """
    功能：绘制投资组合的可行集散点图，仅供教学演示，无实际用途
    """
    
    portfolio,thedate,member_prices_original,_,_,_=pf_info
    member_prices=member_prices_original.copy()
    pname=portfolio_name(portfolio)
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #获得成份股个数
    numstocks=len(tickerlist)
    
    #取出观察期
    hstart0=member_prices.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=member_prices.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、投资组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    
    # 记录每个随机组合的历史日收益率，便于后续RaR对比处理
    random_pdret={}
    
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)

    # 循环模拟n次随机的投资组合
    print(f"  Simulating {simulation} feasible sets of portfolios ...")    
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化收益率
        annual_return,annual_std,daily_returns=portfolio_annual_return_std(member_prices,random_weight)
        
        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_std
        
        random_pdret.update({i:daily_returns})
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    import pandas as pd
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    """
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Returns', 'Volatility']
    """
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['annual_return', 'annual_std']
    
    
    # 将投资组合的日收益率合并入
    RandomPortfolios['dreturn']=RandomPortfolios.index.map(random_pdret)

    # 绘制散点图
    pf_ratio = np.array(RandomPortfolios['annual_return'] / RandomPortfolios['annual_std'])
    pf_returns = np.array(RandomPortfolios['annual_return'])
    pf_volatilities = np.array(RandomPortfolios['annual_std'])
    
    # plt.scatter(x,y,...)
    plt.scatter(pf_volatilities,pf_returns,c=pf_ratio,cmap='RdYlGn',edgecolors='black',marker='o') 
    
    # 空一行
    print('')
    import datetime as dt; stoday=dt.date.today()
    lang = check_language()
    if lang == 'Chinese':  
        if pname == '': pname='投资组合'
        
        plt.colorbar(label='收益率/标准差')
        
        titletxt0=": 马科维茨可行集"
            
        plt.title(pname+titletxt0+'\n',fontsize=title_txt_size)
        plt.ylabel("年化收益率",fontsize=ylabel_txt_size)
        
        footnote1="年化收益率标准差-->"
        footnote2="\n\n基于给定的成份证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="; 数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        titletxt0=": Markowitz Feasible Set"
            
        plt.colorbar(label='Return/Std')
        plt.title(pname+titletxt0+'\n',fontsize=title_txt_size)
        plt.ylabel("Annualized Return",fontsize=ylabel_txt_size)
        
        footnote1="Annualized Std -->\n\n"
        footnote2="Built "+str(simulation)+" portfolios of given securities\n"
        footnote3="Period of sample: "+hstart+" to "+hend
        footnote4="; Data source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel('\n'+footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    plt.gca().set_facecolor(facecolor)
    #plt.legend(loc='best')
    plt.show()

    fs_info=[pf_info,RandomPortfolios]
    return fs_info


#==============================================================================
if __name__ =="__main__":
    portfolio,RF=portfolio_define(
        name="银行概念基金1号",
        market='CN',market_index='000001.SS',
        members={
            '601939.SS':.3,#中国建设银行
            '600000.SS':.2, #浦东发展银行
            '601998.SS':.1,#中信银行
            '601229.SS':.4,#上海银行
            }
        )

    indicator='Adj Close'
    thedate='2025-7-1'
    pastyears=1    
    
    pf_info=portfolio_build2(portfolio,thedate,pastyears,graph=False,printout=False)
    
    fs_info=portfolio_feasible2(pf_info,simulation=2000)
    
    es_info=portfolio_efficient2(fs_info)
    
    
def portfolio_efficient2(fs_info,frontier='efficient', \
                        tol=0.0000, \
                        facecolor='papayawhip', \
                        DEBUG=False,MORE_DETAIL=False, \
                        ):
    """
    功能：绘制投资组合的有效边界和无效边界，并输出有效边界投资组合，最新版！！！
    """
    pf_info_original,RandomPortfolios_original=fs_info
    pf_info=pf_info_original.copy()
    RandomPortfolios=RandomPortfolios_original.copy()
    simulation=len(RandomPortfolios)
    
    
    efficient_set=True
    convex_hull=True
    
    portfolio,thedate,member_prices_original,_,_,_=pf_info
    member_prices=member_prices_original.copy()
    pname=portfolio_name(portfolio)
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #获得成份股个数
    numstocks=len(tickerlist)
    
    #取出观察期
    hstart0=member_prices.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=member_prices.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    # 绘制散点图
    pf_ratio = np.array(RandomPortfolios['annual_return'] / RandomPortfolios['annual_std'])
    pf_returns = np.array(RandomPortfolios['annual_return'])
    pf_volatilities = np.array(RandomPortfolios['annual_std'])
    
    plt.scatter(pf_volatilities,pf_returns,c=pf_ratio,cmap='RdYlGn',edgecolors='black',marker='o') 
    
    # 绘制散点图轮廓线凸包（convex hull）=======================================
    efficient_indices=[]
    if convex_hull:
        print("  Calculating convex hull ...")
        from scipy.spatial import ConvexHull
        
        # 构造散点对的列表（保持最小改动）
        points=[]
        for x, y in zip(pf_volatilities, pf_returns):
            print_progress_percent2(x, pf_volatilities, steps=10, leading_blanks=4)
            points.append([x, y])
        points = np.array(points)
        
        # 计算凸包
        hull = ConvexHull(points)

        # 提取凸包顶点并按 x 升序
        verts = hull.vertices
        hull_pts = points[verts]
        order = np.argsort(hull_pts[:,0])
        hull_pts = hull_pts[order]

        # 找最小方差点和最高收益点（界定上包络范围）
        minvar_pos = np.lexsort((-hull_pts[:,1], hull_pts[:,0]))[0]
        maxret_pos = np.lexsort((hull_pts[:,0], -hull_pts[:,1]))[0]
        x_minvar, y_minvar = hull_pts[minvar_pos]
        x_maxret, y_maxret = hull_pts[maxret_pos]

        # 提取上包络（有效边界）
        eps = 1e-10
        current_max_y = -np.inf
        eff_x=[]; eff_y=[]
        for x,y in hull_pts:
            if x + eps < x_minvar or x - eps > x_maxret:
                continue
            if y >= current_max_y - eps:
                current_max_y = y
                eff_x.append(x); eff_y.append(y)
                # 将上包络点映射回 RandomPortfolios 的索引（严格/带容差）
                idx = RandomPortfolios[(np.isclose(RandomPortfolios['annual_std'], x, atol=1e-12)) &
                                       (np.isclose(RandomPortfolios['annual_return'], y, atol=1e-12))].index.tolist()
                efficient_indices.extend(idx)

        # 绘制有效边界
        if frontier.lower() in ['both','efficient'] and len(eff_x) > 1:
            plt.plot(eff_x, eff_y, 'r--', label=text_lang("有效边界","Efficient Frontier"), lw=3, alpha=0.5)

        # 容差范围内的点也算作有效边界（数量更多），tol=0为严格模式
        if tol > 0 and len(eff_x) > 1:
            # 使用线性插值估计每个 x 的上包络 y
            for i, (x,y) in enumerate(zip(pf_volatilities, pf_returns)):
                # 限定在上包络 x 范围内才计算插值
                if x + eps < min(eff_x) or x - eps > max(eff_x):
                    continue
                y_env = np.interp(x, eff_x, eff_y)
                if y >= y_env - tol:
                    efficient_indices.append(RandomPortfolios.index[i])

        # 绘制无效边界（凸包剩余边）
        if frontier.lower() in ['both','inefficient']:
            # 为判断端点是否在有效边界，做一个便捷检查函数
            def on_eff(xp, yp, band=max(tol, 1e-12)):
                # 在上包络范围内才认为可能是有效点
                if xp + eps < min(eff_x) or xp - eps > max(eff_x):
                    return False
                y_env = np.interp(xp, eff_x, eff_y)
                return yp >= y_env - band

            firsttime_inefficient = True
            for s0, s1 in hull.simplices:
                x0, y0 = points[s0]
                x1_, y1_ = points[s1]
                # 如果两端都在有效边界（或容差带内），跳过；否则绘制为无效边界
                if on_eff(x0, y0) and on_eff(x1_, y1_):
                    continue
                # 只绘制凸包线段
                if firsttime_inefficient:
                    plt.plot([x0, x1_], [y0, y1_], 'k-.',
                             label=text_lang("无效边界","Inefficient Frontier"),
                             alpha=0.5)
                    firsttime_inefficient = False
                else:
                    plt.plot([x0, x1_], [y0, y1_], 'k-.', alpha=0.5)
    else:
        pass
    # 结束处理凸包==============================================================
    
    # 空一行
    print('')
    import datetime as dt; stoday=dt.date.today()
    lang = check_language()
    if lang == 'Chinese':  
        if pname == '': pname='投资组合'
        
        plt.colorbar(label='收益率/标准差')
        
        if efficient_set:
            if frontier == 'efficient':
                titletxt0=": 马科维茨有效集(有效边界)"
            elif frontier == 'inefficient':
                titletxt0=": 马科维茨无效集(无效边界)"
            elif frontier == 'both':
                titletxt0=": 马科维茨有效边界与无效边界"
            else:
                titletxt0=": 马科维茨可行集"
        else:
            titletxt0=": 马科维茨可行集"
            
        plt.title(pname+titletxt0+'\n',fontsize=title_txt_size)
        plt.ylabel("年化收益率",fontsize=ylabel_txt_size)
        
        footnote1="年化收益率标准差-->"
        footnote2="\n\n基于给定的成份证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="\n数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        if efficient_set:
            if frontier == 'efficient':
                titletxt0=": Markowitz Efficient Set (Efficient Frontier)"
            elif frontier == 'inefficient':
                titletxt0=": Markowitz Inefficient Set (Inefficient Frontier)"
            elif frontier == 'both':
                titletxt0=": Markowitz Efficient & Inefficient Frontier"
            else:
                titletxt0=": Markowitz Feasible Set"
        else:
            titletxt0=": Markowitz Feasible Set"
            
        plt.colorbar(label='Return/Std')
        plt.title(pname+titletxt0+'\n',fontsize=title_txt_size)
        plt.ylabel("Annualized Return",fontsize=ylabel_txt_size)
        
        footnote1="Annualized Std -->\n\n"
        footnote2="Built "+str(simulation)+" portfolios of given securities\n"
        footnote3="Period of sample: "+hstart+" to "+hend
        footnote4="\nData source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel('\n'+footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    plt.gca().set_facecolor(facecolor)
    if efficient_set:
        plt.legend(loc='best')
    plt.show()

    # 去重并返回有效边界投资组合索引
    efficient_indices = list(set(efficient_indices))
    resulttxt_cn=f"  结果：有效边界上共有{len(efficient_indices)}个投资组合"
    result_txt_en=f"  Result: {len(efficient_indices)} investment portfolios found along the efficient frontier"
    print(text_lang(resulttxt_cn,result_txt_en))
    
    # 记录有效边界的坐标
    efficient_frontier_coordinates=[eff_x,eff_y]
    
    es_info=[pf_info_original,RandomPortfolios_original,efficient_indices,efficient_frontier_coordinates]
    return es_info

#==============================================================================
#==============================================================================


