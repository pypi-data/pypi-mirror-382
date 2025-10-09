#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PixelArray 第三方微服务客户端
这个库包含了常用的开发工具和服务集成：
- order: 订单管理模块和支付模块
- product: 产品管理模块
- celery: 定时任务管理模块
- user: 用户管理模块
"""

__version__ = "1.0.0"
__author__ = "Lu qi"
__email__ = "qi.lu@pixelarrayai.com"

# 导出主要模块
__all__ = [
    "product",
    "celery",
    "user",
    "order",
]
