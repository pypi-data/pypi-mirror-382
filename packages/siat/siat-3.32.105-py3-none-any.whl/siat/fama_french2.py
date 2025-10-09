# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：Fama-French股票市场资产定价因子（中国大陆市场为估计值）
版本：2025-10-7，尚未测试，未加入allin.py
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
import matplotlib.pyplot as plt

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

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
import requests

if __name__=='__main__':

    # 输出下载文本的原始信息FF3
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors.CSV"
    url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily.CSV"
    
    # 输出下载文本的原始信息MOM
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor.CSV"
    
    # 输出下载文本的原始信息FF5
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily.CSV"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    raw = r.content.decode("utf-8", errors="ignore")
    print("\n".join(raw.splitlines()[-50:]))  # 打印后 50 行




        
if __name__=='__main__':
    # 美国三因子月度数据
    df_us_ff3 = get_ff_factors('2020-01-01', '2023-12-31', scope='US', factor='FF3', freq='monthly')
    print(df_us_ff3.head())
    
    # 美国四因子 (自动拼接 FF3 + Momentum)
    df_us_ffc4 = get_ff_factors('2020-01-01', '2023-12-31', scope='US', factor='FFC4', freq='monthly')
    print(df_us_ffc4.head())
    
    # 欧洲五因子年度数据（由月度聚合而成）
    df_eu_ff5 = get_ff_factors('2010-01-01', '2023-12-31', scope='EU', factor='FF5', freq='monthly')
    print(df_eu_ff5.head())
    
    
import pandas as pd
import time
import requests
import io
import re

def get_ff_factorsX(start, end, scope='US', factor='FF3', freq='monthly', retry=3, use_http=False):
    """
    获取 Fama-French 因子数据（Kenneth French 官网 CSV，带浏览器头部；支持 FF3 / FF5 / MOM / FFC4）
    保持原有逻辑不变：参数、重试、FFC4 拼接、频度转换、RF 年化。

    参数:
        start (str): 开始日期, 'YYYY-mm-dd'
        end (str): 结束日期, 'YYYY-mm-dd'
        scope (str): 'US','EU','JP','AP','GL'
        factor (str): 'FF3','FF5','MOM','FFC4'
        freq (str): 'daily','monthly','annual'
        retry (int): 最大重试次数

    返回:
        pd.DataFrame，尚未完全测试，可能存在诸多缺陷！建议沿用原来的get_ff_factors
    """

    dataset_map = {
        # US - FF3
        ('US', 'FF3', 'monthly'): 'F-F_Research_Data_Factors.CSV',
        ('US', 'FF3', 'daily'): 'F-F_Research_Data_Factors_daily.CSV',
        ('US', 'FF3', 'annual'): 'F-F_Research_Data_Factors.CSV',
    
        # US - FF5
        ('US', 'FF5', 'monthly'): 'F-F_Research_Data_5_Factors_2x3.CSV',
        ('US', 'FF5', 'daily'): 'F-F_Research_Data_5_Factors_2x3_daily.CSV',
        ('US', 'FF5', 'annual'): 'F-F_Research_Data_5_Factors_2x3.CSV',
    
        # US - MOM
        ('US', 'MOM', 'monthly'): 'F-F_Momentum_Factor.CSV',
        ('US', 'MOM', 'daily'): 'F-F_Momentum_Factor_daily.CSV',
        ('US', 'MOM', 'annual'): 'F-F_Momentum_Factor.CSV',
    
        # Europe
        ('EU', 'FF3', 'monthly'): 'Europe_3_Factors.CSV',
        ('EU', 'FF3', 'annual'): 'Europe_3_Factors.CSV',
        ('EU', 'FF5', 'monthly'): 'Europe_5_Factors.CSV',
        ('EU', 'FF5', 'annual'): 'Europe_5_Factors.CSV',
    
        # Japan
        ('JP', 'FF3', 'monthly'): 'Japan_3_Factors.CSV',
        ('JP', 'FF3', 'annual'): 'Japan_3_Factors.CSV',
        ('JP', 'FF5', 'monthly'): 'Japan_5_Factors.CSV',
        ('JP', 'FF5', 'annual'): 'Japan_5_Factors.CSV',
    
        # Asia Pacific ex Japan
        ('AP', 'FF3', 'monthly'): 'Asia_Pacific_ex_Japan_3_Factors.CSV',
        ('AP', 'FF3', 'annual'): 'Asia_Pacific_ex_Japan_3_Factors.CSV',
        ('AP', 'FF5', 'monthly'): 'Asia_Pacific_ex_Japan_5_Factors.CSV',
        ('AP', 'FF5', 'annual'): 'Asia_Pacific_ex_Japan_5_Factors.CSV',
    
        # Global
        ('GL', 'FF3', 'monthly'): 'Global_3_Factors.CSV',
        ('GL', 'FF3', 'annual'): 'Global_3_Factors.CSV',
        ('GL', 'FF5', 'monthly'): 'Global_5_Factors.CSV',
        ('GL', 'FF5', 'annual'): 'Global_5_Factors.CSV',
    }

    base_url = ("http://" if use_http else "https://") + "mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"

    def expected_columns(dataset_name: str):
        """
        根据数据集名返回预期因子列名（不含日期）。
        特别注意：MOM 月度文件只有 Mom 一列（没有 RF）。
        """
        name = dataset_name.lower()
        if '5_factors' in name:
            return ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'RF']
        if 'momentum' in name:
            # MOM 月度文件只有 Mom，一般不含 RF；日度文件通常也只含 Mom。
            return ['Mom']
        # 默认 3 因子
        return ['Mkt-RF', 'SMB', 'HML', 'RF']

    def parse_date_token(tok: str):
        tok = str(tok).strip()
        if not tok or not tok[0].isdigit():
            return pd.NaT
        if len(tok) == 6:   # YYYYMM
            return pd.to_datetime(tok, format='%Y%m', errors='coerce')
        if len(tok) == 8:   # YYYYMMDD
            return pd.to_datetime(tok, format='%Y%m%d', errors='coerce')
        return pd.to_datetime(tok, errors='coerce')

    def robust_header_block(text: str, cols_expected: list):
        """
        查找列名行和数据块边界：
        - FF3/FF5 常见表头形如 ",Mkt-RF,SMB,HML,RF"（首列为空，实际为日期），修正为 "Date,Mkt-RF,SMB,HML,RF"
        - MOM 月度文件表头为 ",Mom"（只有 Mom 一列），修正为 "Date,Mom"
        - 数据块从列名行后的第一条数字行开始，到年度表或文件结尾。
        - 若无法找到表头，则退化为无表头模式：从第一条数字行起，直到年度表或文件结尾。
        返回: (header_line, data_lines, sep)
        """
        lines = text.splitlines()
        header_idx, header_line = None, None

        # 优先匹配以逗号开头的表头
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith(','):
                hdr_low = s.lower()
                # MOM 月度文件：",Mom"
                if hdr_low.startswith(',mom'):
                    header_idx = i
                    header_line = 'Date,Mom'
                    break
                # FF3/FF5：",Mkt-RF,SMB,HML,RF" 或类似
                if 'mkt-rf' in hdr_low:
                    header_idx = i
                    header_line = 'Date' + line[line.index(','):]  # 将首列空名替换为 Date
                    break

        # 次优匹配：包含关键列名的表头行
        if header_idx is None:
            for i, line in enumerate(lines):
                l = line.lower()
                has_mom = ('mom' in l)
                has_mktrf = ('mkt-rf' in l) or ('mktrf' in l) or ('mkt' in l and 'rf' in l)
                if has_mom or has_mktrf:
                    header_idx = i
                    header_line = line
                    break

        # 数据块起始：表头后第一条数字行；若未找到表头，退化为第一条数字行
        def first_numeric_index(start_i=0):
            for j in range(start_i, len(lines)):
                sj = lines[j].strip()
                if sj and sj[0].isdigit():
                    return j
            return None

        if header_idx is not None:
            start_idx = first_numeric_index(header_idx + 1)
            if start_idx is None:
                raise ValueError("未找到数据起始行")
        else:
            start_idx = first_numeric_index(0)
            if start_idx is None:
                raise ValueError("未找到数据表起始位置")

        # 数据块结束：年度表开始或末尾
        end_idx = None
        for j in range(start_idx, len(lines)):
            lj = lines[j].lower()
            if ('annual factors' in lj) or ('annual returns' in lj):
                end_idx = j
                break

        data_lines = lines[start_idx:(end_idx if end_idx else None)]
        sep = ',' if (header_line and ',' in header_line) else None
        return header_line, data_lines, sep

    def build_df_from_block(header_line: str, data_lines: list, cols_expected: list, sep, dataset_name: str):
        """
        依据 header + data 块构建 DataFrame；如无 header_line，则按固定列数（日期 + 因子）逐行解析。
        """
        if header_line is not None:
            block = "\n".join([header_line] + data_lines)
            if sep is None:
                df = pd.read_csv(io.StringIO(block), delim_whitespace=True, header=0)
            else:
                df = pd.read_csv(io.StringIO(block), sep=sep, header=0, skipinitialspace=True)

            # 统一首列为 Date
            if df.columns[0].strip().lower() not in ('date', 'yyyymm'):
                df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

            # 标准化列名
            rename = {}
            for c in df.columns:
                lc = c.strip().lower().replace('.', '-').replace('_', '-')
                if lc in ('date', 'yyyymm'):
                    rename[c] = 'Date'
                elif lc in ('mkt-rf', 'mktrf', 'mkt'):
                    rename[c] = 'Mkt-RF'
                elif lc == 'smb':
                    rename[c] = 'SMB'
                elif lc == 'hml':
                    rename[c] = 'HML'
                elif lc == 'rf':
                    rename[c] = 'RF'
                elif lc == 'rmw':
                    rename[c] = 'RMW'
                elif lc == 'cma':
                    rename[c] = 'CMA'
                elif lc == 'mom':
                    rename[c] = 'Mom'
            df.rename(columns=rename, inplace=True)

            # 只保留并按序排列预期列（Date + cols_expected），缺列补空
            keep = ['Date'] + cols_expected
            for c in keep:
                if c not in df.columns:
                    df[c] = pd.NA
            df = df[keep]
        else:
            # 无表头：按固定列数（日期 + 因子）逐行解析
            needed = 1 + len(cols_expected)
            rows = []
            for ln in data_lines:
                s = ln.strip()
                if not s or not s[0].isdigit():
                    continue
                tokens = re.split(r',|\s+', s)
                if len(tokens) < needed:
                    continue
                tokens = tokens[:needed]
                rows.append(tokens)
            if not rows:
                raise ValueError("数据区为空或未能解析出有效行")
            df = pd.DataFrame(rows, columns=['Date'] + cols_expected)

        # 日期解析与索引
        df['Date'] = df['Date'].apply(parse_date_token)
        df = df[~df['Date'].isna()]
        df.set_index('Date', inplace=True)

        # 数值转换
        for c in cols_expected:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        # 去除全空行
        return df.dropna(how='all')

    def fetch_data(dataset: str, start: str, end: str, retry: int):
        url = base_url + dataset
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/117.0 Safari/537.36"
            )
        }
        for attempt in range(retry):
            try:
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                raw = r.content.decode("utf-8", errors="ignore")

                cols_expected = expected_columns(dataset)
                header_line, data_lines, sep = robust_header_block(raw, cols_expected)
                df = build_df_from_block(header_line, data_lines, cols_expected, sep, dataset)

                # 截取日期范围
                df = df.loc[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]
                return df.dropna(how="all")
            except Exception as e:
                print(f"第 {attempt+1} 次尝试失败: {e}")
                time.sleep(3)
        raise ConnectionError(f"获取数据失败，已重试 {retry} 次。")

    # === 特殊处理 Carhart 四因子（FFC4） ===
    if factor == 'FFC4':
        # FF3 + MOM
        ff3_key = (scope, 'FF3', freq if (scope, 'FF3', freq) in dataset_map else 'monthly')
        mom_key = (scope, 'MOM', freq if (scope, 'MOM', freq) in dataset_map else 'monthly')

        df_ff3 = fetch_data(dataset_map[ff3_key], start, end, retry)
        df_mom = fetch_data(dataset_map[mom_key], start, end, retry)

        # MOM 数据表只有 Mom 列；若存在 RF 列（个别日度文件或其他版本），避免冲突，删除 MOM 的 RF
        if 'RF' in df_mom.columns:
            df_mom = df_mom.drop(columns=['RF'])

        # 合并为 FFC4：Mkt-RF, SMB, HML, RF + Mom
        df = df_ff3.join(df_mom, how='inner')

    else:
        key = (scope, factor, freq)
        if key not in dataset_map:
            alt_key = (scope, factor, 'monthly')
            if alt_key not in dataset_map:
                raise ValueError(f"暂不支持该组合: {key}")
            df = fetch_data(dataset_map[alt_key], start, end, retry)
        else:
            df = fetch_data(dataset_map[key], start, end, retry)

    # === 频度转换（保持原逻辑） ===
    if freq == 'daily' and df.index.inferred_freq != 'D':
        df = df.resample('D').ffill()
    elif freq == 'annual' and df.index.inferred_freq != 'A-DEC':
        df = df.resample('A-DEC').mean()

    # === 添加年化 RF（保持原逻辑） ===
    if 'RF' in df.columns:
        if freq == 'monthly':
            df['RF_annual'] = (1 + df['RF'] / 100) ** 12 - 1
        elif freq == 'daily':
            df['RF_annual'] = (1 + df['RF'] / 100) ** 252 - 1
        elif freq == 'annual':
            df['RF_annual'] = df['RF'] / 100
    else:
        df['RF_annual'] = None

    return df

    
#==============================================================================

def plot_ff_factors(start, end, scope='US', factor='FF3', freq='monthly', cols=None):
    """
    绘制 Fama-French 因子走势
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scope (str): 国家或经济体, 如 'US', 'EU', 'JP', 'AP', 'GL', 'CN', 'HK'
        factor (str): 'FF3', 'FFC4', 'FF5'
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的列名，例如 ['Mkt-RF','SMB','HML']
    """
    df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
    
    if cols is None:
        # 默认绘制除 RF 和 RF_annual 外的所有因子
        cols = [c for c in df.columns if c not in ['RF','RF_annual']]
    
    plt.figure(figsize=(10,6))
    for c in cols:
        plt.plot(df.index, df[c], label=c)
    
    plt.title(f"{scope} {factor} Factors ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Return (%)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__=='__main__':
    # 绘制美国三因子月度走势
    plot_ff_factors('2020-01-01', '2024-12-31', scope='US', factor='FF3', freq='monthly')
    
    # 绘制美国四因子（自动拼接 FF3 + Momentum）
    plot_ff_factors('2020-01-01', '2023-12-31', scope='US', factor='FFC4', freq='monthly')
    
    # 绘制欧洲五因子年度走势
    plot_ff_factors('2010-01-01', '2023-12-31', scope='EU', factor='FF5', freq='annual')

#==============================================================================

def compare_ff_factors(start, end, scopes=['US','EU'], factor='FF3', freq='monthly', col='Mkt-RF'):
    """
    对比多个国家/地区的 Fama-French 因子走势
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FFC4', 'FF5'
        freq (str): 'daily', 'monthly', 'annual'
        col (str): 要对比的因子列名，例如 'Mkt-RF', 'SMB', 'HML'
    """
    plt.figure(figsize=(10,6))
    
    for scope in scopes:
        try:
            df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
            if col not in df.columns:
                print(f"{scope} 数据中没有列 {col}，跳过。")
                continue
            plt.plot(df.index, df[col], label=f"{scope}-{col}")
        except Exception as e:
            print(f"获取 {scope} 数据失败: {e}")
    
    plt.title(f"Fama-French {factor} {col} 对比 ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Return (%)")
    plt.legend()
    plt.grid(True)
    plt.show()



if __name__=='__main__':
    # 对比美国和欧洲的三因子模型中的市场因子 (Mkt-RF)
    compare_ff_factors('2015-01-01', '2023-12-31', scopes=['US','EU'], factor='FF3', freq='monthly', col='Mkt-RF')
    
    # 对比美国、日本、全球的 SMB 因子
    compare_ff_factors('2010-01-01', '2023-12-31', scopes=['US','JP','GL'], factor='FF3', freq='monthly', col='SMB')
    
    # 对比美国和欧洲的五因子模型中的盈利因子 (RMW)
    compare_ff_factors('2010-01-01', '2023-12-31', scopes=['US','EU'], factor='FF5', freq='monthly', col='RMW')


#==============================================================================
import numpy as np

def compare_ff_cumulative(start, end, scopes=['US','EU'], factor='FF3', freq='monthly', col='Mkt-RF'):
    """
    对比多个国家/地区的 Fama-French 因子累计收益走势
    
    📌 功能说明
    累计收益曲线：将因子收益率序列转为复利累计收益，起始点为 1。
    多国对比：支持多个国家/地区在同一张图中对比。
    灵活选择因子：支持 FF3、FFC4、FF5 模型中的任意因子。
    频度支持：日度、月度、年度（自动转换）。
    错误处理：如果某个国家没有该因子，会自动跳过并提示。
    这样，就能展示不同国家因子长期表现的差异，例如“美国 vs 欧洲的市场风险溢价长期走势”。    
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FFC4', 'FF5'
        freq (str): 'daily', 'monthly', 'annual'
        col (str): 要对比的因子列名，例如 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'
    """
    plt.figure(figsize=(10,6))
    
    for scope in scopes:
        try:
            df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
            if col not in df.columns:
                print(f"{scope} 数据中没有列 {col}，跳过。")
                continue
            
            # 将百分比收益率转为小数
            returns = df[col] / 100.0
            
            # 累计收益曲线（复利）
            cum_return = (1 + returns).cumprod()
            
            plt.plot(df.index, cum_return, label=f"{scope}-{col}")
        except Exception as e:
            print(f"获取 {scope} 数据失败: {e}")
    
    plt.title(f"Fama-French {factor} {col} 累计收益对比 ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (Index=1)")
    plt.legend()
    plt.grid(True)
    plt.show()




if __name__=='__main__':
    # 对比美国和欧洲的市场因子累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','EU'], factor='FF3', freq='monthly', col='Mkt-RF')
    
    # 对比美国、日本、全球的 SMB 因子累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','JP','GL'], factor='FF3', freq='monthly', col='SMB')
    
    # 对比美国和欧洲的盈利因子 (RMW) 累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','EU'], factor='FF5', freq='monthly', col='RMW')

#==============================================================================

def compare_factors_cumulative_single_country(start, end, scope='US', factor='FF5', freq='monthly', cols=None):
    """
    绘制单一国家/地区的多个 Fama-French 因子累计收益曲线
    
    📌 功能说明
    单国多因子对比：在同一张图中展示多个因子的累计收益曲线。
    灵活选择因子：支持 FF3、FFC4、FF5 模型。
    自动处理频度：日度、月度、年度均可。
    默认绘制所有因子（除 RF 和 RF_annual），也可手动指定 cols。
    累计收益曲线：采用复利累计，起始点为 1。
    这样就能展示同一国家内部不同因子的长期表现差异，例如“美国市场因子中，SMB 与 HML 的长期走势对比”。    
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scope (str): 国家或经济体, 如 'US','EU','JP','AP','GL','CN','HK'
        factor (str): 'FF3', 'FFC4', 'FF5'
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的因子列名，例如 ['Mkt-RF','SMB','HML','RMW','CMA']
    """
    df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
    
    if cols is None:
        # 默认绘制除 RF 和 RF_annual 外的所有因子
        cols = [c for c in df.columns if c not in ['RF','RF_annual']]
    
    plt.figure(figsize=(10,6))
    
    for c in cols:
        if c not in df.columns:
            print(f"{scope} 数据中没有列 {c}，跳过。")
            continue
        returns = df[c] / 100.0
        cum_return = (1 + returns).cumprod()
        plt.plot(df.index, cum_return, label=c)
    
    plt.title(f"{scope} {factor} 多因子累计收益对比 ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (Index=1)")
    plt.legend()
    plt.grid(True)
    plt.show()



if __name__=='__main__':
    # 美国五因子模型：对比 Mkt-RF、SMB、HML、RMW、CMA
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='US', factor='FF5', freq='monthly',
        cols=['Mkt-RF','SMB','HML','RMW','CMA']
    )
    
    # 欧洲三因子模型：对比 Mkt-RF、SMB、HML
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='EU', factor='FF3', freq='monthly'
    )
    
    # 日本四因子模型（FF3 + Momentum）
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='JP', factor='FFC4', freq='monthly',
        cols=['Mkt-RF','SMB','HML','Mom']
    )

    
#==============================================================================

def plot_ff_matrix(start, end, scopes=['US','EU','JP'], factor='FF5', freq='monthly', cols=None):
    """
    绘制多国 × 多因子累计收益矩阵图

    矩阵布局：行 = 国家/地区，列 = 因子。
    累计收益曲线：采用复利累计，起始点为 1。
    灵活选择因子：默认绘制所有可用因子，也可通过 cols 指定。
    自动跳过缺失因子：如果某个国家没有该因子，子图会隐藏。
    适合教材展示：一张图就能展示跨国 × 多因子的长期表现差异。
    这样就能展示一个多维度对比图，例如“美国、欧洲、日本的五因子模型累计收益矩阵”，非常直观。
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FFC4', 'FF5'
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的因子列名，例如 ['Mkt-RF','SMB','HML','RMW','CMA']
    """
    # 先获取第一个国家的数据，确定默认因子列
    df_sample = get_ff_factors(start, end, scope=scopes[0], factor=factor, freq=freq)
    if cols is None:
        cols = [c for c in df_sample.columns if c not in ['RF','RF_annual']]
    
    n_rows = len(scopes)
    n_cols = len(cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows), sharex=True)
    
    if n_rows == 1: axes = [axes]  # 保证二维结构
    if n_cols == 1: axes = [[ax] for ax in axes]
    
    for i, scope in enumerate(scopes):
        try:
            df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
            for j, c in enumerate(cols):
                ax = axes[i][j]
                if c not in df.columns:
                    ax.set_visible(False)
                    continue
                returns = df[c] / 100.0
                cum_return = (1 + returns).cumprod()
                ax.plot(df.index, cum_return, label=f"{scope}-{c}")
                ax.set_title(f"{scope}-{c}")
                ax.grid(True)
                if i == n_rows-1:
                    ax.set_xlabel("Date")
                if j == 0:
                    ax.set_ylabel("Cumulative Return")
        except Exception as e:
            print(f"获取 {scope} 数据失败: {e}")
    
    plt.tight_layout()
    plt.show()





if __name__=='__main__':
    # 美国、欧洲、日本的五因子模型，展示所有因子累计收益
    plot_ff_matrix(
        '2010-01-01', '2023-12-31',
        scopes=['US','EU','JP'],
        factor='FF5',
        freq='monthly'
    )
    
    # 美国、全球的三因子模型，只展示 Mkt-RF、SMB、HML
    plot_ff_matrix(
        '2010-01-01', '2023-12-31',
        scopes=['US','GL'],
        factor='FF3',
        freq='monthly',
        cols=['Mkt-RF','SMB','HML']
    )

    


#==============================================================================
if __name__=='__main__':
    # 一次性生成美国、欧洲、日本、全球的 FF3/FF5/FFC4 月度累计收益图
    batch_generate_plots(
        start='2010-01-01',
        end='2023-12-31',
        scopes=['US','EU','JP','GL'],
        factors=['FF3','FF5','FFC4'],
        freqs=['monthly']
    )


import os

def save_ff_cumulative_plot(start, end, scope, factor, freq, cols=None, outdir="ff_plots"):
    """
    保存单国多因子累计收益图为 PNG 文件
    
    📌 功能亮点
    一键生成整套教材图表，省去手动绘制的麻烦。
    自动化：一行代码批量生成所有教材图表。
    可扩展：可以轻松增加 scopes、factors、freqs。
    高分辨率：保存为 300dpi PNG，适合教材/论文排版。
    健壮性：遇到缺失数据会跳过并提示，不会中断整个批处理。   
    
    运行后，会在当前目录下生成一个 ff_plots/ 文件夹，里面包含类似：
    ff_plots/
     ├── US_FF3_monthly.png
     ├── US_FF5_monthly.png
     ├── US_FFC4_monthly.png
     ├── EU_FF3_monthly.png
     ├── EU_FF5_monthly.png
     ├── EU_FFC4_monthly.png
     ├── JP_FF3_monthly.png
     ├── JP_FF5_monthly.png
     ├── JP_FFC4_monthly.png
     ├── GL_FF3_monthly.png
     ├── GL_FF5_monthly.png
     └── GL_FFC4_monthly.png
    
    
    
    """
    df = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
    if cols is None:
        cols = [c for c in df.columns if c not in ['RF','RF_annual']]
    
    plt.figure(figsize=(10,6))
    for c in cols:
        if c not in df.columns:
            continue
        returns = df[c] / 100.0
        cum_return = (1 + returns).cumprod()
        plt.plot(df.index, cum_return, label=c)
    
    plt.title(f"{scope} {factor} 累计收益 ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (Index=1)")
    plt.legend()
    plt.grid(True)
    
    os.makedirs(outdir, exist_ok=True)
    fname = f"{outdir}/{scope}_{factor}_{freq}.png"
    plt.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"已保存图表: {fname}")


def batch_generate_plots(start, end, scopes=['US','EU','JP','GL'], factors=['FF3','FF5','FFC4'], freqs=['monthly']):
    """
    批量生成并保存教材图表
    """
    for scope in scopes:
        for factor in factors:
            for freq in freqs:
                try:
                    save_ff_cumulative_plot(start, end, scope, factor, freq)
                except Exception as e:
                    print(f"生成 {scope}-{factor}-{freq} 图表失败: {e}")

#==============================================================================

#==============================================================================

#==============================================================================

#==============================================================================




















