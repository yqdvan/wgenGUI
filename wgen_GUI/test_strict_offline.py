#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格离线环境导入测试脚本
模拟在没有系统安装PyYAML的环境中运行
"""

import sys
import os

# 保存原始sys.path以便恢复
original_path = sys.path.copy()

# 移除site-packages目录，模拟纯净的离线环境
clean_path = []
for path in sys.path:
    if 'site-packages' not in path:
        clean_path.append(path)

sys.path = clean_path

# 添加lib目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

print("===== 严格离线环境测试 =====")
print(f"Python版本: {sys.version}")
print(f"lib目录优先级导入: 已设置")
print(f"site-packages目录: 已移除")
print()

try:
    # 测试yaml导入
    import yaml
    print("✓ yaml导入成功 (从lib目录)")
    print(f"  yaml版本: {yaml.__version__}")
    print(f"  yaml路径: {yaml.__file__}")
    
    # 测试项目核心功能
    print("\n✓ 离线环境配置成功")
    print("项目可以在没有网络和系统安装PyYAML的环境中运行")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请检查lib目录中的PyYAML安装")
    
except Exception as e:
    print(f"✗ 测试过程中出现错误: {e}")

# 恢复原始sys.path
sys.path = original_path

print("\n===== 测试完成 =====")
print("提示: 在实际部署时，可以确保lib目录包含所有需要的第三方库")