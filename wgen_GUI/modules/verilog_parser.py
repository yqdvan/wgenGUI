
import re
import sys
import os

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import yaml
from .verilog_models import VerilogModule, VerilogPort
from tkinter import messagebox

class VerilogParser:
    """Verilog文件解析器，用于提取模块的输入输出端口信息"""
    
    def __init__(self):
        """初始化解析器"""
        # 测试阶段，用于存储固定的端口信息
        self.test_input_ports = ['aa_in', 'bb_in', 'cc_in', 'dd_in', 'rr_in', 'ee_in']
        self.test_output_ports = ['cc_out', 'dd_out']
    
    def parse_config_file(self, config_file_path):
        """
        解析配置文件，获取模块名与文件路径的映射关系
        
        参数:
            config_file_path: 配置文件路径
        
        返回:
            list: 包含VerilogModule对象的列表
        """

        modules_ans: list[VerilogModule] = []
        try:
            import yaml
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
                # 假设配置文件格式为：
                # modules:
                #   - module_name: simple_module
                #     ins_name: u_simple
                #     path: ./examples/simple_module.v
                
                # 解析原始的modules部分
                if 'modules' in config_data:
                    for module_info in config_data['modules']:
                        # 对于每个模块，解析其端口信息
                        portParser =VerilogPortParser(module_info['path'])
                        ins_name = module_info.get('ins_name')
                        module_def_name = module_info.get('module_name')

                        # 直接创建VerilogModule对象
                        module_obj = VerilogModule(name=ins_name, file_path=portParser.file_path, module_def_name=module_def_name)
                        
                        # 添加输入端口
                        module_obj.add_ports(portParser.get_input_ports())
                        # 添加输出端口
                        module_obj.add_ports(portParser.get_output_ports())
                        
                        # 添加到模块列表
                        modules_ans.append(module_obj)
                
                # generate_modules:
                #   - module_name: soc_chip
                #     path: ./examples/soc_chip.v
                #   - module_name: sublock
                #     path: ./examples/sublock.v                    
                # 解析generate_modules部分
                if 'generate_modules' in config_data:

                    # 标记需要生成的模块
                    for gen_module_info in config_data['generate_modules']:
                        module_name = gen_module_info['module_name']
                        module_path = gen_module_info['path']
                        
                        #创建新的模块对象
                        module_obj = VerilogModule(
                            name=module_name,
                            file_path=module_path,
                            module_def_name=module_name
                        )

                        module_obj.need_gen = True 
                        modules_ans.append(module_obj)

                # hierarchy_def:
                #   - hierarchy: soc_chip
                #     includes:
                #       - u_simple
                #       - u_simple
                #       - u_param_module
                #       - u_complex
                #       - sublock                
                # 解析hierarchy_def部分
                if 'hierarchy_def' in config_data:

                    for hierarchy_info in config_data['hierarchy_def']:
                        parent_module_name = hierarchy_info['hierarchy']
                        included_modules = hierarchy_info['includes']
                        
                        # edit module include relation
                        parent_module = self.get_module_by_name(modules_ans, parent_module_name)
                        if parent_module:
                            for included_module_name in included_modules:
                                included_module = self.get_module_by_name(modules_ans, included_module_name)
                                if included_module:
                                    parent_module.includes.append(included_module)
                                    included_module.top_module = parent_module
                                else:
                                    messagebox.showwarning("警告", f"未找到包含模块(RTL verilog) {included_module_name}")
                                    return None
                        else:
                            messagebox.showwarning("警告", f"未找到父模块(generate verilog) {parent_module_name}")
                            return None

        except Exception as e:
            # 如果解析失败，返回空列表
            messagebox.showerror("错误", f"解析yaml配置文件失败: {e}")
        
        return modules_ans
        

    def get_module_by_name(self,module_list: list[VerilogModule], module_name: str):
        """
        根据模块名获取模块对象
        
        参数:
            module_name (str): 模块名
            
        返回:
            VerilogModule: 对应的模块对象
        """
        for module in module_list:
            if module.name == module_name:
                return module
        return None


class VerilogPortParser:
    """Verilog端口解析器，用于解析Verilog文件中的module输入输出端口信息"""
    
    def __init__(self, file_path=None):
        """
        初始化Verilog端口解析器
        
        参数:
            file_path (str, optional): Verilog文件路径
        """
        self.file_path = file_path
        self.module_name = None
        self.ports: list[VerilogPort] = []  # 存储解析出的端口信息，使用VerilogPort对象
        self.parameters = {}  # 存储模块参数
        
        # 如果提供了文件路径，则立即解析
        if file_path:
            self.parse_file(file_path)
    
    
    def parse_file(self, file_path=None):
        """
        解析Verilog文件，提取端口信息
        
        参数:
            file_path (str, optional): Verilog文件路径
            
        返回:
            dict: 包含模块名和端口信息的字典
        """
        if file_path:
            self.file_path = file_path
        
        if not self.file_path:
            raise ValueError("未提供Verilog文件路径")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"无法读取文件: {e}")
        
        # 重置解析结果
        self.ports = []
        self.parameters = {}  # 重置参数
        self.module_name = None
        
        # 在进行content分析之前，先把注释内容和空白行一律删除
        # 移除Verilog单行注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # 移除Verilog多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # 删除空白行
        content = re.sub(r'\n\s*\n', '\n', content, flags=re.MULTILINE)
        
        # 提取模块名和参数
        self._extract_module_name_and_parameters(content)
        
        # 确定Verilog代码风格并提取端口信息
        self._extract_ports_by_style(content)

    
    def _extract_module_name_and_parameters(self, content):
        """提取模块名和参数信息"""
        # 匹配模块定义行（支持带有参数的模块定义）
        module_pattern = r'module\s+(\w+)\s*(?:#\s*\(.*?\))?\s*\('
        match = re.search(module_pattern, content, re.DOTALL)
        if match:
            self.module_name = match.group(1)
        else:
            # 如果没找到标准的模块定义，尝试从文件名获取
            import os
            self.module_name = os.path.splitext(os.path.basename(self.file_path))[0]
    
    def _extract_ports_by_style(self, content):
        """
        确定Verilog代码风格并提取端口信息
        - ANSI风格：端口在module声明中定义
        - 非ANSI风格：端口在module体中定义
        - 混合风格：同时存在两种风格的端口定义
        """
        # 检查是否有ANSI风格的端口定义（在module声明中）
        module_declaration_pattern = r'module\s+\w+\s*(?:#\s*\(.*?\))?\s*\((.*?)\);'
        module_declaration_match = re.search(module_declaration_pattern, content, re.DOTALL)
        
        # 获取模块体内容
        module_body = self._extract_module_body(content)
        
        # 检查是否有非ANSI风格的端口定义（在module体中）
        has_body_ports = bool(re.search(r'\b(input|output|inout)\b', module_body))
        
        # 确定风格并调用相应的解析函数
        if module_declaration_match and has_body_ports:
            # 混合风格
            self._extract_ports_hybrid_style(content, module_body)
        elif module_declaration_match:
            # ANSI风格
            self._extract_ports_ansi_style(content)
        elif has_body_ports:
            # 非ANSI风格
            self._extract_ports_non_ansi_style(module_body)
    
    def _extract_module_body(self, content):
        """提取模块体内容"""
        # 匹配模块体
        module_pattern = r'module\s+\w+\s*(?:#\s*\(.*?\))?\s*\(.*?\);(.*?)endmodule'
        match = re.search(module_pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        return ''
    
    def _extract_ports_ansi_style(self, content):
        """从ANSI风格的Verilog代码中提取端口信息"""
        # 匹配模块声明中的端口列表
        module_declaration_pattern = r'module\s+\w+\s*(?:#\s*\(.*?\))?\s*\((.*?)\);'
        match = re.search(module_declaration_pattern, content, re.DOTALL)
        
        if match:
            port_section = match.group(1)
            
            # 分割端口声明
            port_groups = re.split(r'\b(input|output|inout)\b', port_section)
            
            # 处理每个端口组
            for i in range(1, len(port_groups), 2):
                direction = port_groups[i].strip()
                ports_text = port_groups[i+1].strip()
                
                # 分割单个端口声明
                port_lines = re.split(r'[;,]', ports_text)
                for port_line in port_lines:
                    port_line = port_line.strip()
                    if not port_line:
                        continue
                    
                    # 解析端口行中的多个端口
                    self._parse_port_line_ansi(direction, port_line)
    
    def _extract_ports_non_ansi_style(self, module_body):
        """从非ANSI风格的Verilog代码中提取端口信息"""
        # 匹配模块体中的端口声明
        port_declaration_pattern = r'\b(input|output|inout)\b\s+(.*?);'
        matches = re.finditer(port_declaration_pattern, module_body, re.DOTALL)
        
        for match in matches:
            direction = match.group(1).strip()
            ports_text = match.group(2).strip()
            
            # 解析端口声明行
            self._parse_port_declaration_line_non_ansi(direction, ports_text)
    
    def _extract_ports_hybrid_style(self, content, module_body):
        """从混合风格的Verilog代码中提取端口信息"""
        # 先解析ANSI风格的端口
        self._extract_ports_ansi_style(content)
        
        # 然后解析非ANSI风格的端口
        self._extract_ports_non_ansi_style(module_body)
    
    def _parse_port_declaration_line_non_ansi(self, direction, ports_text):
        """解析非ANSI风格的端口声明行"""
        # 检查是否包含向量声明
        vector_match = re.search(r'\[(\d+):(\d+)\]', ports_text)
        width = {'high': 0, 'low': 0}
        
        if vector_match:
            width['high'] = int(vector_match.group(1))
            width['low'] = int(vector_match.group(2))
            # 移除向量部分
            ports_text = re.sub(r'\[(\d+):(\d+)\]', '', ports_text)
        
        # 检查是否有reg/wire等类型声明
        type_match = re.search(r'\b(reg|wire|logic|signed|unsigned)\b', ports_text)
        port_type = type_match.group(1) if type_match else ''
        
        # 移除类型声明和关键字
        ports_text = re.sub(r'\b(reg|wire|logic|signed|unsigned)\b', '', ports_text)
        
        # 提取端口名（确保是有效的标识符）
        port_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', ports_text)
        
        # 过滤掉关键字
        keywords = {'input', 'output', 'inout', 'reg', 'wire', 'logic', 'signed', 'unsigned'}
        port_names = [name for name in port_names if name not in keywords]
        
        # 添加端口信息，使用VerilogPort对象
        for port_name in port_names:
            # 检查是否已经存在同名端口
            if not any(port.name == port_name for port in self.ports):
                # 创建VerilogPort对象并添加到端口列表
                port = VerilogPort(name=port_name, direction=direction, width=width)
                self.ports.append(port)
    
    def _parse_port_line_ansi(self, direction, port_line):
        """解析ANSI风格的端口行"""
        # 检查是否有向量声明
        vector_match = re.search(r'\[(\d+):(\d+)\]', port_line)
        width = {'high': 0, 'low': 0}
        
        if vector_match:
            width['high'] = int(vector_match.group(1))
            width['low'] = int(vector_match.group(2))
            # 移除向量部分
            port_line = re.sub(r'\[(\d+):(\d+)\]', '', port_line)
        
        # 移除signed/unsigned等关键字
        port_line = re.sub(r'\b(signed|unsigned)\b', '', port_line)
        
        # 提取端口名（确保是有效的标识符）
        port_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', port_line)
        
        # 过滤掉关键字
        keywords = {'input', 'output', 'inout', 'reg', 'wire', 'logic', 'signed', 'unsigned'}
        port_names = [name for name in port_names if name not in keywords]
        
        # 添加端口信息，使用VerilogPort对象
        for port_name in port_names:
            # 检查是否已经存在同名端口
            if not any(port.name == port_name for port in self.ports):
                # 创建VerilogPort对象并添加到端口列表
                port = VerilogPort(name=port_name, direction=direction, width=width)
                self.ports.append(port)
    
    def get_all_ports(self):
        """获取所有端口"""
        return self.ports.copy()
    
    def get_input_ports(self):
        """获取所有输入端口"""
        return [port for port in self.ports if port.is_input()]
        
    def get_input_port_names(self):
        """获取所有输入端口名称"""
        return [port.name for port in self.get_input_ports()]
    
    def get_output_port_names(self):
        """获取所有输出端口名称"""
        return [port.name for port in self.get_output_ports()]

    def get_output_ports(self):
        """获取所有输出端口"""
        return [port for port in self.ports if port.is_output()]
    
    def get_inout_ports(self):
        """获取所有双向端口"""
        return [port for port in self.ports if port.is_inout()]
    
    def get_port_info(self, port_name):
        """
        获取指定端口的详细信息
        
        参数:
            port_name (str): 端口名称
            
        返回:
            VerilogPort or None: 端口对象，如果未找到则返回None
        """
        for port in self.ports:
            if port.name == port_name:
                return port
        return None
    
    def get_summary(self):
        """获取解析结果的摘要信息"""
        summary = f"Module: {self.module_name}\n"
        summary += f"Total ports: {len(self.ports)}\n"
        summary += f"Input ports: {len(self.get_input_ports())}\n"
        summary += f"Output ports: {len(self.get_output_ports())}\n"
        summary += f"Inout ports: {len(self.get_inout_ports())}\n\n"
        
        if self.parameters:
            summary += "Parameters:\n"
            for name, value in self.parameters.items():
                summary += f"  {name} = {value}\n"
            summary += "\n"
        
        summary += "Ports:\n"
        for port in self.ports:
            width_str = ''
            if port.width['high'] != port.width['low']:
                width_str = f"[{port.width['high']}:{port.width['low']}]"
            
            summary += f"  {port.direction} {port.name}{width_str}\n"
        
        return summary

if __name__ == "__main__":
    parser = VerilogPortParser("C:\\Users\\yqduan\\Documents\\trae_projects\\wgenGUI\\examples\\simple_module.v")
    all_ports = parser.get_summary()
    print("All ports:")
    print(all_ports)
    # print(parser.get_input_ports())
    # print(parser.get_output_ports())
    # print(parser.get_inout_ports())
    print("\nPort info for data_in_1:")
    print(parser.get_port_info("data_in_1"))
