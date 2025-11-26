import os
import sys
import copy
import datetime
import json
from modules.verilog_parser import VerilogParser

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import yaml
from tkinter import filedialog, messagebox
from modules.verilog_models import VerilogModuleCollection

class FileHandler:
    """文件处理类，负责处理txt配置文件和json数据库文件的读写操作"""
    
    def __init__(self):
        """初始化文件处理器"""
        pass
        
    def open_config_file_dialog(self):
        """打开配置文件对话框，让用户选择txt文件
        
        返回:
            str or None: 选择的文件路径，如果用户取消则返回None
        """
        file_path = filedialog.askopenfilename(
            title="打开配置文件",
            filetypes=[("文本文件", "*.yaml"), ("所有文件", "*.*")]
        )
        return file_path
        
    def load_config_file(self, file_path, parser:VerilogParser, parse_parameters=False):
        """加载配置文件并解析
        
        参数:
            file_path (str): 配置文件的路径
            parser (VerilogParser): 配置文件解析器实例  
            
        返回:
            list: 解析后的模块列表
            
        异常:
            Exception: 加载或解析失败时抛出异常
        """
        try:
            # 解析配置文件
            modules = parser.parse_config_file(file_path, parse_parameters)
            return modules
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")
            
    def open_database_dialog(self):
        """打开数据库对话框，让用户选择json文件
        
        返回:
            str or None: 选择的文件路径，如果用户取消则返回None
        """
        file_path = filedialog.askopenfilename(
            title="打开数据库",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        return file_path
        
    def load_database(self, file_path):
        """加载数据库文件并恢复模块集合
        
        参数:
            file_path (str): 数据库文件的路径
            
        返回:
            VerilogModuleCollection: 从文件加载的模块集合
            
        异常:
            Exception: 加载失败时抛出异常
        """
        try:
            # 从文件加载模块集合
            loaded_collection = VerilogModuleCollection.load_from_file(file_path)
            
            if loaded_collection:
                return loaded_collection
            else:
                raise Exception("数据库文件加载失败，文件格式可能不正确")
        except Exception as e:
            raise Exception(f"加载数据库失败: {str(e)}")
            
    def save_database(self, collection_DB, file_path=None, collection_DB_stack=None, version=None):
        """深拷贝collection_DB并保存为时间戳命名的json文件到sessions目录
        
        参数:
            collection_DB: 要保存的模块集合数据库
            file_path (str or None): 数据库文件路径，为None时使用默认路径
            collection_DB_stack (deque or None): 连接历史栈，用于保存历史记录
            version (str): 可选的软件版本信息
            
        返回:
            str: 保存结果信息
            
        异常:
            Exception: 保存失败时抛出异常
        """
        if not collection_DB:
            raise Exception("没有可保存的数据库")
            
        try:
            # 深拷贝collection_DB
            db_copy = copy.deepcopy(collection_DB)
            
            # # 获取当前文件的父目录
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # # 向上一级目录，然后进入sessions目录
            # sessions_dir = os.path.join(current_dir, "..", "sessions")
            # # 规范化路径
            # sessions_dir = os.path.normpath(sessions_dir)

            # 在current work dir创建 sessions.bak 目录（如果不存在）
            sessions_dir = os.path.join(os.getcwd(), "sessions.bak")
                
            # 创建sessions目录（如果不存在）
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
                
            # 生成包含时间戳的文件名（具体到秒）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_path is None:
                file_path = os.path.join(sessions_dir, f"collection_{timestamp}.json")
            
            # 准备元数据
            metadata = {'version': version} if version else {}
            
            # 调用副本的save_to_file方法保存，并传递元数据
            save_success = db_copy.save_to_file(file_path, metadata)
            
            if save_success:
                success_message = f"数据库已成功保存到:\n{file_path}"
                # 如果提供了连接栈，则添加到栈中
                if collection_DB_stack is not None:
                    collection_DB_stack.append(db_copy)
                return success_message
            else:
                raise Exception("保存数据库失败")
        except Exception as e:
            raise Exception(f"保存数据库时发生错误: {str(e)}")
            
    def load_from_file_with_dialog(self, file_type="json"):
        """打开文件对话框并加载文件
        
        参数:
            file_type (str): 文件类型，可选值: "json", "txt"
            
        返回:
            object: 加载的对象，根据文件类型不同返回不同类型
            
        异常:
            Exception: 加载失败时抛出异常
        """
        if file_type == "json":
            file_path = self.open_database_dialog()
            if file_path:
                return self.load_database(file_path)
        elif file_type == "txt":
            file_path = self.open_config_file_dialog()
            if file_path:
                # 对于txt文件，这里只返回路径，因为解析需要parser
                return file_path
        return None