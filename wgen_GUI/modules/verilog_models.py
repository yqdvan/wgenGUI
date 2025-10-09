class VerilogPort:
    """Verilog端口类，用于描述Verilog模块的端口信息"""
    
    def __init__(self, name, direction, width=None, source='', destination=''):
        """
        初始化Verilog端口
        
        参数:
            name (str): 端口名称
            direction (str): 端口方向，可选值: 'input', 'output', 'inout'
            width (dict): 端口位宽，格式为 {'high': int, 'low': int}，默认为1位宽
            source (str): 输入信号的源头，默认为空
            destination (str): 输出信号的目的地，默认为空
        """
        self.name = name
        self.direction = direction.lower()  # 转换为小写以确保一致性
        
        # 设置默认位宽为1位
        if width is None:
            self.width = {'high': 0, 'low': 0}
        else:
            self.width = width
        
        self.source = source
        self.destination = destination
    
    def __str__(self):
        """返回端口的字符串表示"""
        # 构建位宽字符串
        if self.width['high'] == self.width['low']:
            width_str = ''
        else:
            width_str = f"[{self.width['high']}:{self.width['low']}]"
        
        # 构建源和目的地信息
        conn_info = ''
        if self.direction in ['input', 'inout'] and self.source:
            conn_info += f" (source: {self.source})"
        if self.direction in ['output', 'inout'] and self.destination:
            conn_info += f" (dest: {self.destination})"
        
        return f"{self.direction} {self.name}{width_str}{conn_info}"
    
    def is_input(self):
        """判断是否为输入端口"""
        return self.direction == 'input'
    
    def is_output(self):
        """判断是否为输出端口"""
        return self.direction == 'output'
    
    def is_inout(self):
        """判断是否为双向端口"""
        return self.direction == 'inout'
    
    def get_bit_width(self):
        """获取端口的位宽"""
        return self.width['high'] - self.width['low'] + 1

class VerilogModule:
    """Verilog模块类，用于描述Verilog模块的信息"""
    
    def __init__(self, name, file_path=''):
        """
        初始化Verilog模块
        
        参数:
            name (str): 模块名称
            file_path (str): 模块所在文件路径，默认为空
        """
        self.name = name
        self.file_path = file_path
        self.ports = []  # 存储端口列表
    
    def add_port(self, port):
        """
        添加一个端口到模块
        
        参数:
            port (VerilogPort): 要添加的端口对象
        """
        if isinstance(port, VerilogPort):
            self.ports.append(port)
        else:
            raise TypeError("添加的端口必须是VerilogPort类型")
    
    def get_ports_by_direction(self, direction):
        """
        获取指定方向的端口列表
        
        参数:
            direction (str): 端口方向，可选值: 'input', 'output', 'inout'
        
        返回:
            list: 指定方向的端口列表
        """
        direction = direction.lower()
        return [port for port in self.ports if port.direction == direction]
    
    def get_input_ports(self):
        """获取所有输入端口"""
        return self.get_ports_by_direction('input')
    
    def get_output_ports(self):
        """获取所有输出端口"""
        return self.get_ports_by_direction('output')
    
    def get_inout_ports(self):
        """获取所有双向端口"""
        return self.get_ports_by_direction('inout')
    
    def get_port(self, port_name):
        """
        根据端口名称获取端口对象
        
        参数:
            port_name (str): 端口名称
        
        返回:
            VerilogPort or None: 找到的端口对象，如果未找到则返回None
        """
        for port in self.ports:
            if port.name == port_name:
                return port
        return None
    
    def __str__(self):
        """返回模块的字符串表示"""
        result = f"module {self.name}(\n"
        
        # 获取所有端口名称
        port_names = [port.name for port in self.ports]
        
        # 格式化端口列表
        if port_names:
            result += f"  {', '.join(port_names)}"
        
        result += "\n);\n\n"
        
        # 添加端口声明
        for port in self.ports:
            result += f"  {port}\n"
        
        result += "\nendmodule"
        
        return result
    
    def get_connections_summary(self):
        """获取连接摘要信息"""
        result = f"Module: {self.name}\n"
        result += "Connections:\n"
        
        # 输入端口连接信息
        for port in self.get_input_ports():
            if port.source:
                result += f"  Input {port.name} <- {port.source}\n"
            else:
                result += f"  Input {port.name} (unconnected)\n"
        
        # 输出端口连接信息
        for port in self.get_output_ports():
            if port.destination:
                result += f"  Output {port.name} -> {port.destination}\n"
            else:
                result += f"  Output {port.name} (unconnected)\n"
        
        # 双向端口连接信息
        for port in self.get_inout_ports():
            source_info = f"source: {port.source}" if port.source else "no source"
            dest_info = f"dest: {port.destination}" if port.destination else "no dest"
            result += f"  Inout {port.name} ({source_info}, {dest_info})\n"
        
        return result

class VerilogConnection:
    """Verilog连接类，用于描述两个模块之间的连接"""
    
    def __init__(self, source_module, source_port, dest_module, dest_port):
        """
        初始化Verilog连接
        
        参数:
            source_module (str): 源模块名称
            source_port (str): 源模块端口名称
            dest_module (str): 目标模块名称
            dest_port (str): 目标模块端口名称
        """
        self.source_module = source_module
        self.source_port = source_port
        self.dest_module = dest_module
        self.dest_port = dest_port
    
    def __str__(self):
        """返回连接的字符串表示"""
        return f"{self.source_module}.{self.source_port} -> {self.dest_module}.{self.dest_port}"

class VerilogModuleCollection:
    """Verilog模块集合类，用于管理多个Verilog模块"""
    
    def __init__(self):
        """初始化模块集合"""
        self.modules = []  # 存储模块列表
        self.connections = []  # 存储模块之间的连接
    
    def add_module(self, module):
        """
        添加一个模块到集合
        
        参数:
            module (VerilogModule): 要添加的模块对象
        """
        if isinstance(module, VerilogModule):
            self.modules.append(module)
        else:
            raise TypeError("添加的模块必须是VerilogModule类型")
    
    def get_module(self, module_name):
        """
        根据模块名称获取模块对象
        
        参数:
            module_name (str): 模块名称
        
        返回:
            VerilogModule or None: 找到的模块对象，如果未找到则返回None
        """
        for module in self.modules:
            if module.name == module_name:
                return module
        return None
    
    def add_connection(self, source_module, source_port, dest_module, dest_port):
        """
        添加模块之间的连接
        
        参数:
            source_module (str): 源模块名称
            source_port (str): 源模块端口名称
            dest_module (str): 目标模块名称
            dest_port (str): 目标模块端口名称
        """
        # 创建连接对象
        connection = VerilogConnection(source_module, source_port, dest_module, dest_port)
        self.connections.append(connection)
        
        # 更新端口的源和目的地信息
        source_mod = self.get_module(source_module)
        dest_mod = self.get_module(dest_module)
        
        if source_mod and dest_mod:
            source_port_obj = source_mod.get_port(source_port)
            dest_port_obj = dest_mod.get_port(dest_port)
            
            if source_port_obj and dest_port_obj:
                # 源端口是输出端口或双向端口
                if source_port_obj.is_output() or source_port_obj.is_inout():
                    source_port_obj.destination = f"{dest_module}.{dest_port}"
                
                # 目标端口是输入端口或双向端口
                if dest_port_obj.is_input() or dest_port_obj.is_inout():
                    dest_port_obj.source = f"{source_module}.{source_port}"
    
    def get_connections_for_module(self, module_name):
        """
        获取与指定模块相关的所有连接
        
        参数:
            module_name (str): 模块名称
        
        返回:
            list: 与指定模块相关的连接列表
        """
        return [conn for conn in self.connections \
                if conn.source_module == module_name or conn.dest_module == module_name]
    
    def get_hierarchy_summary(self):
        """获取模块层次结构摘要"""
        result = "Module Hierarchy:\n"
        
        # 打印每个模块及其端口
        for module in self.modules:
            result += f"\n{module.name}:\n"
            
            # 输入端口
            input_ports = module.get_input_ports()
            if input_ports:
                result += "  Inputs:\n"
                for port in input_ports:
                    result += f"    {port.name}{' (connected)' if port.source else ' (unconnected)'}\n"
            
            # 输出端口
            output_ports = module.get_output_ports()
            if output_ports:
                result += "  Outputs:\n"
                for port in output_ports:
                    result += f"    {port.name}{' (connected)' if port.destination else ' (unconnected)'}\n"
            
            # 双向端口
            inout_ports = module.get_inout_ports()
            if inout_ports:
                result += "  Inouts:\n"
                for port in inout_ports:
                    connected = port.source or port.destination
                    result += f"    {port.name}{' (connected)' if connected else ' (unconnected)'}\n"
        
        # 打印连接信息
        if self.connections:
            result += "\nConnections:\n"
            for conn in self.connections:
                result += f"  {conn}\n"
        
        return result