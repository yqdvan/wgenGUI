class VerilogPort:
    """Verilog端口类，用于描述Verilog模块的端口信息"""
    
    def __init__(self, name, direction, width=None, source=None, father_module=None):
        """
        初始化Verilog端口
        
        参数:
            name (str): 端口名称
            direction (str): 端口方向，可选值: 'input', 'output', 'inout'
            width (dict): 端口位宽，格式为 {'high': int, 'low': int}，默认为1位宽
            source (VerilogPort or None): 输入信号的源头端口实例，默认为None
        """
        self.name = name
        self.direction = direction.lower()  # 转换为小写以确保一致性
        self.father_module:VerilogModule = father_module
        
        # 设置默认位宽为1位
        if width is None:
            self.width = {'high': 0, 'low': 0}
        else:
            self.width = width
        
        self.source = source
        self.destinations: list[VerilogPort] = []  # 存储多个目标端口
    
    def __str__(self):
        """返回端口的字符串表示"""
        # 构建位宽字符串
        if self.width['high'] == self.width['low']:
            width_str = '[0:0]'
        else:
            width_str = f"[{self.width['high']}:{self.width['low']}]"
        
        # 构建源和目的地信息
        source_info = ''
        if self.direction in ['input', 'inout'] and self.source:
            source_module = self.source.father_module if self.source.father_module is None else self.source.father_module
            source_info += f" (source: {source_module.name}.{self.source.name if self.source else 'None'})"
        
        dest_info = ''
        if self.direction in ['output', 'inout'] and self.destinations:
            dest_info += "port loads:\n"
            for dest_port in self.destinations:
                dest_module = dest_port.father_module if dest_port.father_module is None else dest_port.father_module
                dest_info += f"    {dest_module.name}.{dest_port.name}\n"

        return f"father md: {self.father_module.name}\nport type: {self.direction}\nport name: {self.name}{width_str}\n{source_info}\n{dest_info}"

  
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

    def get_port_full_name(self):
        """获取端口的全名，包括模块名称"""
        # 这个方法应该由所属的模块调用时提供完整信息
        # 这里返回默认的名称表示
        return self.name

class VerilogModule:
    """Verilog模块类，用于描述Verilog模块的信息"""
    
    def __init__(self, name, file_path='', module_def_name=''):
        """
        初始化Verilog模块
        
        参数:
            name (str): 模块名称
            file_path (str): 模块所在文件路径，默认为空字符串
            module_def_name (str): 模块定义名称，默认为空字符串
        """
        self.name = name
        self.file_path = file_path
        self.module_def_name = module_def_name
        self.ports:list[VerilogPort] = []  # 存储端口列表
        
        # 模块包含关系(yaml 中定义的包含关系)
        self.includes:list[VerilogModule] = []  # 存储包含的模块对象
        self.top_module:VerilogModule = None  # 指向顶级模块的引用
        self.need_gen:bool = False  # 是否需要生成该模块的Verilog代码
    
    def add_port(self, port):
        """
        添加一个端口到模块
        
        参数:
            port (VerilogPort): 要添加的端口对象
        """
        if isinstance(port, VerilogPort):
            self.ports.append(port)
            port.father_module = self  # 记录端口所属模块
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
                # 获取源端口所在模块信息
                source_module_name = port.source.father_module.name if port.source.father_module else 'unknown_module'
                result += f"  Input {port.name} <- {source_module_name}.{port.source.name}\n"
            else:
                result += f"  Input {port.name} (unconnected)\n"
        
        # 输出端口连接信息
        for port in self.get_output_ports():
            if port.destinations:
                # 获取所有目标端口所在模块信息
                for dest_port in port.destinations:
                    dest_module_name = dest_port.father_module.name if dest_port.father_module else 'unknown_module'
                    result += f"  Output {port.name} -> {dest_module_name}.{dest_port.name}\n"
            else:
                result += f"  Output {port.name} (unconnected)\n"
        
        # 双向端口连接信息
        for port in self.get_inout_ports():
            source_info = f"source: {port.source.__module_name}.{port.source.name}" if port.source else "no source"
            if port.destinations:
                dest_info_list = [f"{dest_port.__module_name}.{dest_port.name}" for dest_port in port.destinations]
                dest_info = f"dests: {', '.join(dest_info_list)}"
            else:
                dest_info = "no dest"
            result += f"  Inout {port.name} ({source_info}, {dest_info})\n"
        
        return result

class VerilogConnection:
    """Verilog连接类，用于描述两个模块之间的连接"""
    
    def __init__(self, source_module, source_port, dest_module, dest_port, source_bit_range=None, dest_bit_range=None):
        """
        初始化Verilog连接
        
        参数:
            source_module (VerilogModule): 源模块实例
            source_port (VerilogPort): 源端口实例
            dest_module (VerilogModule): 目标模块实例
            dest_port (VerilogPort): 目标端口实例
            source_bit_range (dict, optional): 源端口使用的位范围，格式为 {'high': int, 'low': int}
            dest_bit_range (dict, optional): 目标端口使用的位范围，格式为 {'high': int, 'low': int}
        """
        # 验证参数类型
        if not isinstance(source_port, VerilogPort):
            raise TypeError("源端口必须是VerilogPort类型")
        if not isinstance(dest_port, VerilogPort):
            raise TypeError("目标端口必须是VerilogPort类型")
            
        # 验证端口方向是否兼容
        if not (source_port.is_output() or source_port.is_inout()):
            raise ValueError(f"源端口 '{source_port.name}' 必须是输出或双向端口")
        if not (dest_port.is_input() or dest_port.is_inout()):
            raise ValueError(f"目标端口 '{dest_port.name}' 必须是输入或双向端口")
        
        self.source_port = source_port
        self.dest_port = dest_port
        
        # 设置源端口的位范围，如果未提供则使用整个端口位宽
        if source_bit_range is None:
            self.source_bit_range = source_port.width.copy()
        else:
            # 验证位范围是否有效
            self._validate_bit_range(source_bit_range, source_port.width)
            self.source_bit_range = source_bit_range
        
        # 设置目标端口的位范围，如果未提供则使用整个端口位宽
        if dest_bit_range is None:
            self.dest_bit_range = dest_port.width.copy()
        else:
            # 验证位范围是否有效
            self._validate_bit_range(dest_bit_range, dest_port.width)
            self.dest_bit_range = dest_bit_range
            
        # 记录端口所属模块名称，方便显示
        if hasattr(source_module, 'name'):
            self.source_module_name = source_module.name
        else:
            self.source_module_name = 'unknown_module'
            
        if hasattr(dest_module, 'name'):
            self.dest_module_name = dest_module.name
        else:
            self.dest_module_name = 'unknown_module'
    
    def _validate_bit_range(self, bit_range, port_width):
        """
        验证位范围是否在端口位宽范围内
        
        参数:
            bit_range (dict): 要验证的位范围
            port_width (dict): 端口的位宽范围
            
        异常:
            ValueError: 如果位范围无效
        """
        if not isinstance(bit_range, dict) or 'high' not in bit_range or 'low' not in bit_range:
            raise ValueError("位范围必须是包含'high'和'low'键的字典")
            
        if bit_range['high'] < bit_range['low']:
            raise ValueError("位范围的high必须大于等于low")
            
        if bit_range['high'] > port_width['high'] or bit_range['low'] < port_width['low']:
            raise ValueError(f"位范围必须在端口位宽范围内 [{port_width['high']}:{port_width['low']}]")
    
    def __str__(self):
        """返回连接的字符串表示"""
        # 构建源端口位范围字符串
        if self.source_bit_range['high'] == self.source_bit_range['low']:
            source_range_str = ''
        else:
            source_range_str = f"[{self.source_bit_range['high']}:{self.source_bit_range['low']}]"
        
        # 构建目标端口位范围字符串
        if self.dest_bit_range['high'] == self.dest_bit_range['low']:
            dest_range_str = ''
        else:
            dest_range_str = f"[{self.dest_bit_range['high']}:{self.dest_bit_range['low']}]"
        
        # 如果位范围与端口原始位宽不同，则显示位范围
        source_full_name = f"{self.source_module_name}.{self.source_port.name}"
        dest_full_name = f"{self.dest_module_name}.{self.dest_port.name}"
        
        # 只有当使用部分位宽时才显示位范围
        source_str = source_full_name
        dest_str = dest_full_name
        
        if self.source_bit_range != self.source_port.width:
            source_str += source_range_str
        if self.dest_bit_range != self.dest_port.width:
            dest_str += dest_range_str
        
        return f"{source_str} -> {dest_str}"

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
            # 确保模块名称唯一
            if any(m.name == module.name for m in self.modules):
                raise ValueError(f"模块名称 '{module.name}' 已存在")
            
            # 为端口添加模块名称属性，方便在连接时识别
            for port in module.ports:
                port.__module_name = module.name
                
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
    
    def connect_port(self, from_port:VerilogPort, to_port: VerilogPort, 
                     source_bit_range=None, dest_bit_range=None):
        """
        连接两个端口
        
        参数:
            from_port (VerilogPort): 源端口
            to_port (VerilogPort): 目标端口
            source_bit_range : 源端口使用的位范围 width={'high': 7, 'low': 0})
            dest_bit_range : 目标端口使用的位范围 width={'high': 7, 'low': 0})
        """
        # 如果bit_range为空，使用端口的width
        if source_bit_range is None:
            source_bit_range = from_port.width
        if dest_bit_range is None:
            dest_bit_range = to_port.width
        
        # 检查源端口和目标端口的bit_range的high-low值是否相等
        source_bit_width = source_bit_range['high'] - source_bit_range['low']
        dest_bit_width = dest_bit_range['high'] - dest_bit_range['low']
        
        if source_bit_width != dest_bit_width:
            raise ValueError(f"源端口位宽 ({source_bit_width + 1}) 与目标端口位宽 ({dest_bit_width + 1}) 不匹配")
        
        # 获取端口和模块信息
        source_port_name = from_port.name
        dest_port_name = to_port.name
        source_module_name = from_port.father_module.name
        dest_module_name = to_port.father_module.name   

        # 执行连接
        self.add_connection(source_module_name, source_port_name, dest_module_name, dest_port_name,
                            source_bit_range, dest_bit_range)


    def add_connection(self, source_module_name, source_port_name, dest_module_name, dest_port_name, 
                       source_bit_range=None, dest_bit_range=None):
        """
        添加模块之间的连接
        
        参数:
            source_module_name (str): 源模块名称
            source_port_name (str): 源模块端口名称
            dest_module_name (str): 目标模块名称
            dest_port_name (str): 目标模块端口名称
            source_bit_range (dict, optional): 源端口使用的位范围
            dest_bit_range (dict, optional): 目标端口使用的位范围
        """
        # 获取源模块和目标模块
        source_mod = self.get_module(source_module_name)
        dest_mod = self.get_module(dest_module_name)
        
        if not source_mod:
            raise ValueError(f"未找到源模块 '{source_module_name}'")
        if not dest_mod:
            raise ValueError(f"未找到目标模块 '{dest_module_name}'")
        
        # 获取源端口和目标端口
        source_port = source_mod.get_port(source_port_name)
        dest_port = dest_mod.get_port(dest_port_name)
        
        if not source_port:
            raise ValueError(f"在模块 '{source_module_name}' 中未找到端口 '{source_port_name}'")
        if not dest_port:
            raise ValueError(f"在模块 '{dest_module_name}' 中未找到端口 '{dest_port_name}'")
        
        # 创建连接对象
        connection = VerilogConnection(
            source_module=source_mod,
            source_port=source_port,
            dest_module=dest_mod,
            dest_port=dest_port,
            source_bit_range=source_bit_range,
            dest_bit_range=dest_bit_range
        )
        self.connections.append(connection)
        
        # 更新端口的源和目的地信息
        # 源端口是输出端口或双向端口
        if source_port.is_output() or source_port.is_inout():
            # 将目标端口添加到源端口的destinations列表中
            if dest_port not in source_port.destinations:
                source_port.destinations.append(dest_port)
        
        # 目标端口是输入端口或双向端口
        if dest_port.is_input() or dest_port.is_inout():
            dest_port.source = source_port
    

    def remove_master_port_connections(self, master_port: VerilogPort):
        """
        删除主端口的连接
        
        参数:
            master_port (VerilogPort): 主端口
        
        返回:
            str: 操作结果消息
        """
        ans = False
        message_str = ""
        
        # 检查主端口是否有连接
        if not master_port.destinations:
            message_str = f"主端口 {master_port.name} 没有load!!"
            return message_str
        
        # 从每个目标端口的destinations列表中移除主端口
        for dest_port in master_port.destinations:
            if master_port is dest_port.source:
                self.remove_slave_port_connection(dest_port)
                ans = True
            else:
                message_str = f"主端口 {master_port.name} load {dest_port.name}, BUT NOT FROM IT !!!"
                ans = False
                break
        
        # 清空主端口的destinations列表
        if ans:
            master_port.destinations.clear()
            # message_str = f"成功删除主端口 {master_port.name} 的所有连接"
        
        return message_str


    def remove_slave_port_connection(self, slave_port: VerilogPort):
        """
        删除从端口的连接
        
        参数:
            slave_port (VerilogPort): 从端口
        
        返回:
            str: 操作结果消息
        """
        message_str = ""
        # 检查从端口是否有连接
        if not slave_port.source:
            message_str = f"从端口 {slave_port.name} 没有driver!!"
            return message_str
        
        # 先获取源端口信息，再移除从端口的源引用
        source_port = slave_port.source
        source_module_name = source_port.father_module.name
        source_port_name = source_port.name
        dest_module_name = slave_port.father_module.name
        dest_port_name = slave_port.name
        
        # 移除从端口的源引用
        slave_port.source = None
        
        # 从源端口的destinations列表中移除从端口
        if slave_port in source_port.destinations:
            ans = self.remove_connection(source_module_name, source_port_name, dest_module_name, dest_port_name)
            if ans:
                # message_str = f"成功删除从端口 {slave_port.name} 的连接"
                message_str = ""
            else:
                message_str = f"删除从端口 {slave_port.name} 的连接失败"
        else:
            message_str = f"从端口 {slave_port.name} 不在源端口的连接列表中"
        
        return message_str


    def remove_connection(self, source_module_name, source_port_name, dest_module_name, dest_port_name):
        """
        删除模块之间的连接
        
        参数:
            source_module_name (str): 源模块名称
            source_port_name (str): 源模块端口名称
            dest_module_name (str): 目标模块名称
            dest_port_name (str): 目标模块端口名称
        
        返回:
            bool: 如果成功删除连接则返回True，否则返回False
        """
        # 查找匹配的连接
        connection_to_remove = None
        for conn in self.connections:
            if (conn.source_module_name == source_module_name and 
                conn.source_port.name == source_port_name and 
                conn.dest_module_name == dest_module_name and 
                conn.dest_port.name == dest_port_name):
                connection_to_remove = conn
                break
        
        if not connection_to_remove:
            return False
        
        # 更新端口的源和目的地信息
        source_port = connection_to_remove.source_port
        dest_port = connection_to_remove.dest_port
        
        # 移除源端口的目的地引用
        if dest_port in source_port.destinations:
            source_port.destinations.remove(dest_port)
        
        # 移除目标端口的源引用
        if dest_port.source == source_port:
            dest_port.source = None
        
        # 从连接列表中删除连接
        self.connections.remove(connection_to_remove)
        return True
    
    def get_connections_for_module(self, module_name):
        """
        获取与指定模块相关的所有连接
        
        参数:
            module_name (str): 模块名称
        
        返回:
            list: 与指定模块相关的连接列表
        """
        module = self.get_module(module_name)
        if not module:
            return []
        
        # 检查连接的源端口或目标端口是否属于指定模块
        return [conn for conn in self.connections \
                if (conn.source_module_name == module_name or conn.dest_module_name == module_name)]
    
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
                    result += f"    {port.name}{' (connected)' if port.destinations else ' (unconnected)'}\n"
            
            # 双向端口
            inout_ports = module.get_inout_ports()
            if inout_ports:
                result += "  Inouts:\n"
                for port in inout_ports:
                    connected = port.source or port.destinations
                    result += f"    {port.name}{' (connected)' if connected else ' (unconnected)'}\n"
        
        # 打印连接信息
        if self.connections:
            result += "\nConnections:\n"
            for conn in self.connections:
                result += f"  {conn}\n"
        
        return result
        
    def to_dict(self):
        """将模块集合转换为可序列化的字典
        
        返回:
            dict: 包含所有模块和连接信息的字典
        """
        # 首先序列化所有模块
        modules_dict = []
        for module in self.modules:
            module_info = {
                'name': module.name,
                'file_path': module.file_path,
                'module_def_name': module.module_def_name,
                'ports': [],
                'includes': [included_module.name for included_module in module.includes],
                'top_module_name': module.top_module.name if module.top_module else None,
                'need_gen': module.need_gen
            }
            
            # 序列化模块的所有端口
            for port in module.ports:
                port_info = {
                    'name': port.name,
                    'direction': port.direction,
                    'width': port.width
                }
                module_info['ports'].append(port_info)
            
            modules_dict.append(module_info)
        
        # 然后序列化所有连接
        connections_dict = []
        for conn in self.connections:
            conn_info = {
                'source_module_name': conn.source_module_name,
                'source_port_name': conn.source_port.name,
                'dest_module_name': conn.dest_module_name,
                'dest_port_name': conn.dest_port.name,
                'source_bit_range': conn.source_bit_range,
                'dest_bit_range': conn.dest_bit_range
            }
            connections_dict.append(conn_info)
        
        # 返回完整的字典表示
        return {
            'modules': modules_dict,
            'connections': connections_dict
        }
    
    def to_json(self):
        """将模块集合直接转换为JSON字符串
        
        返回:
            str: 包含所有模块和连接信息的JSON字符串
        """
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data_dict):
        """从字典中创建VerilogModuleCollection对象
        
        参数:
            data_dict (dict): 包含模块和连接信息的字典
            
        返回:
            VerilogModuleCollection: 重建的模块集合对象
        """
        # 创建空的模块集合
        collection = cls()
        
        # 首先重建所有模块
        module_map = {}
        for module_info in data_dict.get('modules', []):
            module = VerilogModule(
                name=module_info['name'],
                file_path=module_info.get('file_path', ''),
                module_def_name=module_info.get('module_def_name', '')
            )
            
            # 重建模块的所有端口
            for port_info in module_info.get('ports', []):
                port = VerilogPort(
                    name=port_info['name'],
                    direction=port_info['direction'],
                    width=port_info.get('width', {'high': 0, 'low': 0})
                )
                module.add_port(port)
            
            # 保存模块信息以便后续建立引用关系
            module_info['__module_object'] = module
            collection.add_module(module)
            module_map[module.name] = module
        
        # 建立模块之间的引用关系（includes和top_module）
        for module_info in data_dict.get('modules', []):
            module = module_info['__module_object']
            
            # 恢复includes引用
            for included_module_name in module_info.get('includes', []):
                if included_module_name in module_map:
                    module.includes.append(module_map[included_module_name])
            
            # 恢复top_module引用
            top_module_name = module_info.get('top_module_name')
            if top_module_name and top_module_name in module_map:
                module.top_module = module_map[top_module_name]
            
            # 恢复need_gen属性
            module.need_gen = module_info.get('need_gen', False)
        
        # 然后重建所有连接
        for conn_info in data_dict.get('connections', []):
            try:
                # 使用现有的add_connection方法来确保所有验证和引用都正确设置
                collection.add_connection(
                    source_module_name=conn_info['source_module_name'],
                    source_port_name=conn_info['source_port_name'],
                    dest_module_name=conn_info['dest_module_name'],
                    dest_port_name=conn_info['dest_port_name'],
                    source_bit_range=conn_info.get('source_bit_range'),
                    dest_bit_range=conn_info.get('dest_bit_range')
                )
            except Exception as e:
                # 如果连接创建失败，打印错误信息但继续处理其他连接
                print(f"警告: 无法创建连接 {conn_info['source_module_name']}.{conn_info['source_port_name']} -> {conn_info['dest_module_name']}.{conn_info['dest_port_name']}: {e}")
        
        return collection
    
    @classmethod
    def from_json(cls, json_str):
        """从JSON字符串中创建VerilogModuleCollection对象
        
        参数:
            json_str (str): 包含模块和连接信息的JSON字符串
            
        返回:
            VerilogModuleCollection: 重建的模块集合对象
        """
        import json
        data_dict = json.loads(json_str)
        return cls.from_dict(data_dict)
    
    def save_to_file(self, file_path):
        """将模块集合保存到文件
        
        参数:
            file_path (str): 保存文件的路径
            
        返回:
            bool: 保存是否成功
        """
        try:
            import json
            
            # 获取模块集合的字典表示
            collection_dict = self.to_dict()
            
            # 将字典保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collection_dict, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"错误: 无法保存模块集合到文件 {file_path}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path):
        """从文件加载模块集合
        
        参数:
            file_path (str): 加载文件的路径
            
        返回:
            VerilogModuleCollection or None: 重建的模块集合对象，如果加载失败则返回None
        """
        try:
            import json
            
            # 从文件读取字典
            with open(file_path, 'r', encoding='utf-8') as f:
                collection_dict = json.load(f)
            
            # 从字典创建模块集合
            return cls.from_dict(collection_dict)
        except Exception as e:
            print(f"错误: 无法从文件 {file_path} 加载模块集合: {e}")
            return None