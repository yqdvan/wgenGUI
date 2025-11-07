from time import sleep
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import copy
from collections import deque
from modules.verilog_parser import VerilogParser
from modules.verilog_models import VerilogModuleCollection, VerilogPort
from modules.file_handler import FileHandler
from modules.toast import Toast
from modules.wgen_config_generator import WgenConfigGenerator
from tkinter import ttk

class WGenGUI:
    """Verilog模块互联GUI工具"""
    version = "1.1.0" 
    
    def __init__(self, root):
        """初始化GUI界面"""
        self.root = root
        self.root.title(f"wgen_GUI {self.version}")

        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题

        self.root.geometry("1200x800")

        
        # 创建解析器实例
        self.parser = VerilogParser()
        
        # 创建文件处理器实例
        self.file_handler = FileHandler()
        
        # 存储模块信息
        self.modules: list['VerilogModule'] = []
        self.master_module: 'VerilogModule' = None
        self.slave_module: 'VerilogModule' = None
        
        # 创建模块集合database
        self.collection_DB:VerilogModuleCollection = None
        # 初始化一个大小为1024的栈，用于存放collection_DB的历史副本
        self.connections_DB_stack: deque[VerilogModuleCollection] = deque(maxlen=1024)

        # 存储缩放相关的属性
        self.master_scale = 1.0  # Master电路图的缩放比例
        self.slave_scale = 1.0   # Slave电路图的缩放比例
        self.selected_canvas = None  # 当前选中的canvas
        
        # 添加空格键快捷键来触发创建连接操作
        # 使用bind_all确保无论焦点在哪个控件上，快捷键都能响应
        # 添加return "break"防止事件冒泡，确保事件被正确处理
        def on_space_press(event):
            print("space！")
            self._create_connection()
            return "break"  # 防止事件冒泡
        
        self.root.bind_all('<space>', on_space_press)
        # 确保根窗口能接收键盘事件
        self.root.focus_set()
        
        # 存储画布偏移量
        self.master_offset_x = 0  # Master画布的X偏移
        self.master_offset_y = 0  # Master画布的Y偏移
        self.slave_offset_x = 0   # Slave画布的X偏移
        self.slave_offset_y = 0   # Slave画布的Y偏移
        self.is_dragging = False  # 是否正在拖动
        self.last_x = 0           # 上一次鼠标X坐标
        self.last_y = 0           # 上一次鼠标Y坐标
        
        # 创建主界面布局
        self._create_layout()
        
        # 启动时打开选择对话框
        self._show_startup_dialog()
    
    def _show_startup_dialog(self):
        """显示启动选择对话框，使用tkinter内置的是/否按钮对话框"""
        # 使用messagebox.askyesnocancel显示是/否/取消对话框
        result = messagebox.askyesnocancel(
            title=f"wgen_GUI {self.version} 启动选择",
            message="是否继续上一次工作？\n\n“是”：选择您保存的database，“否”：打开配置文件初始化数据库"
        )
        
        # 根据用户的选择执行相应操作
        if result is True:  # 用户选择"是"
            self._open_database()
        elif result is False:  # 用户选择"否"
            self._open_config_file()
        else:  # 用户选择"取消"或关闭对话框
            print("用户选择了取消或关闭对话框")
    
    def _create_layout(self):
        """创建GUI布局
        
        此函数作为布局创建的入口，调用三个子函数分别创建：
        1. 基础布局结构（主分割器、左右面板）
        2. 左侧面板内容（互联hierarchy、模块列表）
        3. 右侧面板内容（端口列表和电路示意图）
        """
        # 创建基础布局结构
        self._create_basic_layout()
        
        # 创建左侧面板内容
        self._create_left_panel()
        
        # 创建右侧面板内容
        self._create_right_panel()
        
        # 添加菜单
        self._create_menu()
        
    def _create_basic_layout(self):
        """创建基础布局结构
        
        负责创建主分割器、左侧面板和右侧面板的基本框架。
        设置主窗口的整体布局结构和比例。
        """
        # 创建主分割器（左右布局）
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧面板
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=1)
        
        # 创建右侧面板
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=4)
        
        # 确保窗口已经初始化
        self.root.update_idletasks() 
        
    def _create_left_panel(self):
        """创建左侧面板内容
        
        负责创建左侧面板的所有组件，包括：
        1. 上下分割器
        2. 互联hierarchy文本框
        3. 模块列表Treeview及右键菜单
        """
        # 左侧上下分割器
        left_paned = ttk.PanedWindow(self.left_frame, orient=tk.VERTICAL)
        left_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧上部分（互联hierarchy）
        hierarchy_frame = ttk.LabelFrame(left_paned, text="互联Hierarchy")
        left_paned.add(hierarchy_frame, weight=1)
        
        # 使用Text控件，以多行文本加缩进的方式展示层次关系
        self.hierarchy_text = tk.Text(hierarchy_frame, wrap=tk.WORD, font=('Arial', 10))
        self.hierarchy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        # hierarchy_scrollbar = ttk.Scrollbar(hierarchy_frame, orient=tk.VERTICAL, command=self.hierarchy_text.yview)
        # hierarchy_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.hierarchy_text.configure(yscrollcommand=hierarchy_scrollbar.set)
        
        # 左侧下部分（模块列表）
        modules_frame = ttk.LabelFrame(left_paned, text="模块列表")
        left_paned.add(modules_frame, weight=1)
        
        self.modules_tree = ttk.Treeview(modules_frame)
        self.modules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        modules_scrollbar = ttk.Scrollbar(modules_frame, orient=tk.VERTICAL, command=self.modules_tree.yview)
        modules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.modules_tree.configure(yscrollcommand=modules_scrollbar.set)
        
        # 绑定右键菜单事件
        self.modules_tree.bind("<Button-3>", self._show_module_context_menu)
        
        # 创建模块右键菜单
        self.module_menu = tk.Menu(self.root, tearoff=0)
        self.module_menu.add_command(label="设为Master", command=self._set_as_master)
        self.module_menu.add_command(label="设为Slave", command=self._set_as_slave)
        self.module_menu.add_separator()
        self.module_menu.add_command(label="属性", command=self._show_module_properties)
        
    def _create_right_panel(self):
        """创建右侧面板内容
        
        负责创建右侧面板的所有组件，包括：
        1. 使用左右PanedWindow布局，左侧为Master，右侧为Slave
        2. 在Master和Slave内部各自使用上下PanedWindow
        3. 上方放置端口列表，下方放置电路示意图
        4. 所有区域大小均可调整
        """
        # 右侧主PanedWindow - 左右布局
        right_main_paned = ttk.PanedWindow(self.right_frame, orient=tk.HORIZONTAL)
        right_main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Master部分 - 左侧
        # 创建Master内部PanedWindow - 上下布局
        master_paned = ttk.PanedWindow(right_main_paned, orient=tk.VERTICAL)
        right_main_paned.add(master_paned, weight=1)
        
        # Master上方 - 输出端口列表
        master_ports_frame = ttk.LabelFrame(master_paned, text="Master输出端口")
        master_paned.add(master_ports_frame, weight=1)
        
        # 创建内部容器框架
        master_ports_inner_frame = ttk.Frame(master_ports_frame)
        master_ports_inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 使用Treeview显示端口列表
        self.master_ports_tree = ttk.Treeview(master_ports_inner_frame, columns=("port","width", "connected"), show="headings")
        self.master_ports_tree.heading("port", text="端口名称")
        self.master_ports_tree.heading("width", text="Bit(s)")
        self.master_ports_tree.heading("connected", text="Load")
        self.master_ports_tree.column("port", width=50)
        self.master_ports_tree.column("width", width=0)  # 设置默认宽度为10个字符
        self.master_ports_tree.column("connected", width=200, anchor="center")
        self.master_ports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        master_ports_scrollbar = ttk.Scrollbar(master_ports_inner_frame, orient=tk.VERTICAL, command=self.master_ports_tree.yview)
        master_ports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.master_ports_tree.configure(yscrollcommand=master_ports_scrollbar.set)
        
        # 绑定右键菜单事件
        self.master_ports_tree.bind("<Button-3>", self._show_port_context_menu)
        # 绑定双击事件，用于显示端口信息
        self.master_ports_tree.bind("<Double-1>", lambda event: self._on_port_double_click(self.master_ports_tree, event))
        
        # Master下方 - 电路示意图
        master_schematic_frame = ttk.LabelFrame(master_paned, text="Master电路示意图")
        master_paned.add(master_schematic_frame, weight=1)
        
        self.master_canvas = tk.Canvas(master_schematic_frame, bg="white")
        self.master_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 绑定鼠标事件
        self.master_canvas.bind("<Button-1>", lambda event: self._on_drag_start(event, "master"))
        self.master_canvas.bind("<B1-Motion>", lambda event: self._on_drag_motion(event, "master"))
        self.master_canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        # Windows鼠标滚轮事件
        self.master_canvas.bind("<MouseWheel>", lambda event: self._on_mousewheel(event, "master"))
        # Linux鼠标滚轮事件
        self.master_canvas.bind("<Button-4>", lambda event: self._on_mousewheel(event, "master"))
        self.master_canvas.bind("<Button-5>", lambda event: self._on_mousewheel(event, "master"))
        
        # Slave部分 - 右侧
        # 创建Slave内部PanedWindow - 上下布局
        slave_paned = ttk.PanedWindow(right_main_paned, orient=tk.VERTICAL)
        right_main_paned.add(slave_paned, weight=1)
        
        # Slave上方 - 输入端口列表
        slave_ports_frame = ttk.LabelFrame(slave_paned, text="Slave输入端口")
        slave_paned.add(slave_ports_frame, weight=1)
        
        # 创建内部容器框架
        slave_ports_inner_frame = ttk.Frame(slave_ports_frame)
        slave_ports_inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 使用Treeview显示端口列表
        self.slave_ports_tree = ttk.Treeview(slave_ports_inner_frame, columns=("port","width", "connected"), show="headings")
        self.slave_ports_tree.heading("port", text="端口名称")
        self.slave_ports_tree.heading("width", text="Bit(s)")
        self.slave_ports_tree.heading("connected", text="Driver")
        self.slave_ports_tree.column("port", width=50)
        self.slave_ports_tree.column("width", width=0)  # 设置默认宽度为10个字符
        self.slave_ports_tree.column("connected", width=200, anchor="center")
        self.slave_ports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        slave_ports_scrollbar = ttk.Scrollbar(slave_ports_inner_frame, orient=tk.VERTICAL, command=self.slave_ports_tree.yview)
        slave_ports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.slave_ports_tree.configure(yscrollcommand=slave_ports_scrollbar.set)
        
        # 绑定右键菜单事件
        self.slave_ports_tree.bind("<Button-3>", self._show_port_context_menu)
        # # # 绑定双击事件，用于显示端口信息
        self.slave_ports_tree.bind("<Double-1>", lambda event: self._on_port_double_click(self.slave_ports_tree, event))
        
        # 创建端口右键菜单
        self.port_menu = tk.Menu(self.root, tearoff=0)
        self.port_menu.add_command(label="断开连接", command=lambda: self._port_menu_action("optionA", self.current_tree))
        self.port_menu.add_command(label="optionB", command=lambda: self._port_menu_action("optionB", self.current_tree))
        self.port_menu.add_separator()
        self.port_menu.add_command(label="属性", command=lambda: self._port_menu_action("optionC", self.current_tree))
        
        # Slave下方 - 电路示意图
        slave_schematic_frame = ttk.LabelFrame(slave_paned, text="Slave电路示意图")
        slave_paned.add(slave_schematic_frame, weight=1)
        
        self.slave_canvas = tk.Canvas(slave_schematic_frame, bg="white")
        self.slave_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 绑定鼠标事件
        self.slave_canvas.bind("<Button-1>", lambda event: self._on_drag_start(event, "slave"))
        self.slave_canvas.bind("<B1-Motion>", lambda event: self._on_drag_motion(event, "slave"))
        self.slave_canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        # Windows鼠标滚轮事件
        self.slave_canvas.bind("<MouseWheel>", lambda event: self._on_mousewheel(event, "slave"))
        # Linux鼠标滚轮事件
        self.slave_canvas.bind("<Button-4>", lambda event: self._on_mousewheel(event, "slave"))
        self.slave_canvas.bind("<Button-5>", lambda event: self._on_mousewheel(event, "slave"))
    
    def _create_menu(self):
        """创建菜单栏"""
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开配置文件", command=self._open_config_file)
        file_menu.add_separator()
        file_menu.add_command(label="打开Database", command=self._open_database)
        file_menu.add_command(label="保存Database", command=self._user_save_database)
        file_menu.add_separator()
        file_menu.add_command(label="增量更新Database", command=self._try_update_database)   
        file_menu.add_separator()     
        file_menu.add_command(label="导出wgen_config", command=self._export_wgen_config)        
        file_menu.add_separator()     
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 添加文件按钮
        menu_bar.add_cascade(label="文件", menu=file_menu)

        # 添加创建连接按钮
        menu_bar.add_command(label="创建连接", command=self._create_connection)

        # 添加查询菜单
        query_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="查询", menu=query_menu)
        query_menu.add_command(label="未连接端口", command=self._show_unconnected_ports_info)
        query_menu.add_command(label="所有连接", command=self._show_all_connnections_info)
        query_menu.add_separator()
        query_menu.add_command(label="根据实例名", command=self._query_connections_by_instance_name)
        
        # 添加帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="配置文件示例", command= lambda: self._show_scolledtext(VerilogParser._yaml_example, "配置文件示例", False)) 
        help_menu.add_command(label="快捷键列表", command= lambda: messagebox.showinfo("快捷键列表", "空格：创建连接\n"))  
        help_menu.add_separator()
        help_menu.add_command(label="关于", command=self._show_about_info) 

        self.root.config(menu=menu_bar)

    def _query_connections_by_instance_name(self):
        """根据实例名查询连接信息的辅助方法"""
        if self.collection_DB is None:
            messagebox.showerror("错误", "请先打开Database!")
            return
                    
        instance_name = simpledialog.askstring(
            "查询连接信息", 
            "                根据实例名查询连接信息                \n                    请输入实例名："
        )

        if instance_name is not None:
            connections = self.collection_DB.get_connections_by_instance_name(instance_name)
            self._show_scolledtext(connections, "根据实例名查询连接信息", False)
        else:
            Toast(self.root, "用户取消了查询操作", duration=2000, position='center')

    def _show_all_connnections_info(self):
        """查询所有连接按钮的响应函数"""
        # 弹出确认对话框
        # messagebox.showinfo("所有连接", "所有连接信息：\n" + self.collection_DB.get_all_connections_info())
        self._show_scolledtext( self.collection_DB.get_all_connections_info(), "所有连接信息", False)

    def _show_unconnected_ports_info(self):
        """查询未连接端口按钮的响应函数"""
        # 弹出确认对话框
        # messagebox.showinfo("未连接端口", "未连接端口信息：\n" + self.collection_DB.get_unconnected_ports_info())
        self._show_scolledtext( self.collection_DB.get_unconnected_ports_info(), "未连接端口信息", False)

    def _export_wgen_config(self):
        """导出wgen_config按钮的响应函数"""
        # 弹出确认对话框
        generator = WgenConfigGenerator()
        
        try:
            wgen_config_txt = generator.generate_by_DB(self.collection_DB)
        except Exception as e:
            messagebox.showerror("错误", f"导出wgen_config时发生错误: {str(e)}")
            return
        # 打开文件保存交互窗口，询问用户保存文件的名字与路径
        file_path = filedialog.asksaveasfilename(
            title="保存wgen_config",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.config"), ("所有文件", "*.*")]
        )

        # 如果用户选择了文件路径，则保存wgen_config_txt
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(wgen_config_txt)
                messagebox.showinfo("成功", f"wgen_config 已成功保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存wgen_config时发生错误: {str(e)}")
        else:
            # 用户取消了保存操作
            Toast(self.root, "用户取消了保存操作", duration=2000, position='center')
            pass
        
    def _try_update_database(self):
        """增量更新Database按钮的响应函数"""
        # 弹出确认对话框
        messagebox.showwarning("Warning", "敏感操作，可能毁坏现有数据库，更新前务必保存当前数据库！")

        # 增量更新数据库
        try:
            # 打开file dialog, 选择YAML config文件
            file_path = filedialog.askopenfilename(
                title="选择YAML config文件",
                filetypes=[("YAML config文件", "*.yaml"), ("所有文件", "*.*")]
            )
            if not file_path:
                messagebox.showwarning("Warning", "未选择YAML config文件！")
                return
            # 增量更新数据库
            modules:VerilogModule = self.file_handler.load_config_file(file_path, self.parser)
            ans_str = self.collection_DB.update_module(modules)
            
            # 使用可滚动文本框显示详细信息
            self._show_scolledtext(ans_str, "数据库增量更新Log", False)
            
            # save database
            save_result = self._save_database()
            Toast(self.root, save_result, duration=2000, position='center')

            self.modules = self.collection_DB.modules
            self.master_module = self.modules[0]
            self.slave_module = self.modules[1]

            # 更新GUI显示
            self._update_modules_list()
            self._update_hierarchy_view()
            self._update_master_display()
            self._update_slave_display()
        except Exception as e:
            # 打印完整的异常堆栈跟踪信息
            traceback.print_exc()
            messagebox.showerror("错误", f"更新时发生错误,请手动回退数据库！\n {str(e)}")
        
    def _create_connection(self):
        """创建连接按钮的响应函数，显示选中的master和slave端口"""
        # 获取master端口列表中选中的端口
        selected_master_items = self.master_ports_tree.selection()
        master_port = "未选中" if not selected_master_items else self.master_ports_tree.item(selected_master_items[0])['values'][0]
        
        # 获取slave端口列表中选中的端口
        selected_slave_items = self.slave_ports_tree.selection()
        slave_port = "未选中" if not selected_slave_items else self.slave_ports_tree.item(selected_slave_items[0])['values'][0]
        
        # 弹出messagebox显示信息
        # messagebox.showinfo("连接信息", f"Master输出端口选中：{master_port}\nSlave输入端口选中：{slave_port}")
        if self.master_module is None or self.slave_module is None:
            messagebox.showerror("错误", "请在模块列表鼠标右键指定Master与Slave, 并在端口列表选择端口！！")
            return

        from_port_obj = self.master_module.get_port(master_port)
        to_port_obj = self.slave_module.get_port(slave_port)
        
        if from_port_obj and to_port_obj:
            try:
                from_bit_range = from_port_obj.get_bit_range()
                to_bit_range = to_port_obj.get_bit_range()
                # 判断两个端口的width宽度是否一致
                if from_port_obj.get_width_value() == to_port_obj.get_width_value():
                    pass  # 宽度一致，按原流程走
                elif (from_bit_range['high'] - from_bit_range['low']) < (to_bit_range['high'] - to_bit_range['low']):
                    messagebox.showerror("错误", f"端口 {from_port_obj.name} 宽度为 {from_bit_range}，端口 {to_port_obj.name} 宽度为 {to_bit_range}。to的位宽不能大于from的位宽！")
                    return
                else:
                    # 弹出窗口让用户输入端口宽度
                    new_width = simpledialog.askstring(
                        "源端口宽度大于目标端口宽度",
                        f"端口 {from_port_obj.name} 宽度为 {from_bit_range}，端口 {to_port_obj.name} 宽度为 {to_bit_range}。\n请输入源端口范围（格式如 [high:low]）："
                    )
                    if new_width:
                        try:
                            # 解析用户输入的宽度
                            high, low = map(int, new_width.strip('[]').split(':'))
                            from_bit_range = {'high': high, 'low': low}
                            if (from_bit_range['high'] - from_bit_range['low']) != (to_bit_range['high'] - to_bit_range['low']):
                                messagebox.showerror("错误", f"端口位宽仍然不匹配，请重新操作！{from_bit_range},{to_bit_range}")
                                return
     
                        except Exception:
                            messagebox.showerror("错误", "输入的端口宽度格式不正确，请使用 [high:low] 格式！")
                            return
                    else:
                        return  # 用户取消输入，退出连接操作

                self.collection_DB.connect_port(from_port_obj, to_port_obj, from_bit_range, to_bit_range)
                save_result = self._save_database()
                show_str = f"已成功连接 {self.master_module.name}.{master_port} -> {self.slave_module.name}.{slave_port} \n{save_result}"
                # messagebox.showinfo("成功", show_str)
                Toast(self.root, show_str, duration=2000, position='center')
                self._update_master_display()
                self._update_slave_display()
            except Exception as e:
                messagebox.showerror("错误", f"连接端口失败: {str(e)}")
        else:
            messagebox.showerror("错误", "请先选择有效的“输出端口”和“输入端口”！！")
    
    def _open_config_file(self):
        """打开配置文件对话框"""
        file_path = self.file_handler.open_config_file_dialog()
        if file_path:
            try:
                modules = self.file_handler.load_config_file(file_path, self.parser)
                if modules:
                    self.modules = modules
                    self._update_modules_list()
                    self._update_hierarchy_view()
                    show_str = f"配置文件已加载成功！！共包含 {len(modules)} 个模块"
                    Toast(self.root, show_str, duration=2000, position='center')
                    self._initialize_collection_DB()
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")

    def _initialize_collection_DB(self):
        """初始化模块集合数据库"""
        self.collection_DB = VerilogModuleCollection()
        try:
            # 直接使用self.modules中的VerilogModule对象
            for module in self.modules:
                self.collection_DB.add_module(module)
            self.collection_DB.get_hierarchy_summary()
        except Exception as e:
            messagebox.showerror("错误", f"初始化模块集合数据库失败: {str(e)}")
            
    def _open_database(self):
        """打开并加载数据库文件，更新模块列表"""
        for item in self.master_ports_tree.get_children():
            self.master_ports_tree.delete(item)
        for item in self.slave_ports_tree.get_children():
            self.slave_ports_tree.delete(item)
        
        file_path = self.file_handler.open_database_dialog()
        if file_path:
            try:
                # 使用FileHandler加载数据库文件
                self.collection_DB = self.file_handler.load_database(file_path)
                
                # 显示加载成功信息
                show_str = f"Database已从 {file_path} 加载成功！！"
                Toast(self.root, show_str, duration=2000, position='center')

                # 直接使用VerilogModule对象，不再转换为结构体
                self.modules = self.collection_DB.modules
                self.master_module = self.modules[0]
                self.slave_module = self.modules[1]

                # 更新GUI显示
                self._update_modules_list()
                self._update_hierarchy_view()
                self._update_master_display()
                self._update_slave_display()
            except Exception as e:
                messagebox.showerror("错误", f"加载Database失败: {str(e)}")
            
    def _user_save_database(self):
        """弹出文件窗口让用户指定保存位置和文件名，然后调用_save_database保存数据库"""
        if self.collection_DB:
            try:
                # 使用filedialog让用户选择保存位置和文件名
                file_path = filedialog.asksaveasfilename(
                    title="保存Database",
                    defaultextension=".json",
                    filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
                )
                
                # 如果用户选择了文件路径
                if file_path:
                    # 调用_save_database函数，传入用户选择的文件路径和软件版本
                    save_result = self._save_database(file_path, self.version)  
                    if save_result:
                        show_str = f"Database已成功保存到:\n{file_path}"
                        Toast(self.root, show_str, duration=2000, position='center')
                        return save_result
                else:
                    # 用户取消了保存操作
                    return "save Cancelled"
            except Exception as e:
                messagebox.showerror("错误", f"保存Database失败: {str(e)}")
                return "save Failed"
        else:
            messagebox.showwarning("警告", "没有可保存的Database")
            return "save Failed"
    
    def _save_database(self, file_path=None, version=None):
        """保存database到文件"""
        if self.collection_DB:
            try:
                # 使用FileHandler保存数据库，并传递版本信息
                # 如果没有传入版本，默认使用类的version属性
                save_result = self.file_handler.save_database(
                    self.collection_DB, 
                    file_path, 
                    self.connections_DB_stack,
                    version or self.version
                )
                if save_result:
                    # messagebox.showinfo("成功", save_result)
                    return save_result
            except Exception as e:
                messagebox.showerror("错误", f"保存Database失败: {str(e)}")
                return ""
        else:
            messagebox.showwarning("警告", "没有可保存的Database")
            return ""

    def _update_modules_list(self):
        """更新模块列表显示"""
        # 清空现有列表
        for item in self.modules_tree.get_children():
            self.modules_tree.delete(item)
        
        # 添加新模块
        # 给modules根据name排序
        self.modules.sort(key=lambda x: x.name)
        for module in self.modules:
            # 存储模块名称，使用VerilogModule对象的name属性
            self.modules_tree.insert('', tk.END, text=module.name, values=(module.name,))
    
    def _show_module_context_menu(self, event):
        """显示模块右键菜单"""
        # 获取点击的项目
        item = self.modules_tree.identify_row(event.y)
        if item:
            # 选中点击的项目
            self.modules_tree.selection_set(item)
            self.modules_tree.focus(item)
            # 显示右键菜单
            self.module_menu.post(event.x_root, event.y_root)
    
    def _show_module_properties(self):
        """显示选中模块的属性"""
        selected_item = self.modules_tree.selection()
        if selected_item:
            module_name = self.modules_tree.item(selected_item[0])['values'][0]
            
            # 查找对应的模块
            for module in self.modules:
                if module.name == module_name:
                    # 构建属性信息
                    properties = module.__str__()
                    # messagebox.showinfo("模块属性", properties)
                    # top = tk.Toplevel()
                    # top.title("模块属性")
                    # text = tk.Text(top, wrap=tk.WORD)
                    # text.insert(tk.END, properties)
                    # text.pack(fill=tk.BOTH, expand=True)
                    # text.configure(state=tk.DISABLED)
                    # button = ttk.Button(top, text="确定", command=top.destroy)
                    # button.pack(pady=5)          
                    self._show_scolledtext(properties, "模块属性")          
                    break

    def _set_as_master(self):
        """将选中的模块设为Master"""
        selected_item = self.modules_tree.selection()
        if selected_item:
            module_name = self.modules_tree.item(selected_item[0])['values'][0]
            
            # 查找对应的模块
            for module in self.modules:
                if module.name == module_name:
                    self.master_module = module
                    break
            
            # 更新Master显示
            self._update_master_display()
    
    def _set_as_slave(self):
        """将选中的模块设为Slave"""
        selected_item = self.modules_tree.selection()
        if selected_item:
            module_name = self.modules_tree.item(selected_item[0])['values'][0]
            
            # 查找对应的模块
            for module in self.modules:
                if module.name == module_name:
                    self.slave_module = module
                    break
            
            # 更新Slave显示
            self._update_slave_display()
    
    def _on_port_double_click(self, tree, event):
        """处理Master端口Treeview的双击事件"""
        is_master:bool = tree == self.master_ports_tree
        item = tree.identify_row(event.y)
        port_name = self.master_ports_tree.item(item)['values'][0] if is_master else self.slave_ports_tree.item(item)['values'][0]
        
        # 查找对应的端口
        query_ports = self.master_module.ports if is_master else self.slave_module.ports
        selected_port = None
        for port in query_ports:
            if port.name == port_name:
                selected_port = port
                break

        if isinstance(selected_port, VerilogPort):
            # 显示端口详细信息
            top = tk.Toplevel()
            top.title("端口详细信息")
            text = tk.Text(top, wrap=tk.WORD)
            text.insert(tk.END, str(selected_port))
            text.pack(fill=tk.BOTH, expand=True)
            text.configure(state=tk.DISABLED)
            button = ttk.Button(top, text="确定", command=top.destroy)
            button.pack(pady=5)
            # self._show_scolledtext(str(selected_port), "端口详细信息")
        else:
            messagebox.showwarning("警告", f"未找到端口 {port_name}")
        
    def _update_master_display(self):
        """更新Master相关显示"""
        if self.master_module:
            # 更新输出端口显示
            # 清空现有列表
            for item in self.master_ports_tree.get_children():
                self.master_ports_tree.delete(item)
            
            # 添加端口信息，默认连接状态为否
            # 使用VerilogModule对象的方法获取端口，并从VerilogPort对象获取名称
            show_ports = self.master_module.get_output_ports()
            if self.master_module.need_gen:
                show_ports.extend(self.master_module.get_input_ports())

            # 将show_ports 内的port按照direction排序
            show_ports.sort(key=lambda x: x.direction)

            for port in show_ports:
                if isinstance(port, VerilogPort):
                    width_show = "[" +str(port.width['high']) +":"+ str(port.width['low']) + "]"
                    connect_show = "None"
                    if port.destinations:
                        # 显示第一个目标端口名称，如果有多个则添加省略号
                        if len(port.destinations) > 1:
                            # connect_show = "\n".join([f"{dest.father_module.name} -> {dest.name}" for dest in port.destinations])
                            connect_show = port.destinations[0].father_module.name + "." + port.destinations[0].name + "...(" + str(len(port.destinations)) + " more lines)"
                        else:
                            connect_show = port.destinations[0].father_module.name + "." + port.destinations[0].name
                    self.master_ports_tree.insert('', tk.END, values=(port.name,width_show, connect_show), open=True)
                else:
                    messagebox.showerror("错误", f"端口 {port.name} 不是 VerilogPort 类型")
            
            # 更新电路示意图
            self._draw_module_schematic(self.master_canvas, self.master_module)
    
    def _update_slave_display(self):
        """更新Slave相关显示"""
        if self.slave_module:
            # 更新输入端口显示
            # 清空现有列表
            for item in self.slave_ports_tree.get_children():
                self.slave_ports_tree.delete(item)
            
            # 添加端口信息，默认连接状态为否
            # 使用VerilogModule对象的方法获取端口，并从VerilogPort对象获取名称
            show_ports = self.slave_module.get_input_ports()
            if self.slave_module.need_gen:
                show_ports.extend(self.slave_module.get_output_ports())

            # 将show_ports 内的port按照direction排序
            show_ports.sort(key=lambda x: x.direction)

            for port in show_ports:
                if isinstance(port, VerilogPort):
                    width_show = "[" +str(port.width['high']) +":"+ str(port.width['low']) + "]"
                    connect_show = "None"
                    if port.source:
                        connect_show = port.source.father_module.name + "." + port.source.name
                    self.slave_ports_tree.insert('', tk.END, values=(port.name,width_show, connect_show)) 
                else:
                    messagebox.showerror("错误", f"端口 {port.name} 不是 VerilogPort 类型")
            
            # 更新电路示意图
            self._draw_module_schematic(self.slave_canvas, self.slave_module)
    
    def _show_port_context_menu(self, event):
        """显示端口右键菜单"""
        # 获取点击的控件和项目
        widget = event.widget
        item = widget.identify_row(event.y)
        if item:
            # 选中点击的项目
            widget.selection_set(item)
            widget.focus(item)
            # 记录当前操作的tree控件
            self.current_tree = widget
            # 显示右键菜单
            self.port_menu.post(event.x_root, event.y_root)
    
    def _port_menu_action(self, action, tree=None):
        """端口右键菜单操作"""
        # 确定当前操作的是哪个tree以及端口信息
        tree_type = ""
        port_name = ""
        port_obj:VerilogPort  = None
        
        if tree is not None:
            # 确定tree的类型
            if tree == self.master_ports_tree:
                tree_type = "master"
            elif tree == self.slave_ports_tree:
                tree_type = "slave"
            
            # 获取选中的端口信息
            selected_items = tree.selection()
            if selected_items:
                port_name = tree.item(selected_items[0])['values'][0]
                
        else:
            # 检查哪个tree有选中的项目
            selected_master_items = self.master_ports_tree.selection()
            selected_slave_items = self.slave_ports_tree.selection()
            
            if selected_master_items:
                tree_type = "master"
                port_name = self.master_ports_tree.item(selected_master_items[0])['values'][0]
            elif selected_slave_items:
                tree_type = "slave"
                port_name = self.slave_ports_tree.item(selected_slave_items[0])['values'][0]
        
        if tree_type == "master" and action == "optionA":
            port_obj = self.master_module.get_port(port_name)
            if port_obj:
                # 检查port_obj的destinations数量
                le = len(port_obj.destinations)
                # 弹窗询问用户是否删除所有连接
                confirm = messagebox.askyesno("确认删除", f"是否删除主端口 {port_name} 内所有 {le} 个 load 连接？")
                if confirm:
                    ans_str = self.collection_DB.remove_master_port_connections(port_obj)
                    if ans_str is None or ans_str == "":
                        save_result = self._save_database()
                        if save_result is not None and save_result != "":
                            Toast(self.root, "删除连接成功\n" + save_result, duration=2000, position='center')
                            print(f"成功删除主端口 {port_name} 的连接")
                        else:
                            save_result = "save failed!!!"
                            messagebox.showerror("错误", save_result)
                    else:
                        messagebox.showerror("错误", ans_str)
            else:
                messagebox.showerror("错误", f"端口 {port_name} 不是 VerilogPort 类型")
            self._update_master_display()
            self._update_slave_display()

        elif tree_type == "master" and action == "optionC":
            messagebox.showinfo("操作提示", f"正在开发，敬请期待！")
        elif tree_type == "slave" and action == "optionA":  
            port_obj = self.slave_module.get_port(port_name)
            if port_obj:
                ans_str = self.collection_DB.remove_slave_port_connection(port_obj)
                if ans_str is None or ans_str == "":
                    save_result = self._save_database()
                    if save_result is not None and save_result != "":
                        Toast(self.root, "删除连接成功\n" + save_result, duration=2000, position='center')
                        print(f"成功删除从端口 {port_name} 的连接")
                    else:
                        save_result = "save failed!!!"
                        messagebox.showerror("错误", save_result)
                else:
                    messagebox.showerror("错误", ans_str)
            else:
                messagebox.showerror("错误", f"端口 {port_name} 不是 VerilogPort 类型")
            self._update_master_display()
            self._update_slave_display()

        else:
            show_str = f"你在{tree_type}端口列表中点击了{action}操作，端口：{port_name}"
            Toast(self.root, show_str, duration=2000, position='center')

        # # 根据操作类型显示不同的消息
        # if action == "optionA":
        #     messagebox.showinfo("操作提示", f"你在{tree_type}端口列表中点击了{action}操作，端口：{port_name}")
        # elif action == "optionB":
        #     messagebox.showinfo("操作提示", f"你在{tree_type}端口列表中点击了{action}操作，端口：{port_name}")
        # else:
        #     # 其他操作保持原有逻辑
        #     messagebox.showinfo("操作提示", f"你在{tree_type}端口列表中点击了{action}操作，端口：{port_name}")
    
    def _draw_module_schematic(self, canvas, module):
        """绘制模块电路示意图"""
        # 清空画布
        canvas.delete("all")
        
        # 获取当前ttk主题的背景色作为矩形填充色
        style = ttk.Style()
        # 尝试获取不同元素的背景色，确保能获得合适的填充色
        try:
            fill_color = style.lookup("Frame", "background")
        except:
            # 如果获取失败，使用默认的浅灰色
            fill_color = "#1abc9c"
        fill_color = "#8aa9c4"
        if module.need_gen:
            fill_color = "#99CCFF"

        # 获取画布尺寸
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # 如果画布尺寸为0，设置默认尺寸
        if width == 1 or height == 1:
            width = 300
            height = 200
        
        # 确定当前使用的缩放比例和偏移量
        if canvas == self.master_canvas:
            scale = self.master_scale
            offset_x = self.master_offset_x
            offset_y = self.master_offset_y
        else:
            scale = self.slave_scale
            offset_x = self.slave_offset_x
            offset_y = self.slave_offset_y
        
        # 计算基础尺寸，考虑缩放
        base_width = min(width - 40, 200) * scale
        base_height = 100  # 基础高度
        
        # 使用VerilogModule对象的方法获取端口
        input_ports = module.get_input_ports()
        output_ports = module.get_output_ports()
        
        # 根据端口数量调整矩形高度，确保每个端口至少有20像素的空间
        input_count = len(input_ports)
        output_count = len(output_ports)
        max_port_count = max(input_count, output_count)
        port_based_height = 40 + max_port_count * 20  # 40是边距，每个端口20像素
        
        # 综合考虑画布高度和端口需求的高度
        rect_width = base_width
        rect_height = min(height - 40, max(base_height, port_based_height)) * scale
        
        # 计算中心位置，并考虑偏移量
        center_x = (width // 2) + offset_x
        center_y = (height // 2) + offset_y
        x1 = center_x - rect_width // 2
        y1 = center_y - rect_height // 2
        x2 = x1 + rect_width
        y2 = y1 + rect_height
        
        # 绘制模块矩形，使用主题背景色填充
        canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2, fill=fill_color)
        
        # 绘制模块名称，使用VerilogModule对象的name属性
        if module.need_gen:
            text_show = "\n"+module.name + "\n (Need to generate)"
        else:
            text_show = "\n"+module.name + "\n (" + module.module_def_name + ")"
        canvas.create_text((x1 + x2) // 2, y1 + 15, text=text_show, font=("Arial", 12, "bold"))
        
        # 绘制输入端口，从VerilogPort对象获取名称
        if input_count > 0:
            port_spacing = (rect_height - 40) / (max(1, input_count - 1)) if input_count > 1 else 0
            for i, port in enumerate(input_ports):
                y_pos = y1 + 30 + port_spacing * i
                # 根据端口是否有source设置颜色：有source用绿色，无source用红色
                line_color = "green" if port.source is not None else "red"
                if module.need_gen:
                    line_color = "green" if port.source is not None or port.destinations else "red"
                # 绘制端口线
                canvas.create_line(x1 - 20, y_pos, x1, y_pos, width=2, fill=line_color)
                # 绘制端口名称，使用VerilogPort对象的name属性
                canvas.create_text(x1 - 25, y_pos, text=port.name, anchor="e", font=('Arial', 10), fill=line_color)
        
        # 绘制输出端口，从VerilogPort对象获取名称
        if output_count > 0:
            port_spacing = (rect_height - 40) / (max(1, output_count - 1)) if output_count > 1 else 0
            for i, port in enumerate(output_ports):
                y_pos = y1 + 30 + port_spacing * i
                # 根据端口的destinations是否为空设置颜色：有目标端口用绿色，无目标端口用红色
                line_color = "green" if port.destinations else "red"
                if module.need_gen:
                    line_color = "green" if port.source is not None or port.destinations else "red"
                # 绘制端口线
                canvas.create_line(x2, y_pos, x2 + 20, y_pos, width=2, fill=line_color)
                # 绘制端口名称，使用VerilogPort对象的name属性
                canvas.create_text(x2 + 25, y_pos, text=port.name, anchor="w", font=('Arial', 10), fill=line_color)
                
    def _on_drag_start(self, event, canvas_type):
        """开始拖动画布"""
        # 选中当前画布
        if canvas_type == "master":
            self.selected_canvas = self.master_canvas
        else:
            self.selected_canvas = self.slave_canvas
        
        # 开始拖动
        self.is_dragging = True
        self.last_x = event.x
        self.last_y = event.y
            
    def _on_drag_motion(self, event, canvas_type):
        """拖动画布时的移动事件"""
        # print("\n拖动画布时的移动事件")
        # print("当前事件:", event)
        if self.is_dragging:
            # 计算鼠标移动的距离
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            
            # 更新偏移量
            if canvas_type == "master":
                self.master_offset_x += dx
                self.master_offset_y += dy
                if self.master_module:
                    self._draw_module_schematic(self.master_canvas, self.master_module)
            else:
                self.slave_offset_x += dx
                self.slave_offset_y += dy
                if self.slave_module:
                    self._draw_module_schematic(self.slave_canvas, self.slave_module)
            
            # 更新上次鼠标位置
            self.last_x = event.x
            self.last_y = event.y
            
    def _on_drag_end(self, event):
        """结束拖动画布"""
        self.is_dragging = False
        
    def _select_canvas(self, canvas):
        """选中canvas"""
        self.selected_canvas = canvas
        
    def _on_mousewheel(self, event, canvas_type):
        """处理鼠标滚轮事件，实现缩放功能（跨平台兼容）"""
        # 检查当前画布是否被选中
        # print("\n处理鼠标滚轮事件，实现缩放功能")
        # print("当前事件:", event)
        if (canvas_type == "master" and self.selected_canvas == self.master_canvas) or \
           (canvas_type == "slave" and self.selected_canvas == self.slave_canvas):
            # 跨平台滚动方向判断
            # Windows使用event.delta，Linux使用event.num（Button-4=向上，Button-5=向下）
            zoom_factor = 1.1

            if hasattr(event, 'num') and event.num in [4, 5]:
                # Linux平台
                # print("Linux平台鼠标滚轮事件，event.num =", event.num)
                zoom_factor = 1.1 if event.num == 4 else 0.9
            elif hasattr(event, 'delta'):
                # Windows平台
                # print("Windows平台鼠标滚轮事件，event.delta =", event.delta)
                delta = event.delta
                zoom_factor = 1.1 if delta > 0 else 0.9

            
            # 更新缩放比例
            if canvas_type == "master":
                self.master_scale = max(0.5, min(3.0, self.master_scale * zoom_factor))
                if self.master_module:
                    self._draw_module_schematic(self.master_canvas, self.master_module)
            else:
                self.slave_scale = max(0.5, min(3.0, self.slave_scale * zoom_factor))
                if self.slave_module:
                    self._draw_module_schematic(self.slave_canvas, self.slave_module)

    def _update_hierarchy_view(self):
        """更新互联hierarchy视图
        
        检索self.modules中所有top_module为None的对象（顶级对象），
        并以改进的多行文本加缩进的方式显示它们的层次结构
        """
        # 清空文本框
        self.hierarchy_text.configure(state=tk.NORMAL)
        self.hierarchy_text.delete(1.0, tk.END)
        
        # 检索所有top_module为None的对象
        top_modules = [module for module in self.modules if getattr(module, 'top_module', None) is None]
        
        hierarchy_text = "# 模块层次结构\n"
        hierarchy_text += "# ===============\n\n"
        
        if not top_modules:
            # 如果没有top模块，显示提示信息
            hierarchy_text += "未找到顶级模块\n"
        else:
            # 为每个top模块生成层次结构文本
            for i, top_module in enumerate(top_modules):
                # 对于顶级模块，is_last总是True，因为它们之间是并列关系
                is_last_top = (i == len(top_modules) - 1)
                # 生成top模块的层次结构文本
                module_text = self._generate_module_hierarchy_text(top_module, 0, is_last_top)
                hierarchy_text += module_text + "\n\n"
        
        # 在文本框中显示层次结构
        self.hierarchy_text.insert(tk.END, hierarchy_text)
        self.hierarchy_text.configure(state=tk.DISABLED)  # 设置为只读
        
    def _generate_module_hierarchy_text(self, module, indent_level, is_last=False, prefix=[]):
        """递归生成模块及其包含的模块层次结构文本，使用树形结构指示符增强视觉效果
        
        参数:
            module: 当前模块对象
            indent_level: 缩进级别
            is_last: 是否是父模块的最后一个子模块
            prefix: 前缀列表，用于构建树形结构指示符
            
        返回:
            str: 层次结构文本
        """
        # 构建树形结构指示符
        tree_prefix = ""
        for i, p in enumerate(prefix):
            if p:
                tree_prefix += "│   "
            else:
                tree_prefix += "    "
        
        if indent_level > 0:
            if is_last:
                tree_prefix += "└── "
            else:
                tree_prefix += "├── "
        
        # 生成模块文本
        module_text = f"{tree_prefix}{module.name}"
        
        # 添加模块属性信息
        if hasattr(module, 'module_def_name') and module.module_def_name:
            module_text += f" ({module.module_def_name})"
        
        # 添加是否为生成模块的标记
        if hasattr(module, 'need_gen') and module.need_gen:
            module_text += " [需要生成]"
        
        # 检查模块是否有包含的模块
        includes = getattr(module, 'includes', [])
        if includes:
            new_prefix = prefix + [not is_last]
            # 为每个包含的模块递归生成文本
            for i, include_module in enumerate(includes):
                is_last_child = (i == len(includes) - 1)
                include_text = self._generate_module_hierarchy_text(include_module, indent_level + 1, is_last_child, new_prefix)
                module_text += f"\n{include_text}"
        
        return module_text

    def _show_scolledtext(self, text: str, title: str = "showText", modal: bool = True):
        """显示可滚动的文本框，用于展示详细信息
        
        Args:
            text: 要显示的文本内容
            title: 窗口标题
            modal: 是否为模态窗口，True表示需要等待用户操作后才返回主流程，False表示非模态窗口
        """
        result_window = tk.Toplevel(self.root)
        # 先隐藏窗口，避免闪烁
        result_window.withdraw()
        
        result_window.title("Information")
        result_window.geometry("600x400")
        result_window.resizable(True, True)
        
        # 创建标题标签
        title_label = tk.Label(result_window, text=title, font=("SimHei", 12, "bold"))
        title_label.pack(pady=10, padx=10, anchor="w")
        
        # 创建可滚动文本框
        text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=70, height=15, font=("SimHei", 10))
        text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, text)
        text_area.config(state=tk.DISABLED)  # 设置为只读
        
        # 添加关闭按钮
        close_button = tk.Button(result_window, text="关闭", command=result_window.destroy, width=15)
        close_button.pack(pady=10)
        
        # 设置窗口居中（使用直接计算的方式，避免update_idletasks导致的闪烁）
        # 计算屏幕中心位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        result_window.geometry(f"600x400+{x}+{y}")
        
        # 根据modal参数决定窗口行为
        if modal:
            # 模态窗口：设置为主窗口的临时窗口并获取焦点
            result_window.transient(self.root)
            result_window.grab_set()
        else:
            # 非模态窗口：不设置为临时窗口，允许被主窗口遮挡
            pass  # 不调用transient()方法，让窗口按正常方式显示
        
        # 所有组件创建完成后显示窗口
        result_window.deiconify()
        
        # 如果是模态窗口，则等待用户关闭
        if modal:
            self.root.wait_window(result_window)

    def _show_about_info(self):
        """显示关于信息对话框
        
        弹出一个消息框，显示本软件的著作权、基本功能、版本等信息
        """
        about_message = f"""
WGenGUI 版本 {self.version}

著作权所有 © 2025

基本功能：
- 模块互联层次结构展示
- Master/Slave模块端口连接管理
- 电路示意图可视化显示
- 支持画布缩放和拖动功能
- 端口连接状态管理
- 所有连接信息查询
- 支持模块信息批量更新

感谢使用本软件！
        """
        tk.messagebox.showinfo("关于 WGenGUI", about_message)

if __name__ == "__main__":
    # 首先导入必要的库
    import sys
    import os
    import tkinter as tk

    # 获取当前工作目录（用户执行命令的目录）
    current_working_directory = os.getcwd()
    print(f"用户执行命令的目录: {current_working_directory}")

    # 如果需要获取程序本身所在的目录，可以使用
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"程序本身所在的目录: {script_directory}")

    # 添加模块目录到Python路径
    sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

    from splash_screen import SplashScreen
    # 显示启动窗口
    splash_root = tk.Tk()
    # 设置启动窗口图标
    try:
        # 获取图标文件的绝对路径
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ppm")
        icon = tk.PhotoImage(file=icon_path)
        splash_root.iconphoto(True, icon)
    except Exception as e:
        print(f"无法加载图标: {e}")
    
    splash = SplashScreen(splash_root, WGenGUI.version)
    splash_root.update()
    
    splash.update_loading_text(f"python版本: {sys.version}")
    sleep(0.6)

    # 检查是否安装了yaml库
    try:
        # 添加lib目录到Python路径
        sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
        import yaml
        splash.update_loading_text("导入yaml库...   成功")
        sleep(0.2)
        splash.update_loading_text(f"yaml版本: {yaml.__version__}")
        sleep(0.2)        
        
        # 更新加载信息
        splash.update_loading_text(f"初始化配置... (tk版本: {tk.TkVersion})")
        sleep(0.2)

        splash.update_loading_text(f"wgen_GUI版本: {WGenGUI.version}")
        sleep(0.2)        
        
    except ImportError:
        # 更新加载信息
        splash.update_loading_text("正在安装依赖库...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
            splash.update_loading_text("依赖库安装成功")
        except Exception as e:
            print(f"依赖库安装失败: {e}")
            splash.update_loading_text("依赖库安装失败")
            sys.exit(1)
    
    # 更新加载信息为最后一步
    splash.update_loading_text("准备启动应用...")
    
    # 1秒后关闭启动窗口并启动主应用
    def close_splash():
        # 先停止进度条动画
        splash.stop()
        # 销毁启动窗口
        splash_root.destroy()
        # 创建主应用
        root = tk.Tk()

        app = WGenGUI(root)
        root.mainloop()
    
    # 1秒后执行关闭函数
    splash_root.after(500, close_splash)  # 1000毫秒 = 1秒
    
    # 启动启动窗口的主循环
    splash_root.mainloop()
    # 主应用将在splash窗口关闭后通过close_splash函数启动


