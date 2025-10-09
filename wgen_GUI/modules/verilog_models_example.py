#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verilog模块数据结构使用示例

这个示例展示了如何使用VerilogModule、VerilogPort和VerilogModuleCollection类来描述Verilog模块及其连接关系。
"""

# 导入需要的类
from verilog_models import VerilogModule, VerilogPort, VerilogModuleCollection

# 示例1: 创建一个简单的Verilog模块
print("===== 示例1: 创建一个简单的Verilog模块 =====")

simple_module = VerilogModule(name="simple_module", file_path="simple_module.v")

# 添加输入端口
simple_module.add_port(VerilogPort(name="clk", direction="input"))
simple_module.add_port(VerilogPort(name="rst_n", direction="input"))
simple_module.add_port(VerilogPort(name="data_in", direction="input", width={'high': 7, 'low': 0}))

# 添加输出端口
simple_module.add_port(VerilogPort(name="data_out", direction="output", width={'high': 7, 'low': 0}))
simple_module.add_port(VerilogPort(name="valid", direction="output"))

# 打印模块信息
print(simple_module)
print()

# 示例2: 访问模块的端口信息
print("===== 示例2: 访问模块的端口信息 =====")

# 获取所有输入端口
input_ports = simple_module.get_input_ports()
print(f"输入端口数量: {len(input_ports)}")
for port in input_ports:
    print(f"  - {port.name}, 位宽: {port.get_bit_width()}位")

# 获取所有输出端口
output_ports = simple_module.get_output_ports()
print(f"输出端口数量: {len(output_ports)}")
for port in output_ports:
    print(f"  - {port.name}, 位宽: {port.get_bit_width()}位")

# 根据名称获取特定端口
clk_port = simple_module.get_port("clk")
if clk_port:
    print(f"找到端口: {clk_port}")

print()

# 示例3: 创建模块集合并建立连接
print("===== 示例3: 创建模块集合并建立连接 =====")

# 创建模块集合
module_collection = VerilogModuleCollection()

# 创建源模块
master_module = VerilogModule(name="master_module")
master_module.add_port(VerilogPort(name="clk", direction="output"))
master_module.add_port(VerilogPort(name="data_out", direction="output", width={'high': 7, 'low': 0}))
master_module.add_port(VerilogPort(name="valid_out", direction="output"))

# 创建目标模块
slave_module = VerilogModule(name="slave_module")
slave_module.add_port(VerilogPort(name="clk", direction="input"))
slave_module.add_port(VerilogPort(name="data_in", direction="input", width={'high': 7, 'low': 0}))
slave_module.add_port(VerilogPort(name="valid_in", direction="input"))
slave_module.add_port(VerilogPort(name="result", direction="output", width={'high': 7, 'low': 0}))

# 将模块添加到集合
module_collection.add_module(master_module)
module_collection.add_module(slave_module)

# 建立模块之间的连接
module_collection.add_connection(
    source_module_name="master_module", 
    source_port_name="clk", 
    dest_module_name="slave_module", 
    dest_port_name="clk"
)
module_collection.add_connection(
    source_module_name="master_module", 
    source_port_name="data_out", 
    dest_module_name="slave_module", 
    dest_port_name="data_in"
)
module_collection.add_connection(
    source_module_name="master_module", 
    source_port_name="valid_out", 
    dest_module_name="slave_module", 
    dest_port_name="valid_in"
)

# 打印模块层次结构摘要
print(module_collection.get_hierarchy_summary())

# exit(0)

# 示例4: 查看端口的连接信息
print("===== 示例4: 查看端口的连接信息 =====")

# 查看master_module的输出端口连接信息
print(master_module.get_connections_summary())
print()

# 查看slave_module的输入端口连接信息
print(slave_module.get_connections_summary())

# 示例5: 创建带有双向端口的模块
print("\n===== 示例5: 创建带有双向端口的模块 =====")

bidirectional_module = VerilogModule(name="bidirectional_module")
bidirectional_module.add_port(VerilogPort(name="bus", direction="inout", width={'high': 31, 'low': 0}))
bidirectional_module.add_port(VerilogPort(name="oe", direction="input"))

# 添加到模块集合
module_collection.add_module(bidirectional_module)

print(bidirectional_module)

# 示例6: 演示端口位宽不匹配时的部分位宽连接
print("\n===== 示例6: 端口位宽不匹配时的部分位宽连接 =====")

# 创建一个宽端口模块
broad_module = VerilogModule(name="broad_module")
broad_module.add_port(VerilogPort(name="wide_data", direction="output", width={'high': 15, 'low': 0}))  # 16位宽

# 创建一个窄端口模块
narrow_module = VerilogModule(name="narrow_module")
narrow_module.add_port(VerilogPort(name="low_data", direction="input", width={'high': 7, 'low': 0}))   # 8位宽(低8位)
narrow_module.add_port(VerilogPort(name="high_data", direction="input", width={'high': 7, 'low': 0}))  # 8位宽(高8位)

# 添加到模块集合
module_collection.add_module(broad_module)
module_collection.add_module(narrow_module)

# 连接低位数据 (wide_data[7:0] -> low_data[7:0])
module_collection.add_connection(
    source_module_name="broad_module",
    source_port_name="wide_data",
    dest_module_name="narrow_module",
    dest_port_name="low_data",
    source_bit_range={'high': 7, 'low': 0}
)

# 连接高位数据 (wide_data[15:8] -> high_data[7:0])
module_collection.add_connection(
    source_module_name="broad_module",
    source_port_name="wide_data",
    dest_module_name="narrow_module",
    dest_port_name="high_data",
    source_bit_range={'high': 15, 'low': 8}
)

# 打印位宽连接信息
print("部分位宽连接信息:")
for conn in module_collection.get_connections_for_module("broad_module"):
    print(f"  {conn}")

# 示例7: 演示获取连接端口的详细信息
print("\n===== 示例7: 获取连接端口的详细信息 =====")

# 获取连接的端口对象
high_data_port = narrow_module.get_port("high_data")
if high_data_port and high_data_port.source:
    print(f"narrow_module.high_data 的源端口信息:")
    print(f"  模块名称: {high_data_port.source.father_module.name}")
    print(f"  端口名称: {high_data_port.source.name}")
    print(f"  端口方向: {high_data_port.source.direction}")
    print(f"  端口位宽: {high_data_port.source.get_bit_width()}位")

# 示例8: 创建多个目标连接
print("\n===== 示例8: 创建多个目标连接 =====")

# 创建一个分发模块
distributor_module = VerilogModule(name="distributor_module")
distributor_module.add_port(VerilogPort(name="clk", direction="output"))

# 创建多个接收模块
receiver1_module = VerilogModule(name="receiver1_module")
receiver1_module.add_port(VerilogPort(name="clk", direction="input"))

receiver2_module = VerilogModule(name="receiver2_module")
receiver2_module.add_port(VerilogPort(name="clk", direction="input"))

# 添加到模块集合
module_collection.add_module(distributor_module)
module_collection.add_module(receiver1_module)
module_collection.add_module(receiver2_module)

# 分发时钟信号到多个接收模块
module_collection.add_connection(
    source_module_name="distributor_module",
    source_port_name="clk",
    dest_module_name="receiver1_module",
    dest_port_name="clk"
)

module_collection.add_connection(
    source_module_name="distributor_module",
    source_port_name="clk",
    dest_module_name="receiver2_module",
    dest_port_name="clk"
)

# 打印分发模块的连接信息
print("分发模块的连接信息:")
for conn in module_collection.get_connections_for_module("distributor_module"):
    print(f"  {conn}")

# 示例9: 演示删除连接操作
print("\n===== 示例9: 演示删除连接操作 =====")

# 打印删除连接前的状态
print("删除连接前的时钟连接信息:")
for conn in module_collection.get_connections_for_module("distributor_module"):
    print(f"  {conn}")

# 删除receiver1_module的时钟连接
removed = module_collection.remove_connection(
    source_module_name="distributor_module",
    source_port_name="clk",
    dest_module_name="receiver1_module",
    dest_port_name="clk"
)

if removed:
    print("成功删除连接: distributor_module.clk -> receiver1_module.clk")
else:
    print("删除连接失败: 未找到匹配的连接")

# 打印删除连接后的状态
print("\n删除连接后的时钟连接信息:")
for conn in module_collection.get_connections_for_module("distributor_module"):
    print(f"  {conn}")

# 检查端口的源引用是否已清除
source_port = distributor_module.get_port("clk")
receiver1_port = receiver1_module.get_port("clk")
receiver2_port = receiver2_module.get_port("clk")

print("\n端口连接状态检查:")
print(f"distributor_module.clk的destination引用: {source_port.destination}")
print(f"receiver1_module.clk的source引用: {receiver1_port.source}")
print(f"receiver2_module.clk的source引用: {receiver2_port.source}")

# 打印分发模块的连接摘要
print(distributor_module.get_connections_summary())