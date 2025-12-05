from typing import Any, Optional, List

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
        self.direction:str = direction.lower()  # 转换为小写以确保一致性
        self.father_module:VerilogModule = father_module
        
        # 设置默认位宽为1位
        self.width:dict = None
        if width is None:
            self.width = {'high': 0, 'low': 0}
        else:
            self.width = width
        
        self.source:VerilogPort = source # 在v2.0.0版本后，source变相的被connection替代，以后不要再访问了
        self.connection:VerilogConnection = None # 存储source为多个连接对象时的连接对象
        self.destinations: list[VerilogPort] = []  # 存储多个目标端口
    
    def __str__(self):
        """返回端口的字符串表示"""
        # 构建位宽字符串
        if self.width['high'] == self.width['low']:
            width_str = '[0:0]'
        else:
            width_str = f"[{self.width['high']}:{self.width['low']}]"
        
        # 构建源和目的地信息
        source_info = '\nsource_info:\n'
        dest_info = '\ndestination_info:\n'

        # if not self.father_module.need_gen:
        #     if self.direction in ['input', 'inout'] and self.source:
        #         source_module = self.source.father_module if self.source.father_module is None else self.source.father_module
        #         if isinstance(self.connection, VerilogConnection):
        #             source_info += f" (source: {source_module.name}.{self.connection.name}[{self.connection.source_bit_range['high']}:{self.connection.source_bit_range['low']}])"
        #         elif isinstance(self.connection, VerilogMergeConnection):
        #             for source_port in self.connection.source_port_list:
        #                 source_info += f"  source: {source_module.name}.{source_port.name }[{source_port.width['high']}:{source_port.width['low']}] \n"
            
        #     if self.direction in ['output', 'inout'] and self.destinations:
        #         dest_info += "port loads:\n"
        #         for dest_port in self.destinations:
        #             dest_module = dest_port.father_module if dest_port.father_module is None else dest_port.father_module
        #             dest_info += f"    {dest_module.name}.{dest_port.name}\n"
        # else: # need gen
            
        #     if self.source:
        #         source_module = self.source.father_module if self.source.father_module is None else self.source.father_module
        #         source_info += f" (source: {source_module.name}.{self.source.name if self.source else 'None'})"
        #     if self.destinations:
        #         for dest_port in self.destinations:
        #             dest_module = dest_port.father_module if dest_port.father_module is None else dest_port.father_module
        #             dest_info += f"    {dest_module.name}.{dest_port.name}\n"            
        
        # 1. make source info
        if isinstance(self.connection, VerilogMergeConnection):
            source_info += f"  source is merged by:\n"
            for source_port in self.connection.source_port_list:
                source_info += f"    {source_port.father_module.name}.{source_port.name }[{source_port.width['high']}:{source_port.width['low']}] \n"
        elif isinstance(self.connection, VerilogConnection):
            source_info += f"  source: {self.connection.source_port.father_module.name}.{self.connection.source_port.name}[{self.connection.source_bit_range['high']}:{self.connection.source_bit_range['low']}] \n"

        # 2. make destion info
        dest_info += "  port load(s):\n"
        for dest_port in self.destinations:
            dest_module = dest_port.father_module if dest_port.father_module is None else dest_port.father_module
            dest_info += f"    {dest_module.name}.{dest_port.name}\n"

        return f"father md: {self.father_module.name}\nport type: {self.direction}\nport name: {self.name}{width_str}\n{source_info}\n{dest_info}"

    def get_port_info(self) -> str:
        """获取端口的信息"""
        # 返回 格式为 port type, module_name.portname, port width   
        return f"{self.direction}, {self.father_module.name}.{self.name}, {self.get_width_value()} bit(s)"

    def get_width_value(self) -> int:
        """获取端口的位宽"""
        return self.width['high'] - self.width['low'] + 1

    def get_bit_range(self):
        """获取端口的位宽范围字符串"""
        return {'high': self.width['high'], 'low': self.width['low']}

    def is_input(self):
        """判断是否为输入端口"""
        return self.direction == 'input'
    
    def is_output(self):
        """判断是否为输出端口"""
        return self.direction == 'output'
    
    def is_inout(self):
        """判断是否为双向端口"""
        return self.direction == 'inout'
    
    # def get_bit_width(self):
    #     """获取端口的位宽"""
    #     return self.width['high'] - self.width['low'] + 1

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
        self.name = name # is instance name
        self.file_path = file_path
        self.module_def_name = module_def_name
        self.ports:list[VerilogPort] = []  # 存储端口列表
        self.parameters:dict[str, int] = {}  # 存储参数，键为字符串，值为整数
        
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

    def add_ports(self, ports:list[VerilogPort]):
        """
        添加多个端口到模块
        
        参数:
            ports (list): 要添加的端口对象列表
        """
        for port in ports:
            self.add_port(port)

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
    
    def get_port(self, port_name, port_list:list[VerilogPort] = None):
        """
        根据端口名称获取端口对象
        
        参数:
            port_name (str): 端口名称
        
        返回:
            VerilogPort or None: 找到的端口对象，如果未找到则返回None
        """
        if port_list is None:
            port_list = self.ports
        for port in port_list:
            if port.name == port_name:
                return port
        return None
    
    def __str__(self):
        """返回模块的字符串表示，用于日志记录"""
        result = [f"=== Verilog Module: {self.name} ==="]
        
        # 基本信息
        result.append(f"  Instance Name: {self.name}")
        if self.file_path:
            result.append(f"  File Path: {self.file_path}")
        if self.module_def_name:
            result.append(f"  Module Definition Name: {self.module_def_name}")
        result.append(f"  Need Generate: {self.need_gen}")
        
        # 参数信息
        if self.parameters:
            result.append("\n  Parameters:")
            for param_name, param_value in self.parameters.items():
                result.append(f"    {param_name}: {param_value}")
        else:
            result.append("\n  Parameters: None")
        
        # 端口信息
        if self.ports:
            # 统计各类端口的数量
            input_count = len(self.get_input_ports())
            output_count = len(self.get_output_ports())
            inout_count = len(self.get_inout_ports())
            
            result.append(f"\n  Ports Summary:")
            result.append(f"    Input Ports: {input_count}")
            result.append(f"    Output Ports: {output_count}")
            result.append(f"    Inout Ports: {inout_count}")
            result.append(f"    Total Ports: {len(self.ports)}")
        else:
            result.append("\n  Ports: None")
        
        # 包含关系
        if self.includes:
            result.append("\n  Included Modules:")
            for included_module in self.includes:
                result.append(f"    {included_module.name}")
        else:
            result.append("\n  Included Modules: None")
        
        # 顶级模块信息
        if self.top_module:
            result.append(f"\n  Top Module: {self.top_module.name}")
        else:
            result.append("\n  Top Module: None")
        
        result.append("=" * (len(f"=== Verilog Module: {self.name} ===") + 1))
        
        return "\n".join(result)
    
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

    def get_include_names(self):
        """获取包含的模块名称列表"""
        return [module.name for module in self.includes]

class VerilogConnection:
    """Verilog连接类，用于描述两个模块之间的连接"""
    
    def __init__(self,
            source_module:VerilogModule, 
            source_port:VerilogPort, 
            dest_module:VerilogModule, 
            dest_port:VerilogPort, 
            source_bit_range=None, 
            dest_bit_range=None
        ):
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
        # self.source_module = source_module
        # self.dest_module = dest_module
            
        # 验证端口方向是否兼容
        if not source_port.father_module.need_gen :
            if not (source_port.is_output() or source_port.is_inout()):
                raise ValueError(f"源端口 '{source_port.name}' 必须是输出或双向端口")
        if not dest_port.father_module.need_gen :
            if not (dest_port.is_input() or dest_port.is_inout()):
                raise ValueError(f"目标端口 '{dest_port.name}' 必须是输入或双向端口")
            if dest_port.source:
                raise ValueError(f"目标端口 '{dest_port.name}' 已连接到源端口 '{dest_port.source.name}'")
                # dest_port.source = None
        
        self.source_port = source_port
        self.dest_port = dest_port
        
        # # 设置源端口的位范围，如果未提供则使用整个端口位宽
        # if source_bit_range is None:
        #     self.source_bit_range = source_port.width.copy()
        # else:
        #     # 验证位范围是否有效
        #     self._validate_bit_range(source_bit_range, source_port.width)
        #     self.source_bit_range = source_bit_range
        
        # # 设置目标端口的位范围，如果未提供则使用整个端口位宽
        # if dest_bit_range is None:
        #     self.dest_bit_range = dest_port.width.copy()
        # else:
        #     # 验证位范围是否有效
        #     self._validate_bit_range(dest_bit_range, dest_port.width)
        #     self.dest_bit_range = dest_bit_range
        self.source_bit_range = source_bit_range
        self.dest_bit_range = dest_bit_range
        self._check_range()

        # 记录端口所属模块名称，方便显示
        if hasattr(source_module, 'name'):
            self.source_module_name = source_module.name
        else:
            self.source_module_name = 'unknown_module'
            
        if hasattr(dest_module, 'name'):
            self.dest_module_name = dest_module.name
        else:
            self.dest_module_name = 'unknown_module'

    def _check_range(self):
        """
        验证连接的位范围是否有效
        
        异常:
            ValueError: 如果位范围无效
        """
        # 设置源端口的位范围，如果未提供则使用整个端口位宽
        if self.source_bit_range is None:
            self.source_bit_range = self.source_port.width.copy()
        else:
            # 验证位范围是否有效
            self._validate_bit_range(self.source_bit_range, self.source_port.width)
        
        # 设置目标端口的位范围，如果未提供则使用整个端口位宽
        if self.dest_bit_range is None:
            self.dest_bit_range = self.dest_port.width.copy()
        else:
            # 验证位范围是否有效
            self._validate_bit_range(self.dest_bit_range, self.dest_port.width)
          
    def _get_width_value(self, bit_range):
        """
        计算位范围的宽度值（高索引 - 低索引 + 1）
        
        参数:
            bit_range (dict): 包含'high'和'low'键的位范围字典
            
        返回:
            int: 位范围的宽度值
        """
        return bit_range['high'] - bit_range['low'] + 1

    def _validate_bit_range(self, bit_range, port_width):
        """
        验证位范围是否在端口位宽范围内
        
        参数:
            bit_range (dict): 要验证的位范围(碎片)
            port_width (dict): 端口的位宽范围(完整)
            
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
        if self.source_bit_range['high'] == self.source_bit_range['low'] and self.source_bit_range['high'] == 0 and self.source_port.get_width_value() == 1:
            source_range_str = ''
        else:
            source_range_str = f"[{self.source_bit_range['high']}:{self.source_bit_range['low']}]"
        
        # 构建目标端口位范围字符串
        if self.dest_bit_range['high'] == self.dest_bit_range['low'] and self.dest_bit_range['high'] == 0 and self.dest_port.get_width_value() == 1:
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

class VerilogMergeConnection(VerilogConnection):
    def __init__(self, 
            source_module:VerilogModule, 
            source_port:VerilogPort, 
            dest_module:VerilogModule, 
            dest_port:VerilogPort, 
            source_bit_range=None, 
            dest_bit_range=None,
            merge_type: str = 'joint',
            source_port_list: list[VerilogPort] = [],
            source_range_list: list[dict] = []
        ):

        if(source_port_list == []):
            raise ValueError("source_port_list cannot empty!")
        self.type = merge_type # can extend OR XOR AND OR ...
        self.source_port_list = source_port_list
        self.source_range_list = source_range_list
        self.gui_data_list = []

        # 用list中的第一个端口作为源端口    
        super().__init__(
            source_module=source_module,
            source_port=source_port,
            dest_module=dest_module,
            dest_port=dest_port,
            source_bit_range=source_bit_range,
            dest_bit_range=dest_bit_range
        )

    # 重写_check_range方法，验证每个源端口的位范围是否有效
    def _check_range(self) -> bool:
        """
        验证每个源端口的位范围是否有效
        
        返回:
            bool: 如果所有位范围有效则返回True，否则返回False
        """
        for i in range(len(self.source_port_list)):
            if self.source_range_list[i] is None:
                self.source_range_list[i] = self.source_port_list[i].width.copy()
            else:
                self._validate_bit_range(self.source_range_list[i], self.source_port_list[i].width)

        # 设置目标端口的位范围，如果未提供则使用整个端口位宽
        if self.dest_bit_range is None:
            self.dest_bit_range = self.dest_port.width.copy()
        else:
            # 验证位范围是否有效
            self._validate_bit_range(self.dest_bit_range, self.dest_port.width)   

        return True

    # 重写__str__方法，显示合并连接的信息
    def __str__(self):
        """返回合并连接的字符串表示"""
        #遍历 self.source_port_list 和 self.source_range_list 构建 port.father_module.name . port.name [range['high':range['low']]]
        source_str = ""
        for i in range(len(self.source_port_list)):
            source_str += f"{self.source_port_list[i].father_module.name}.{self.source_port_list[i].name} [{self.source_range_list[i]['high']}:{self.source_range_list[i]['low']}]"
            if i < len(self.source_port_list) - 1:
                source_str += ", "

        return f"{{{source_str}}} -> {self.dest_module_name}.{self.dest_port.name} [{self.dest_bit_range['high']}:{self.dest_bit_range['low']}]"

class VerilogModuleCollection:
    """Verilog模块集合类，用于管理多个Verilog模块"""
    
    def __init__(self):
        """初始化模块集合"""
        self.modules: list[VerilogModule] = []  # 存储模块列表
        self.connections: list[VerilogConnection] = []  # 存储模块之间的连接

        self.tie_0_port:VerilogPort = VerilogPort("tie_0", "output", {'high': 32767, 'low': 0})  # 存储Tie-0端口
        self.tie_1_port:VerilogPort = VerilogPort("tie_1", "output", {'high': 32767, 'low': 0})  # 存储Tie-1端口
        self.system_module = VerilogModule("system_module", "/empty/", "system_module")  # 存储系统模块
        self.system_module.add_port(self.tie_0_port)
        self.system_module.add_port(self.tie_1_port)
        
    def tie01_for_port(self, tie01: int, port: VerilogPort) -> str:
        ans_str = "success"
        tie_port: VerilogPort = self.tie_0_port if tie01 == 0 else self.tie_1_port

        if(port.direction == "output"):
            if port.father_module.need_gen is False :
                ans_str = f"错误：Tie-0/1端口不能连接到输出端口{port.name}\n"
                return ans_str
            elif port.source is not None:
                ans_str = f"错误：Tie-0/1端口不能连接到已连接的端口{port.name}\n"
                return ans_str
        
        if(port.direction == "input") and port.source is not None:
            ans_str = f"错误：Tie-0/1端口不能连接到已连接的输入端口{port.name}\n"
            return ans_str

        """将Tie-0/1端口连接到指定端口"""

        connection = VerilogConnection(
            source_module=self.system_module,
            source_port=tie_port,
            dest_module=port.father_module,
            dest_port=port,
            source_bit_range={'high': port.width['high'], 'low': port.width['low']},
            dest_bit_range={'high': port.width['high'], 'low': port.width['low']}
        )
        self.connections.append(connection)

        port.source = tie_port
        tie_port.destinations.append(port)
        return ans_str

    def get_all_connections_info(self)-> str:
        """获取所有连接信息"""
        # 给connections排序
        self.connections.sort(key=lambda conn: (conn.dest_module_name, conn.dest_port.name))
        return "\n".join(str(conn) for conn in self.connections)

    def get_connections_by_instance_name(self, instance_name: str)-> str:
        """根据实例名获取所有连接信息"""
        ins_obj = self.get_module(instance_name)
        if ins_obj is None:
            return f"实例名 '{instance_name}' 不存在"
        conn_list:List[VerilogConnection] = self.get_connections_obj_by_module_name(instance_name)
        
        ans_str = ""
        # conn_list:List[VerilogConnection] = []
        # for conn in self.connections:
        #     if conn.source_module_name == instance_name or conn.dest_module_name == instance_name:
        #         conn_list.append(conn)
        # conn_list.sort(key=lambda conn: (conn.source_module_name, conn.source_port.name, conn.dest_module_name, conn.dest_port.name))
        for conn in conn_list:
            ans_str += str(conn) + "\n"
        return ans_str

    def get_unconnected_ports_info(self)-> str:
        """获取所有未连接的端口信息"""
        unconnected_gen_ports: list[VerilogPort] = []
        unconnected_non_gen_ports: list[VerilogPort] = []
        for module in self.modules:
            if module.need_gen:
                for port in module.ports:
                    if not port.source and len(port.destinations) == 0:
                        unconnected_gen_ports.append(port)
            else:
                for port in module.ports:
                    if port.direction == "input" :
                        if not port.source :
                            unconnected_non_gen_ports.append(port)
                    elif port.direction == "output":
                        if len(port.destinations) == 0:
                            unconnected_non_gen_ports.append(port)
                    else: # inout
                        ans_str += f"iinot port: {port.get_port_info()} \n"

        ans_str = ""
        if unconnected_gen_ports:
            # unconnected_gen_ports按照端口direction排序
            unconnected_gen_ports.sort(key=lambda port: port.direction)
            ans_str += "未连接generated module 端口:\n" + "\n".join(port.get_port_info() for port in unconnected_gen_ports) + "\n"
        else:
            ans_str += "所有generated module 端口均已连接\n"
        
        if unconnected_non_gen_ports:
            # unconnected_non_gen_ports按照端口direction排序
            unconnected_non_gen_ports.sort(key=lambda port: port.direction)
            ans_str += "\n未连接常规module 端口:\n" + "\n".join(port.get_port_info() for port in unconnected_non_gen_ports) + "\n"
        else:
            ans_str += "\n所有常规module端口均已连接\n"
        
        return ans_str

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
    
    def update_module(self, md_list: list[VerilogModule]) -> str:
        """更新模块内部信息"""
        ans_str = "update info:\n\n"
        # 0. 检查是否有模块需要更新
        if not md_list:
            ans_str += "no VerilogModule need update!"
            raise ValueError(ans_str)

        # 1. 先处理新增的module
        new_md_list = []
        for yaml_md in md_list:
            new_md = self.get_module(yaml_md.name)
            if new_md is None:
                # 1.1 检查是否在hierarchy中
                if yaml_md.top_module is None and yaml_md.includes is None:
                    raise ValueError(f"VerilogModule {yaml_md.name} is not in hierarchy and not included by other modules, can not be added.")

                # 1.2 添加新模块
                new_md = VerilogModule(yaml_md.name, yaml_md.file_path, yaml_md.module_def_name)
                new_md.add_ports(yaml_md.ports)

                self.add_module(new_md)
                new_md_list.append(new_md)

                ans_str += f"VerilogModule {yaml_md.name} add success;\n"
                ans_str += f"{yaml_md.module_def_name} port info:\n"
                for port in new_md.ports:       
                    ans_str += port.get_port_info() + "\n"
        # 1.3 处理新模块的top和include(防止有依赖关系的module也是新加的，因此加完了之后再处理hierarchy)
        if new_md_list is not None:
            ans_str += "\n"
            for new_md in new_md_list :
                yaml_md = self.get_module( new_md.name, md_list)
                if(yaml_md.top_module is not None):
                    new_top = self.get_module(yaml_md.top_module.name)
                    new_md.top_module = new_top
                    if new_md not in new_top.includes:
                        new_top.includes.append(new_md)
                        ans_str += f"VerilogModule {new_top.name} update include {new_md.name};\n"
                else:
                    raise ValueError(f"VerilogModule {new_md.name} top_module is not in hierarchy, can not be added.") # add other soc_chip is illegal

                if(yaml_md.includes is not None):
                    for include in yaml_md.includes:
                        include_md = self.get_module(include.name)
                        if include_md is None:
                            raise ValueError(f"VerilogModule {new_md.name} include {include.name} is not in hierarchy, can not be added.")
                        if include_md not in new_md.includes:   
                            new_md.includes.append(include_md)
                            ans_str += f"VerilogModule {new_md.name} update include {include_md.name};\n"
                        include_md.top_module = new_md

                ans_str += f"VerilogModule {new_md.name} include {[include.name for include in new_md.includes]};\n"
                ans_str += f"VerilogModule {new_md.name} hierarchy process done;\n"
                ans_str += new_md.__str__() + "\n"
                ans_str += "\n"

        # 2.处理已存在的module
        for module in md_list:
            self_md: VerilogModule = self.get_module(module.name)
            if self_md is not None and module.ports is not None and self_md.ports is not None:
                # 2.1 更新parameters
                self_md.parameters = module.parameters.copy()

                # 2.2 找可能新和改动的port
                for port in module.ports:
                    # 新加的端口
                    if port.name not in [p.name for p in self_md.ports]:
                        # 端口不存在，添加端口
                        self_md.add_port(port)
                        ans_str += f"VerilogModule {module.name} port {port.name} add success;\n"
                        ans_str += port.get_port_info() + "\n"
                        
                        # 如果添加的是merge connection的目标端口，确保设置了正确的连接类型
                        if port.connection and isinstance(port.connection, VerilogMergeConnection):
                            ans_str += f"VerilogModule {module.name} port {port.name} is a merge connection target, added with merge connection;\n"

                    # 已有的端口但是位宽变了
                    elif port.width != self_md.get_port(port.name).width:
                        # 端口已存在，但位宽不同，更新位宽
                        self_port: VerilogPort = self_md.get_port(port.name)
                        ans_str += f"VerilogModule {module.name} port {port.name} old width is {self_port.width};\n"
                        self_port.width = port.width
                        ans_str += f"VerilogModule {module.name} port {port.name} update to {self_port.width};\n"
                        ans_str += port.get_port_info() + "\n"
                        
                        # 如果该端口是VerilogMergeConnection的目标端口，确保所有相关源端口都知道这个变化
                        if self_port.connection and isinstance(self_port.connection, VerilogMergeConnection):
                            merge_conn = self_port.connection
                            ans_str += f"VerilogModule {module.name} port {port.name} is a merge connection target, updating all sources;\n"

                        # 删除这个端口的所有连接信息
                        ans_str += self.delete_port_connection(self_md, self_port)
                    
                    else: # 端口已存在，位宽也相等，不进行添加操作
                        # ans_str += f"VerilogModule {module.name} port {port.name} has no change;\n"
                        print(f"VerilogModule {module.name} port {port.name} has no change;")
            
                # 2.3 找可能删除了的端口
                del_port_list: list[VerilogPort] = []
                for self_port in self_md.ports:
                    if self_port.name not in [p.name for p in module.ports]:
                        # 端口不存在，删除端口
                        del_port_list.append(self_port)
                    else:
                        # 端口已存在，不进行删除操作
                        print(f"VerilogModule {module.name} port {self_port.name} not need delete;")
                if del_port_list:
                    for self_port in del_port_list:
                        # 如果该端口是merge connection的目标或源，确保正确清理所有相关连接
                        if self_port.connection and isinstance(self_port.connection, VerilogMergeConnection):
                            ans_str += f"VerilogModule {module.name} port {self_port.name} is part of a merge connection, cleaning up all related connections;\n"
                        ans_str += self.delete_port_connection(self_md, self_port)  
                        ans_str += f"VerilogModule {module.name} port {self_port.name} delete success;\n"
                        self_md.ports.remove(self_port)
            ans_str += "\n"

        # 3. 处理md_list中没有，而self.modules中有的module
        keep_list: list[VerilogModule] = []
        del_list: list[VerilogModule] = []        
        for self_md in self.modules:
            if self_md.name not in [m.name for m in md_list]:
                del_list.append(self_md)
            else:
                keep_list.append(self_md)

        # 3.1 如果被删除的md存在于 新hierarchy，直接报错
        for del_md in del_list:
            for kp_md in keep_list:
                new_kp_md = self.get_module(kp_md.name, md_list)
                if not new_kp_md:
                    raise ValueError(f"VerilogModule {new_kp_md.name} not found in md_list!")

                if new_kp_md.top_module and del_md.name == new_kp_md.top_module.name:
                    raise ValueError(f"VerilogModule {del_md.name} is top_module of {new_kp_md.name}, can not be deleted")

                if new_kp_md.includes and del_md.name in [m.name for m in new_kp_md.includes]:
                    raise ValueError(f"VerilogModule {del_md.name} is included in {new_kp_md.name}, can not be deleted")

        # 3.2 开始删除del_list中的module
        ans_str += "\n"
        for del_md in del_list:
            ans_str += f"VerilogModule {del_md.name} find {len(del_md.ports)} ports;\n"
            for port in del_md.ports:
                ans_str += self.delete_port_connection(del_md, port)
            self.modules.remove(del_md)
            ans_str += f"VerilogModule {del_md.name} is deleted, {len(del_md.ports)} ports are deleted;\n\n"
        
        # 3.3 开始删除del_md 在hierarchy中的include关系
        for kp_md in keep_list:
            for del_md in del_list:
                if del_md.name in [m.name for m in kp_md.includes]:
                    kp_md.includes.remove(del_md)
                    ans_str += f"VerilogModule {kp_md.name} remove include {del_md.name};\n"
        
        # md_list 长度
        ans_str += f"\nA total of {len(md_list)} VerilogModules were verified.\n"
        return ans_str

    def delete_port_connection(self, module: VerilogModule, port: VerilogPort) -> str:
        ans_str = ""
        # 删除这个端口的所有连接信息
        # module.source = None
        # port.destinations: list[VerilogPort] = []

        # # 删除collections中所有包含这个端口的连接,并返回删除的连接
        # deleted_conns = [conn for conn in self.connections if conn.source_port == port or conn.dest_port == port]
        # ans_str += f"VerilogModule {module.name} port {port.name} delete {len(deleted_conns)} connections;\n"
        # self.connections = [conn for conn in self.connections if conn.source_port != port and conn.dest_port != port]
        loads_num = len(port.destinations)
        if self.remove_master_port_connections(port) == "":
            ans_str += f"VerilogModule {module.name} port {port.name} delete {loads_num} destinations;\n"
        if self.remove_slave_port_connection(port) == "":
            ans_str += f"VerilogModule {module.name} port {port.name} delete 1 source;\n"
        return ans_str

    def get_module(self, module_name: str, md_list: Optional[List['VerilogModule']] = None) -> Optional['VerilogModule']:
        # 修复默认参数问题，避免使用可变默认参数
        if md_list is None:
            md_list = self.modules
        """
        根据模块名称获取模块对象
        
        参数:
            module_name (str): 模块名称
        
        返回:
            VerilogModule or None: 找到的模块对象，如果未找到则返回None
        """
        for module in md_list:
            if module.name == module_name:
                return module
        return None
      
    def add_mergeConnection(self, from_port_list: list[VerilogPort], from_range_list: list[dict],new_gui_data_list: list[list[dict]], to_port: VerilogPort):
        """
        连接多个端口到一个端口
        
        参数:
            from_port_list (list[VerilogPort]): 源端口列表
            to_port (VerilogPort): 目标端口
        """

        # 0.1 检查源端口列表是否为空
        if not from_port_list:
            raise ValueError("source port list cannot be empty")

        # 0.2 检查new_gui_data_list是否为空
        if not new_gui_data_list:
            raise ValueError("new_gui_data_list cannot be empty")

        # 0.3 to_port source 应该是空的
        if to_port.source:
            raise ValueError("target port cannot have source connection")

        # 0.4 检查new_gui_data_list的长度是否与from_port_list相同
        if len(new_gui_data_list) != len(from_port_list):
            raise ValueError("new_gui_data_list length must be same as source port list")

        # 1. 创建mergeConnection
        merge_conn = VerilogMergeConnection(
            source_module=from_port_list[0].father_module,
            source_port=from_port_list[0], 
            dest_module=to_port.father_module,
            dest_port=to_port,
            source_bit_range=from_range_list[0], 
            dest_bit_range=to_port.width, 
            merge_type='joint',
            source_port_list=from_port_list, 
            source_range_list=from_range_list
        )
        
        # 设置gui_data_list
        merge_conn.gui_data_list = new_gui_data_list
        
        self.connections.append(merge_conn)

        # 2. All data can be trusted. 修改数据结构
        # 2.1 增加改变目标的来源
        to_port.source = from_port_list[0] # 兼容connection 具体信息存在MergeConnection内
        for from_port in from_port_list:
            # 2.2 增加改变源的目的地
            if to_port not in from_port.destinations:
                from_port.destinations.append(to_port)
        # 2.2 增加改变目标的连接
        to_port.connection = merge_conn
            
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
        # if source_port.is_output() or source_port.is_inout():
            # 将目标端口添加到源端口的destinations列表中
        if dest_port not in source_port.destinations:
            source_port.destinations.append(dest_port)
        
        # 目标端口是输入端口或双向端口
        # if dest_port.is_input() or dest_port.is_inout():
        dest_port.source = source_port
        dest_port.connection = connection
    
    def remove_master_port_connections(self, master_port: VerilogPort) -> str:
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
        # for dest_port in master_port.destinations:
        while master_port.destinations:
            dest_port = master_port.destinations[0]
            # 放弃检查目的的源是不是自己了 因为增加了mergeConnection
            # if master_port is dest_port.source:
            #     self.remove_slave_port_connection(dest_port)
            #     ans = True
            # else:
            #     message_str = f"主端口 {master_port.name} load {dest_port.name}, BUT NOT FROM IT !!!"
            #     ans = False
            #     break
            self.remove_slave_port_connection(dest_port)
            ans = True

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
        
        # 后面connection里面还要判断的
        # # 移除从端口的源引用
        # slave_port.source = None
        # slave_port.connection = None
        
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
        ## 直接从port的 connection获取
        # # 查找匹配的连接
        # connection_to_remove = None
        # for conn in self.connections:
        #     if (conn.source_module_name == source_module_name and 
        #         conn.source_port.name == source_port_name and 
        #         conn.dest_module_name == dest_module_name and 
        #         conn.dest_port.name == dest_port_name):
        #         connection_to_remove = conn
        #         break
        
        # if not connection_to_remove:
        #     return False
        
        # # 更新端口的源和目的地信息
        # source_port = connection_to_remove.source_port
        # dest_port = connection_to_remove.dest_port
        
        dest_module = self.get_module(dest_module_name)
        dest_port = dest_module.get_port(dest_port_name)
        source_port = dest_port.source
        connection_to_remove = dest_port.connection

        # 移除源端口的目的地引用
        if dest_port in source_port.destinations:
            source_port.destinations.remove(dest_port)
        
        # 移除目标端口的源引用
        dest_port.source = None

        # 移除目标端口的connection引用
        dest_port.connection = None        

        # 清理mergeConnection
        if isinstance(connection_to_remove, VerilogMergeConnection):
            for source_port in connection_to_remove.source_port_list:
                # 移除源端口的目的地引用
                if dest_port in source_port.destinations:
                    source_port.destinations.remove(dest_port)    

        # 从连接列表中删除连接
        self.connections.remove(connection_to_remove)
        return True
    
    def get_connections_obj_by_module_name(self, module_name) -> list:
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
        # return [conn for conn in self.connections \
        #         if (conn.source_module_name == module_name or conn.dest_module_name == module_name)]
        ans_conn_list = []
        for conn in self.connections:
            if isinstance(conn, VerilogMergeConnection):
                if conn.dest_port.father_module.name == module_name:
                    ans_conn_list.append(conn)
                else:
                    for source_port in conn.source_port_list:
                        if source_port.father_module.name == module_name:
                            ans_conn_list.append(conn)
                            break
            elif isinstance(conn, VerilogConnection):
                if (conn.source_module_name == module_name or conn.dest_module_name == module_name):
                    ans_conn_list.append(conn)
        
        return ans_conn_list
    
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
                'need_gen': module.need_gen,
                'parameters': module.parameters
            }
            
            # 序列化模块的所有端口
            for port in module.ports:
                port_info = {
                    'name': port.name,
                    'direction': port.direction,
                    'width': port.width,
                    'connection': None,
                    'destinations': []
                }
                # 序列化connection属性
                if port.connection:
                    port_info['connection'] = {
                        'source_module_name': port.connection.source_module_name,
                        'source_port_name': port.connection.source_port.name,
                        'dest_module_name': port.connection.dest_module_name,
                        'dest_port_name': port.connection.dest_port.name
                    }
                # 序列化destinations属性
                for dest_port in port.destinations:
                    port_info['destinations'].append({
                        'module_name': dest_port.father_module.name,
                        'port_name': dest_port.name
                    })
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
            
            # 如果是合并连接，添加额外属性
            if isinstance(conn, VerilogMergeConnection):
                conn_info['type'] = 'merge'
                conn_info['merge_type'] = conn.type
                conn_info['source_port_list'] = [{
                    'module_name': port.father_module.name,
                    'port_name': port.name
                } for port in conn.source_port_list]
                conn_info['source_range_list'] = conn.source_range_list
                conn_info['gui_data_list'] = conn.gui_data_list
            else:
                conn_info['type'] = 'normal'
                
            connections_dict.append(conn_info)
        
        # 序列化tie_0_port和tie_1_port
        tie_ports_dict = {
            'tie_0_port': {
                'name': self.tie_0_port.name,
                'direction': self.tie_0_port.direction,
                'width': self.tie_0_port.width
            },
            'tie_1_port': {
                'name': self.tie_1_port.name,
                'direction': self.tie_1_port.direction,
                'width': self.tie_1_port.width
            }
        }
        
        # 序列化system_module
        system_md_dict = {
            'name': self.system_module.name,
            'file_path': self.system_module.file_path,
            'module_def_name': self.system_module.module_def_name
        }
        
        # 返回完整的字典表示
        return {
            'modules': modules_dict,
            'connections': connections_dict,
            'tie_ports': tie_ports_dict,
            'system_module': system_md_dict
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
        
        # 恢复tie_0_port和tie_1_port
        tie_ports_dict = data_dict.get('tie_ports', {})
        if 'tie_0_port' in tie_ports_dict:
            tie_0_info = tie_ports_dict['tie_0_port']
            collection.tie_0_port = VerilogPort(
                name=tie_0_info.get('name', 'tie_0'),
                direction=tie_0_info.get('direction', 'output'),
                width=tie_0_info.get('width', {'high': 32767, 'low': 0})
            )
        if 'tie_1_port' in tie_ports_dict:
            tie_1_info = tie_ports_dict['tie_1_port']
            collection.tie_1_port = VerilogPort(
                name=tie_1_info.get('name', 'tie_1'),
                direction=tie_1_info.get('direction', 'output'),
                width=tie_1_info.get('width', {'high': 32767, 'low': 0})
            )
        
        # 恢复system_module
        system_md_dict = data_dict.get('system_module', {})
        collection.system_module = VerilogModule(
            name=system_md_dict.get('name', '/empty/'),
            file_path=system_md_dict.get('file_path', 'system_module'),
            module_def_name=system_md_dict.get('module_def_name', 'system_module')  
        )
        # 重新添加端口到system_module
        collection.system_module.add_port(collection.tie_0_port)
        collection.system_module.add_port(collection.tie_1_port)    
        
        # 将system_module添加到module_map中，确保tie01连接能够正确恢复
        module_map[collection.system_module.name] = collection.system_module
        
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
            
            # 恢复parameters属性
            module.parameters = module_info.get('parameters', {})
        
        # 恢复端口的destinations属性
        # 先创建端口的映射关系
        port_map = {}
        for module in collection.modules:
            for port in module.ports:
                port_map[(module.name, port.name)] = port
        
        # 恢复端口的destinations属性
        for module_info in data_dict.get('modules', []):
            module_name = module_info['name']
            module = module_map.get(module_name)
            if module:
                for port_info in module_info.get('ports', []):
                    port_name = port_info['name']
                    port = module.get_port(port_name)
                    if port:
                        # 恢复destinations
                        for dest_info in port_info.get('destinations', []):
                            dest_module_name = dest_info['module_name']
                            dest_port_name = dest_info['port_name']
                            dest_port = port_map.get((dest_module_name, dest_port_name))
                            if dest_port and dest_port not in port.destinations:
                                port.destinations.append(dest_port)
        
        # 然后重建所有连接
        for conn_info in data_dict.get('connections', []):
            try:
                # 特殊处理tie01连接
                source_module_name = conn_info['source_module_name']
                source_port_name = conn_info['source_port_name']
                dest_module_name = conn_info['dest_module_name']
                dest_port_name = conn_info['dest_port_name']
                source_bit_range = conn_info.get('source_bit_range')
                dest_bit_range = conn_info.get('dest_bit_range')
                connection_type = conn_info.get('type', 'normal')
                
                # 如果是tie01端口的连接，直接创建连接对象
                if source_module_name == collection.system_module.name and source_port_name in ['tie_0', 'tie_1']:
                    # 获取源端口
                    source_port = collection.tie_0_port if source_port_name == 'tie_0' else collection.tie_1_port
                    
                    # 获取目标模块和端口
                    dest_module = module_map.get(dest_module_name)
                    if dest_module:
                        dest_port = dest_module.get_port(dest_port_name)
                        if dest_port:
                            # 直接创建连接对象
                            connection = VerilogConnection(
                                source_module=collection.system_module,
                                source_port=source_port,
                                dest_module=dest_module,
                                dest_port=dest_port,
                                source_bit_range=source_bit_range,
                                dest_bit_range=dest_bit_range
                            )
                            collection.connections.append(connection)
                            
                            # 更新端口的源和目的地信息
                            if dest_port not in source_port.destinations:
                                source_port.destinations.append(dest_port)
                            dest_port.source = source_port
                            continue
                
                # 处理合并连接
                if connection_type == 'merge':
                    # 获取所有源端口信息
                    source_port_list = []
                    for port_info in conn_info.get('source_port_list', []):
                        port_module = module_map.get(port_info['module_name'])
                        if port_module:
                            port = port_module.get_port(port_info['port_name'])
                            if port:
                                source_port_list.append(port)
                    
                    if source_port_list:
                        # 获取第一个端口作为主源端口
                        main_source_port = source_port_list[0]
                        main_source_module = main_source_port.father_module
                        
                        # 获取目标模块和端口
                        dest_module = module_map.get(dest_module_name)
                        if dest_module:
                            dest_port = dest_module.get_port(dest_port_name)
                            if dest_port:
                                # 创建合并连接对象
                                merge_connection = VerilogMergeConnection(
                                    source_module=main_source_module,
                                    source_port=main_source_port,
                                    dest_module=dest_module,
                                    dest_port=dest_port,
                                    source_bit_range=source_bit_range,
                                    dest_bit_range=dest_bit_range,
                                    merge_type=conn_info.get('merge_type', 'joint'),
                                    source_port_list=source_port_list,
                                    source_range_list=conn_info.get('source_range_list', [])
                                )
                                
                                # 设置gui_data_list
                                merge_connection.gui_data_list = conn_info.get('gui_data_list', [])
                                
                                # 添加到连接列表
                                collection.connections.append(merge_connection)
                                
                                # 更新端口的源和目的地信息
                                if dest_port not in main_source_port.destinations:
                                    main_source_port.destinations.append(dest_port)
                                dest_port.source = main_source_port
                                continue
                
                # 使用现有的add_connection方法来确保所有验证和引用都正确设置
                collection.add_connection(
                    source_module_name=source_module_name,
                    source_port_name=source_port_name,
                    dest_module_name=dest_module_name,
                    dest_port_name=dest_port_name,
                    source_bit_range=source_bit_range,
                    dest_bit_range=dest_bit_range
                )
            except Exception as e:
                # 如果连接创建失败，打印错误信息但继续处理其他连接
                print(f"警告: 无法创建连接 {conn_info['source_module_name']}.{conn_info['source_port_name']} -> {conn_info['dest_module_name']}.{conn_info['dest_port_name']}: {e}")
        
        # 为端口设置connection属性
        # 遍历所有连接，将连接对象赋值给对应的端口
        for conn in collection.connections:
            # 为源端口设置connection属性
            if hasattr(conn.source_port, 'connection'):
                conn.source_port.connection = conn
            # 为目标端口设置connection属性
            if hasattr(conn.dest_port, 'connection'):
                conn.dest_port.connection = conn
                
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
    
    def save_to_file(self, file_path, metadata=None):
        """将模块集合保存到文件
        
        参数:
            file_path (str): 保存文件的路径
            metadata (dict): 可选的元数据信息
            
        返回:
            bool: 保存是否成功
        """
        try:
            import json
            import os
            import datetime
            
            # 获取模块集合的字典表示
            collection_dict = self.to_dict()
            
            # 添加元数据到集合字典中
            if metadata is None:
                metadata = {}
            
            # 确保元数据包含必要信息
            metadata.setdefault('version', 'unknown')
            metadata.setdefault('save_time', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            metadata.setdefault('user', os.getlogin() if hasattr(os, 'getlogin') else 'unknown')
            
            # 将元数据添加到集合字典中
            collection_dict['metadata'] = metadata
            
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


