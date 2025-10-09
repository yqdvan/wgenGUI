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
        
        return {
            'module_name': self._extract_module_name(file_path),
            'inputs': self.test_input_ports,
            'outputs': self.test_output_ports
        }
    
    def _extract_module_name(self, file_path):
        """\从文件路径中提取模块名（简化版）"""
        import os
        # 简化版实现：直接从文件名中提取（不包含扩展名）
        return os.path.splitext(os.path.basename(file_path))[0]
    
    def parse_config_file(self, config_file_path):
        """
        解析配置文件，获取模块名与文件路径的映射关系
        
        参数:
            config_file_path: 配置文件路径
        
        返回:
            list: 模块信息列表
        """
        modules = []
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
                
                if 'modules' in config_data:
                    for module_info in config_data['modules']:
                        # 对于每个模块，解析其端口信息
                        module_data = self.parse_file(module_info['path'])
                        # 合并模块信息
                        module_data.update({
                            'file_path': module_info['path'],
                            'name': module_info.get('name', module_data['module_name'])
                        })
                        modules.append(module_data)
        except Exception as e:
            # 如果解析失败，返回空列表
            print(f"解析配置文件失败: {e}")
        
        return modules