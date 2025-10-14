
import re
from .verilog_models import VerilogModule, VerilogPort
from tkinter import messagebox

class VerilogParser:
    """Verilog文件解析器，用于提取模块的输入输出端口信息"""
    
    def __init__(self):
        """初始化解析器"""
        # 测试阶段，用于存储固定的端口信息
        self.test_input_ports = ['aa_in', 'bb_in', 'cc_in', 'dd_in', 'rr_in', 'ee_in']
        self.test_output_ports = ['cc_out', 'dd_out']
    
    def parse_file(self, file_path):
        """
        解析Verilog文件，提取输入输出端口信息
        
        参数:
            file_path: Verilog文件路径
        
        返回:
            dict: 包含输入输出端口信息的字典
        """
        # 测试阶段，返回固定的端口列表
        # 实际应用中，这里应该实现真正的Verilog解析逻辑
        
        parser = VerilogPortParser(file_path)

        return {
            'module_name': parser.module_name,
            'inputs': parser.get_input_port_names(),
            'outputs': parser.get_output_port_names()
        }
    
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
                #   - name: module1
                #     path: /path/to/module1.v
                #   - name: module2
                #     path: /path/to/module2.v
                
                # 解析原始的modules部分
                if 'modules' in config_data:
                    for module_info in config_data['modules']:
                        # 对于每个模块，解析其端口信息
                        module_data = self.parse_file(module_info['path'])
                        ins_name = module_info.get('ins_name', module_data['module_name'])
                        module_def_name = module_info.get('module_def_name', module_data['module_name'])

                        file_path = module_info['path']
                        
                        # 直接创建VerilogModule对象
                        module_obj = VerilogModule(name=ins_name, file_path=file_path, module_def_name=module_def_name)
                        
                        # 添加输入端口
                        for port_name in module_data['inputs']:
                            module_obj.add_port(VerilogPort(name=port_name, direction="input"))
                        
                        # 添加输出端口
                        for port_name in module_data['outputs']:
                            module_obj.add_port(VerilogPort(name=port_name, direction="output"))
                        
                        # 添加到模块列表
                        modules_ans.append(module_obj)
                
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
        self.ports = []  # 存储解析出的端口信息
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
        
        # 提取模块名和参数
        self._extract_module_name_and_parameters(content)
        
        # 提取端口信息
        self._extract_ports(content)
        
        return {
            'module_name': self.module_name,
            'ports': self.ports,
            'parameters': self.parameters
        }
    
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
    
    def _extract_ports(self, content):
        """提取端口信息"""
        # 首先获取模块体内容
        module_body = self._extract_module_body(content)
        if not module_body:
            return
        
        # 第一种情况：端口在模块声明中定义 (module (...))
        self._extract_ports_from_module_declaration(content)
        
        # 如果从模块声明中没有提取到端口，尝试从模块体中提取
        if not self.ports:
            self._extract_ports_from_module_body(module_body)
    
    def _extract_module_body(self, content):
        """提取模块体内容"""
        # 匹配模块体
        module_pattern = r'module\s+\w+\s*(?:#\s*\(.*?\))?\s*\(.*?\);(.*?)endmodule'
        match = re.search(module_pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        return ''
    
    def _extract_ports_from_module_declaration(self, content):
        """从模块声明中提取端口信息"""
        # 匹配模块声明中的端口列表
        module_declaration_pattern = r'module\s+\w+\s*(?:#\s*\(.*?\))?\s*\((.*?)\);'
        match = re.search(module_declaration_pattern, content, re.DOTALL)
        
        if match:
            port_section = match.group(1)
            # 去除注释和多余的空白
            port_section = self._remove_comments(port_section)
            
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
                    self._parse_port_line(direction, port_line)
    
    def _extract_ports_from_module_body(self, module_body):
        """从模块体中提取端口信息"""
        # 匹配模块体中的端口声明
        port_declaration_pattern = r'\b(input|output|inout)\b\s+(.*?);'
        matches = re.finditer(port_declaration_pattern, module_body, re.DOTALL)
        
        for match in matches:
            direction = match.group(1).strip()
            ports_text = match.group(2).strip()
            
            # 解析端口声明行
            self._parse_port_declaration_line(direction, ports_text)
    
    def _parse_port_declaration_line(self, direction, ports_text):
        """解析端口声明行"""
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
        
        # 添加端口信息
        for port_name in port_names:
            self.ports.append({
                'name': port_name,
                'direction': direction,
                'width': width.copy(),
                'type': port_type
            })
    
    def _parse_port_line(self, direction, port_line):
        """解析一行端口声明中的多个端口"""
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
        
        # 添加端口信息
        for port_name in port_names:
            self.ports.append({
                'name': port_name,
                'direction': direction,
                'width': width.copy(),
                'type': ''
            })
    
    def _parse_port_definition(self, direction, port_def, port_type):
        """解析单个端口定义"""
        # 检查是否有向量声明
        vector_match = re.search(r'\[(\d+):(\d+)\]', port_def)
        width = {'high': 0, 'low': 0}
        
        if vector_match:
            width['high'] = int(vector_match.group(1))
            width['low'] = int(vector_match.group(2))
            # 移除向量部分
            port_def = re.sub(r'\[(\d+):(\d+)\]', '', port_def)
        
        # 提取端口名（确保是有效的标识符）
        port_name_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', port_def)
        if port_name_match:
            port_name = port_name_match.group(1)
            # 过滤掉关键字
            keywords = {'input', 'output', 'inout', 'reg', 'wire', 'logic', 'signed', 'unsigned'}
            if port_name not in keywords:
                self.ports.append({
                    'name': port_name,
                    'direction': direction,
                    'width': width.copy(),
                    'type': port_type
                })
    
    def _remove_comments(self, text):
        """移除Verilog注释"""
        # 移除多行注释 /* ... */
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        # 移除单行注释 //
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        return text
    
    def get_all_ports(self):
        """获取所有端口"""
        return self.ports.copy()
    
    def get_input_ports(self):
        """获取所有输入端口"""
        return [port for port in self.ports if port['direction'] == 'input']
    def get_input_port_names(self):
        """获取所有输入端口名称"""
        return [port['name'] for port in self.get_input_ports()]
    
    def get_output_port_names(self):
        """获取所有输出端口名称"""
        return [port['name'] for port in self.get_output_ports()]

    def get_output_ports(self):
        """获取所有输出端口"""
        return [port for port in self.ports if port['direction'] == 'output']
    
    def get_inout_ports(self):
        """获取所有双向端口"""
        return [port for port in self.ports if port['direction'] == 'inout']
    
    def get_port_info(self, port_name):
        """
        获取指定端口的详细信息
        
        参数:
            port_name (str): 端口名称
            
        返回:
            dict or None: 端口信息字典，如果未找到则返回None
        """
        for port in self.ports:
            if port['name'] == port_name:
                return port.copy()
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
            if port['width']['high'] != port['width']['low']:
                width_str = f"[{port['width']['high']}:{port['width']['low']}]"
            
            attrs_str = ''
            if port['type']:
                attrs_str = ' ' + port['type']
            
            summary += f"  {port['direction']}{attrs_str} {port['name']}{width_str}\n"
        
        return summary

if __name__ == "__main__":
    parser = VerilogPortParser("C:\\Users\\yqduan\\Documents\\trae_projects\\wgenGUI\\examples\\complex_module.v")
    all_ports = parser.get_summary()
    print("All ports:")
    print(all_ports)
    # print(parser.get_input_ports())
    # print(parser.get_output_ports())
    # print(parser.get_inout_ports())
    print("\nPort info for data_in_1:")
    print(parser.get_port_info("data_in_1"))
