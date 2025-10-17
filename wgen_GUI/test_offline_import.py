#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线环境导入测试脚本
用于验证所有第三方依赖是否正确从lib目录导入
"""

import sys
import os

# 添加lib目录到Python路径（模拟正常运行时的导入）
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

print("===== 离线环境导入测试 =====")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"lib目录: {os.path.join(os.path.dirname(__file__), 'lib')}")
print()

# 测试yaml导入
try:
    import yaml
    print("✓ yaml导入成功")
    print(f"  yaml版本: {yaml.__version__}")
    print(f"  yaml路径: {yaml.__file__}")
except ImportError as e:
    print(f"✗ yaml导入失败: {e}")

# 测试项目文件导入
try:
    from modules.file_handler import FileHandler
    print("\n✓ 项目模块导入成功")
except ImportError as e:
    print(f"\n✗ 项目模块导入失败: {e}")

print("\n===== 测试完成 =====")
print("如果所有测试都通过，说明离线环境配置正确。")
print("项目可以在无网络环境中正常运行。")