# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2021-2025(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
# 设置全局缓存
import datetime
import requests_cache

# 计算今天缓存的结束时间（23:59:59）
expire_time = datetime.datetime.combine(
    datetime.date.today(),
    datetime.time.max
)

# 安装全局缓存（所有 requests 请求都会走这里）
requests_cache.install_cache(
    cache_name='siat_cache',   # 缓存文件名，会生成 siat_cache.sqlite
    backend='sqlite',          # 使用 sqlite 存储
    expire_after=expire_time   # 当日有效，午夜过期
)

#==============================================================================
from siat.allin import *

"""
# deprecated soon
import pkg_resources
current_version=pkg_resources.get_distribution("siat").version
"""
from importlib.metadata import version, PackageNotFoundError

pkg_name="siat"
try:
    current_version = version(pkg_name)
    version_info=f"  Successfully enabled {pkg_name} v{current_version} with cache"
except PackageNotFoundError:
    # 处理包未找到的情况
    version_info=f"  Package {pkg_name} not found or not installed"

#print("  Successfully enabled siat v{}".format(current_version))
print(version_info)
#==============================================================================
# 处理stooq.py修复问题：
# 改为在security_prices.py中使用monkey patch对stooq.py进行override，不灵
# 改为自编程序直接抓取tooq.com网站历史数据
#==============================================================================
