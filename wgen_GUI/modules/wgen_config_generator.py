# 尝试相对导入，如果失败则使用绝对导入
try:
    from .code_generator_interface import CodeGeneratorInterface
    from .verilog_models import VerilogModuleCollection, VerilogModule, VerilogPort, VerilogConnection
except ImportError:
    from code_generator_interface import CodeGeneratorInterface
    from verilog_models import VerilogModuleCollection, VerilogModule, VerilogPort, VerilogConnection
from datetime import datetime
import getpass
import os


class WgenConfigGenerator(CodeGeneratorInterface):
    """
    WGen配置生成器
    
    实现CodeGeneratorInterface接口，用于从数据库中获取所有模块名称并拼接成字符串返回。
    """
    
    def generate_by_DB(self, database: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块名称并拼接成字符串
        
        参数:
            database (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块名称字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(database):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 拼接模块名称成字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = f"# create on {current_time} by " + getpass.getuser() + "\n"
        result += "\n" + self.gen_instace_block(database)
        result += "\n" + self.gen_generated_module_def(database)
        result += "\n" + self.gen_hierarchy_block(database)
        result += "\n" + self.gen_generated_md_port_def(database)
        result += "\n" + self.gen_connection_block(database)

        result = self.string_optimize(result)
        
        return result 

    def string_optimize(self, result: str) -> str:
        """
        对输入字符串进行优化，移除多余的空格和空行
        
        参数:
            input_str (str): 输入的字符串
            
        返回:
            str: 优化后的字符串
        """
        # result 中 所有 from .* to .* 的行要求按照 to 对齐
        connection_lines = result.split("\n")
        
        # 第一步：找出所有包含"to"的行，并计算每行中"to"的位置
        to_lines = []
        to_positions = []
        
        for line in connection_lines:
            if line.startswith("from") and line.find(" to ") != -1:
                to_pos = line.find(" to ")
                to_lines.append(line)
                to_positions.append(to_pos)
        
        # 第二步：找出最大的to位置，作为对齐基准
        if to_lines:
            max_to_pos = max(to_positions)
            
            # 第三步：对每行进行调整，使所有行的"to"对齐
            for i, line in enumerate(connection_lines):
                if line.startswith("from") and line.find(" to ") != -1:
                    # 分割行，在"from"部分后面添加适当的空格
                    to_pos = line.find(" to ")
                    from_part = line[:to_pos]
                    to_part = line[to_pos:]
                    # 计算需要添加的空格数，确保to位置对齐
                    spaces_needed = max_to_pos - to_pos
                    # 重建行
                    connection_lines[i] = from_part + " " * spaces_needed + to_part
        
        result = "\n".join(connection_lines)
        return result

    def gen_instace_block(self, db: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块实例化代码并拼接成字符串
        
        参数:
            db (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块实例化代码字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(db):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 获取所有模块实例化代码
        instance_lines = []
        instance_lines.append(f"##########################################")
        instance_lines.append(f"# generated module instance")
        instance_lines.append(f"##########################################")
        for module in db.modules:
            if not module.need_gen:
                instance_lines.append(f"instance {module.name} \\")
                instance_lines.append(f"  module {module.module_def_name} \\")
                instance_lines.append(f"  library work \\")
                if os.path.isfile(module.file_path):
                    dir_path = os.path.dirname(module.file_path)
                    instance_lines.append(f"  path {dir_path}")
                else:
                    instance_lines.append(f"  path {module.file_path}")
                # if have parameter
                if module.parameters:
                    for par_name, par_value in module.parameters.items():
                        instance_lines.append(f"    generic {par_name}  {par_value} in {module.name} ")
                instance_lines.append(f"\n")

    # 拼接模块实例化代码成字符串
        result = "\n".join(instance_lines)
        return result


    def gen_generated_module_def(self, db: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块定义代码并拼接成字符串
        
        参数:
            db (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块定义代码字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(db):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 获取所有模块定义代码
        module_def_lines = []
        module_def_lines.append(f"##########################################")
        module_def_lines.append(f"# generated module definition")
        module_def_lines.append(f"##########################################")

        for module in db.modules:
            if module.need_gen:
                module_def_lines.append(f"generate verilog {module.module_def_name}  \\")
                module_def_lines.append(f"  library work \\")
                module_def_lines.append(f"  port_order user \\")
                module_def_lines.append(f"  inst_name u_{module.module_def_name} \\")
                module_def_lines.append(f"  path {module.file_path}")
                module_def_lines.append(f"")

        return "\n".join(module_def_lines)


    def gen_hierarchy_block(self, db: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块层级代码并拼接成字符串
        
        参数:
            db (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块层级代码字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(db):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 获取所有模块层级代码
        hierarchy_lines = []
        hierarchy_lines.append(f"##########################################")
        hierarchy_lines.append(f"# generated module hierarchy")
        hierarchy_lines.append(f"##########################################")
        for module in db.modules:
            if module.need_gen:
                hierarchy_def = f"hierarchy {module.module_def_name} = "
                for include_md in module.includes:
                    hierarchy_def += f"{include_md.name} "
                hierarchy_lines.append(hierarchy_def)
                hierarchy_lines.append(f"")

        return "\n".join(hierarchy_lines)


    def gen_generated_md_port_def(self, db: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块端口定义代码并拼接成字符串
        
        参数:
            db (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块端口定义代码字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(db):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 获取所有模块端口定义代码
        port_def_lines = []
        port_def_lines.append(f"##########################################")
        port_def_lines.append(f"# generated module port definition")
        port_def_lines.append(f"##########################################")
        for module in db.modules:
            if module.need_gen:
                port_def_lines.append(f"# port definition {module.module_def_name} ")
                for port in module.ports:
                    pin_or_bus = "pin" if port.get_width_value() == 1 else "bus"
                    port_range_str = f"({port.width['high']}:{port.width['low']})" if port.get_width_value() > 1 else ""
                    port_dir = ""
                    if port.direction == "input":
                        port_dir = "in"
                    elif port.direction == "output":
                        port_dir = "out"
                    elif port.direction == "inout": 
                        port_dir = "inout"
                    port_def_lines.append(f"{pin_or_bus}  {port_dir} {module.name}.{port.name} {port_range_str}")
                port_def_lines.append(f"")

        return "\n".join(port_def_lines)

    def gen_connection_block(self, db: VerilogModuleCollection) -> str:
        """
        从数据库中获取所有模块连接代码并拼接成字符串
        
        参数:
            db (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 拼接后的模块连接代码字符串
            
        异常:
            ValueError: 当数据库验证失败时抛出
        """
        # 首先验证数据库
        if not self.validate_database(db):
            raise ValueError("Invalid database: database must be a valid VerilogModuleCollection with at least one module")
        
        # 获取所有模块连接代码
        connection_lines = []
        connection_lines.append(f"##########################################")
        connection_lines.append(f"# module connection")
        connection_lines.append(f"##########################################")
        for connection in db.connections:
            src_port_range_str = ""
            dst_port_range_str = ""
            if connection._get_width_value(connection.source_bit_range) > 1 and connection._get_width_value(connection.dest_bit_range) > 1:
                src_port_range_str = f"({connection.source_bit_range['high']}:{connection.source_bit_range['low']})" 
                dst_port_range_str = f"({connection.dest_bit_range['high']}:{connection.dest_bit_range['low']})" 

            if connection.source_port.name == "tie_0":
                connection_lines.append(f"from \"all_0\"  to  {{ {connection.dest_module_name}.{connection.dest_port.name}{dst_port_range_str} }}")
            elif connection.source_port.name == "tie_1":
                connection_lines.append(f"from \"all_1\"  to  {{ {connection.dest_module_name}.{connection.dest_port.name}{dst_port_range_str} }}")
            else:
                connection_lines.append(f"from {connection.source_module_name}.{connection.source_port.name}{src_port_range_str} to  {{ {connection.dest_module_name}.{connection.dest_port.name}{dst_port_range_str} }}")
        connection_lines.append(f" ")
        
        return "\n".join(connection_lines)



if __name__ == "__main__":
    # 测试代码
    db = VerilogModuleCollection()
    obj1 = VerilogModule("u_module1", "xxx/yyy/module1.v", "module1")
    obj1.parameters["par1"] = 100
    obj1.parameters["width"] = 32
    obj1.need_gen = True
    obj1.ports.append(VerilogPort("clk", "input", {'high': 0, 'low': 0}, None))
    obj1.ports.append(VerilogPort("rst_n", "input", {'high': 0, 'low': 0}, None))
    obj1.ports.append(VerilogPort("data_in", "input", {'high': 31, 'low': 0}, None))
    obj1.ports.append(VerilogPort("data_out", "output", {'high': 31, 'low': 0}, None))
    obj1.ports.append(VerilogPort("clk_out", "output", {'high': 0, 'low': 0}, None))
    db.add_module(obj1)

    obj2 = VerilogModule("u_module2", "xxx/yyy/module2.v", "module2")
    obj2.ports.append(VerilogPort("clk", "input", {'high': 0, 'low': 0}, None))
    obj2.ports.append(VerilogPort("rst_n", "input", {'high': 0, 'low': 0}, None))
    obj2.ports.append(VerilogPort("data_in", "input", {'high': 31, 'low': 0}, None))
    obj2.ports.append(VerilogPort("data_out", "output", {'high': 31, 'low': 0}, None))
    obj2.parameters["par2"] = 200
    obj2.parameters["size"] = 1024
    db.add_module(obj2) 

    obj3 = VerilogModule("u_module3", "xxx/yyy/module2.v", "module2")
    obj3.parameters["par2"] = 200
    obj3.parameters["size"] = 1024
    db.add_module(obj3) 
    obj3.ports.append(VerilogPort("clk", "input", {'high': 0, 'low': 0}, None)) 
    obj3.ports.append(VerilogPort("rst_n", "input", {'high': 0, 'low': 0}, None))
    obj3.ports.append(VerilogPort("data_in", "input", {'high': 31, 'low': 0}, None))
    obj3.ports.append(VerilogPort("data_out", "output", {'high': 31, 'low': 0}, None))

    obj1.includes.append(obj2)
    obj1.includes.append(obj3)

    db.connections.append(VerilogConnection(obj1,obj1.get_port("clk_out"), obj2, obj2.get_port("clk"), None, None))
    db.connections.append(VerilogConnection(obj1,obj1.get_port("clk_out"), obj2, obj2.get_port("rst_n"), None, None))
    db.connections.append(VerilogConnection(obj1,obj1.get_port("data_out"), obj2, obj2.get_port("data_in"), None, None))
    db.connections.append(VerilogConnection(obj2,obj2.get_port("data_out"), obj3, obj3.get_port("data_in"), None, None))


    generator = WgenConfigGenerator()
    generated_code = generator.generate_by_DB(db)
    print(generated_code)

