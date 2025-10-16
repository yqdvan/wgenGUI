import sys
import os
from verilog_models import VerilogModule, VerilogModuleCollection

# 测试VerilogModule的parameters属性和序列化/反序列化功能
def test_parameters_serialization():
    print("开始测试VerilogModule参数序列化/反序列化...")
    
    # 创建一个测试模块
    module = VerilogModule(name="test_module", module_def_name="test_module_def")
    
    # 添加参数
    module.parameters["WIDTH"] = 32
    module.parameters["DEPTH"] = 1024
    module.parameters["ENABLE_FEATURE"] = 1
    
    print(f"原始模块参数: {module.parameters}")
    
    # 创建模块集合并添加模块
    collection = VerilogModuleCollection()
    collection.add_module(module)
    
    # 序列化为字典
    dict_data = collection.to_dict()
    print(f"序列化后的参数: {dict_data['modules'][0]['parameters']}")
    
    # 从字典反序列化
    new_collection = VerilogModuleCollection.from_dict(dict_data)
    new_module = new_collection.modules[0]
    
    print(f"反序列化后的参数: {new_module.parameters}")
    
    # 验证参数是否正确恢复
    assert new_module.parameters["WIDTH"] == 32, f"WIDTH参数值错误: {new_module.parameters.get('WIDTH')}"
    assert new_module.parameters["DEPTH"] == 1024, f"DEPTH参数值错误: {new_module.parameters.get('DEPTH')}"
    assert new_module.parameters["ENABLE_FEATURE"] == 1, f"ENABLE_FEATURE参数值错误: {new_module.parameters.get('ENABLE_FEATURE')}"
    
    print("✓ 参数序列化和反序列化测试通过!")

# 测试JSON序列化和反序列化
def test_json_serialization():
    print("\n开始测试JSON序列化/反序列化...")
    
    # 创建模块和参数
    module = VerilogModule(name="json_test_module")
    module.parameters["PARAM_A"] = 10
    module.parameters["PARAM_B"] = 20
    
    # 创建集合
    collection = VerilogModuleCollection()
    collection.add_module(module)
    
    # 序列化为JSON
    json_str = collection.to_json()
    print(f"JSON数据: {json_str}")
    
    # 从JSON反序列化
    new_collection = VerilogModuleCollection.from_json(json_str)
    new_module = new_collection.modules[0]
    
    print(f"从JSON恢复的参数: {new_module.parameters}")
    
    # 验证参数
    assert new_module.parameters["PARAM_A"] == 10, f"JSON反序列化PARAM_A错误"
    assert new_module.parameters["PARAM_B"] == 20, f"JSON反序列化PARAM_B错误"
    
    print("✓ JSON序列化和反序列化测试通过!")

# 测试参数类型验证
def test_parameter_types():
    print("\n开始测试参数类型...")
    
    module = VerilogModule(name="type_test_module")
    
    # 添加不同类型的键值对，确保类型正确
    module.parameters["STRING_KEY"] = 42  # 字符串键，整数值
    module.parameters["ANOTHER_KEY"] = 0  # 测试边界值
    
    # 检查类型
    for key, value in module.parameters.items():
        assert isinstance(key, str), f"键 '{key}' 不是字符串类型"
        assert isinstance(value, int), f"值 '{value}' 不是整数类型"
    
    print("✓ 参数类型测试通过!")

if __name__ == "__main__":
    try:
        test_parameters_serialization()
        test_json_serialization()
        test_parameter_types()
        print("\n🎉 所有测试都通过了!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)