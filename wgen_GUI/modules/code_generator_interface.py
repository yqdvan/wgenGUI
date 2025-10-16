from abc import ABC, abstractmethod
# 尝试相对导入，如果失败则使用绝对导入
try:
    from .verilog_models import VerilogModuleCollection
except ImportError:
    from verilog_models import VerilogModuleCollection


class CodeGeneratorInterface(ABC):
    """
    代码生成器接口类
    
    定义用于从VerilogModuleCollection数据库生成代码或配置字符串的标准接口。
    继承这个接口的类可以根据需要将database转换为Verilog代码字符串或其他自定义类型的互联config字符串。
    """
    
    @abstractmethod
    def generate_by_DB(self, database: VerilogModuleCollection) -> str:
        """
        从VerilogModuleCollection数据库生成代码字符串
        
        参数:
            database (VerilogModuleCollection): 包含模块和连接信息的数据库
            
        返回:
            str: 生成的代码字符串，可以是Verilog代码或其他格式的配置字符串
            
        异常:
            Exception: 生成过程中遇到错误时抛出
        """
        pass
    
    def validate_database(self, database: VerilogModuleCollection) -> bool:
        """
        验证数据库是否有效
        
        参数:
            database (VerilogModuleCollection): 要验证的数据库
            
        返回:
            bool: 如果数据库有效则返回True，否则返回False
        """
        if not isinstance(database, VerilogModuleCollection):
            return False
        
        # 验证数据库包含至少一个模块
        if not database.modules:
            return False
        
        return True