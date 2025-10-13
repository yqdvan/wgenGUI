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

# 示例10: 测试模块集合的序列化和反序列化功能
print("\n===== 示例10: 测试模块集合的序列化和反序列化功能 =====")

# 创建一个用于测试序列化的模块集合
serialization_test_collection = VerilogModuleCollection()

# 创建几个模块用于测试
test_module1 = VerilogModule(name="test_module1")
test_module1.add_port(VerilogPort(name="clk", direction="output"))
test_module1.add_port(VerilogPort(name="data_out", direction="output", width={'high': 7, 'low': 0}))

test_module2 = VerilogModule(name="test_module2")
test_module2.add_port(VerilogPort(name="clk", direction="input"))
test_module2.add_port(VerilogPort(name="data_in", direction="input", width={'high': 7, 'low': 0}))
test_module2.add_port(VerilogPort(name="result", direction="output", width={'high': 7, 'low': 0}))

# 添加模块到集合
serialization_test_collection.add_module(test_module1)
serialization_test_collection.add_module(test_module2)

# 建立连接
serialization_test_collection.add_connection(
    source_module_name="test_module1",
    source_port_name="clk",
    dest_module_name="test_module2",
    dest_port_name="clk"
)
serialization_test_collection.add_connection(
    source_module_name="test_module1",
    source_port_name="data_out",
    dest_module_name="test_module2",
    dest_port_name="data_in"
)

print("原始模块集合的层次结构摘要:")
print(serialization_test_collection.get_hierarchy_summary())

# 测试1: 使用to_dict()和from_dict()
print("\n测试1: 使用to_dict()和from_dict()")
collection_dict = serialization_test_collection.to_dict()
print(f"序列化到字典成功, 包含{len(collection_dict['modules'])}个模块和{len(collection_dict['connections'])}个连接")

# 从字典反序列化
restored_collection = VerilogModuleCollection.from_dict(collection_dict)
print("从字典反序列化成功!")
print("反序列化后的模块集合层次结构摘要:")
print(restored_collection.get_hierarchy_summary())

# 测试2: 使用to_json()和from_json()
print("\n测试2: 使用to_json()和from_json()")
collection_json = serialization_test_collection.to_json()
print(f"序列化到JSON字符串成功, 字符串长度: {len(collection_json)}字符")

# 从JSON字符串反序列化
json_restored_collection = VerilogModuleCollection.from_json(collection_json)
print("从JSON字符串反序列化成功!")
print("反序列化后的模块集合层次结构摘要:")
print(json_restored_collection.get_hierarchy_summary())

# 测试3: 验证反序列化后的对象功能是否正常
print("\n测试3: 验证反序列化后的对象功能是否正常")

# 检查模块数量是否正确
print(f"原始集合模块数: {len(serialization_test_collection.modules)}")
print(f"反序列化集合模块数: {len(restored_collection.modules)}")

# 检查连接数量是否正确
print(f"原始集合连接数: {len(serialization_test_collection.connections)}")
print(f"反序列化集合连接数: {len(restored_collection.connections)}")

# 检查模块间连接是否正确建立
restored_module1 = restored_collection.get_module("test_module1")
restored_module2 = restored_collection.get_module("test_module2")

if restored_module1 and restored_module2:
    clk_port = restored_module2.get_port("clk")
    data_in_port = restored_module2.get_port("data_in")
    
    print(f"restored_module2.clk的源端口: {clk_port.source.name if clk_port and clk_port.source else None}")
    print(f"restored_module2.data_in的源端口: {data_in_port.source.name if data_in_port and data_in_port.source else None}")

print("\n序列化和反序列化测试完成!")

# 示例11: 测试模块集合的文件保存和加载功能
print("\n===== 示例11: 测试模块集合的文件保存和加载功能 =====")

# 定义测试文件路径
test_file_path = "test_module_collection.json"

# 测试保存到文件
print(f"\n测试1: 将模块集合保存到文件 {test_file_path}")
save_success = serialization_test_collection.save_to_file(test_file_path)
if save_success:
    print(f"成功将模块集合保存到文件 {test_file_path}!")
    
    # 测试从文件加载
    print(f"\n测试2: 从文件 {test_file_path} 加载模块集合")
    file_loaded_collection = VerilogModuleCollection.load_from_file(test_file_path)
    
    if file_loaded_collection:
        print("成功从文件加载模块集合!")
        print("加载后的模块集合层次结构摘要:")
        print(file_loaded_collection.get_hierarchy_summary())
        
        # 验证加载的对象功能是否正常
        print("\n测试3: 验证从文件加载的对象功能是否正常")
        print(f"原始集合模块数: {len(serialization_test_collection.modules)}")
        print(f"加载集合模块数: {len(file_loaded_collection.modules)}")
        print(f"原始集合连接数: {len(serialization_test_collection.connections)}")
        print(f"加载集合连接数: {len(file_loaded_collection.connections)}")
        
        # 检查模块间连接是否正确建立
        loaded_module1 = file_loaded_collection.get_module("test_module1")
        loaded_module2 = file_loaded_collection.get_module("test_module2")
        
        if loaded_module1 and loaded_module2:
            clk_port = loaded_module2.get_port("clk")
            data_in_port = loaded_module2.get_port("data_in")
            
            print(f"loaded_module2.clk的源端口: {clk_port.source.name if clk_port and clk_port.source else None}")
            print(f"loaded_module2.data_in的源端口: {data_in_port.source.name if data_in_port and data_in_port.source else None}")
    else:
        print(f"无法从文件 {test_file_path} 加载模块集合!")
else:
    print(f"无法将模块集合保存到文件 {test_file_path}!")

print("\n文件保存和加载测试完成!")