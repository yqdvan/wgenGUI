from verilog_models import VerilogModule, VerilogPort, VerilogModuleCollection

"""
Verilog模块数据结构使用示例

这个示例展示了如何使用VerilogModule、VerilogPort和VerilogModuleCollection类来描述Verilog模块及其连接关系。
"""

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
    source_module="master_module", 
    source_port="clk", 
    dest_module="slave_module", 
    dest_port="clk"
)
module_collection.add_connection(
    source_module="master_module", 
    source_port="data_out", 
    dest_module="slave_module", 
    dest_port="data_in"
)
module_collection.add_connection(
    source_module="master_module", 
    source_port="valid_out", 
    dest_module="slave_module", 
    dest_port="valid_in"
)

# 打印模块层次结构摘要
print(module_collection.get_hierarchy_summary())

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

print(bidirectional_module)

# 为双向端口设置源和目的地
bus_port = bidirectional_module.get_port("bus")
if bus_port:
    bus_port.source = "other_module.data_out"
    bus_port.destination = "another_module.data_in"
    print(f"\n双向端口连接信息: {bus_port}")