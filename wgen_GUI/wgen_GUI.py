import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import os
import yaml
from modules.verilog_parser import VerilogParser

class WGenGUI:
    """Verilog模块互联GUI工具"""
    
    def __init__(self, root):
        """初始化GUI界面"""
        self.root = root
        self.root.title("wgen_GUI")
        self.root.geometry("1200x800")
        
        # 创建解析器实例
        self.parser = VerilogParser()
        
        # 存储模块信息
        self.modules = []
        self.master_module = None
        self.slave_module = None
        
        # 创建主界面布局
        self._create_layout()
        
        # 启动时打开配置文件对话框
        self._open_config_file()
    
    def _create_layout(self):
        """创建GUI布局"""
        # 创建主分割器（左右布局）
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板
        left_frame = ttk.Frame(self.main_paned, width=400)
        self.main_paned.add(left_frame, weight=1)
        
        # 左侧上下分割器
        left_paned = ttk.PanedWindow(left_frame, orient=tk.VERTICAL)
        left_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧上部分（互联hierarchy）
        hierarchy_frame = ttk.LabelFrame(left_paned, text="互联Hierarchy")
        left_paned.add(hierarchy_frame, weight=1)
        
        self.hierarchy_text = tk.Text(hierarchy_frame, wrap=tk.WORD)
        self.hierarchy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        
        # 创建右键菜单
        self.module_menu = tk.Menu(self.root, tearoff=0)
        self.module_menu.add_command(label="设为Master", command=self._set_as_master)
        self.module_menu.add_command(label="设为Slave", command=self._set_as_slave)
        
        # 右侧面板
        right_frame = ttk.Frame(self.main_paned, width=800)
        self.main_paned.add(right_frame, weight=2)
        
        # 右侧网格布局
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)
        
        # 右上部分（Master输出端口）
        master_ports_frame = ttk.LabelFrame(right_frame, text="Master输出端口")
        master_ports_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.master_ports_text = tk.Text(master_ports_frame, wrap=tk.WORD)
        self.master_ports_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右下部分（Slave输入端口）
        slave_ports_frame = ttk.LabelFrame(right_frame, text="Slave输入端口")
        slave_ports_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.slave_ports_text = tk.Text(slave_ports_frame, wrap=tk.WORD)
        self.slave_ports_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左下部分（Master电路示意图）
        master_schematic_frame = ttk.LabelFrame(right_frame, text="Master电路示意图")
        master_schematic_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.master_canvas = tk.Canvas(master_schematic_frame, bg="white")
        self.master_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右下部分（Slave电路示意图）
        slave_schematic_frame = ttk.LabelFrame(right_frame, text="Slave电路示意图")
        slave_schematic_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.slave_canvas = tk.Canvas(slave_schematic_frame, bg="white")
        self.slave_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加菜单
        self._create_menu()
    
    def _create_menu(self):
        """创建菜单栏"""
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开配置文件", command=self._open_config_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        menu_bar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menu_bar)
    
    def _open_config_file(self):
        """打开配置文件对话框"""
        file_path = filedialog.askopenfilename(
            title="打开配置文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self._load_config_file(file_path)
    
    def _load_config_file(self, file_path):
        """加载配置文件并更新界面"""
        try:
            # 解析配置文件
            self.modules = self.parser.parse_config_file(file_path)
            
            # 如果解析结果为空，尝试直接读取txt文件的简单格式
            if not self.modules:
                self.modules = self._parse_simple_config(file_path)
            
            # 更新模块列表
            self._update_modules_list()
            
            # 显示加载成功信息
            messagebox.showinfo("成功", f"已成功加载{len(self.modules)}个模块")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")
    
    def _parse_simple_config(self, file_path):
        """解析简单格式的配置文件"""
        modules = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 假设格式为: module_name: file_path
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            module_name = parts[0].strip()
                            file_path = parts[1].strip()
                            
                            # 解析模块信息
                            module_data = self.parser.parse_file(file_path)
                            module_data.update({
                                'file_path': file_path,
                                'name': module_name
                            })
                            modules.append(module_data)
        except Exception as e:
            print(f"解析简单配置文件失败: {e}")
        
        return modules
    
    def _update_modules_list(self):
        """更新模块列表显示"""
        # 清空现有列表
        for item in self.modules_tree.get_children():
            self.modules_tree.delete(item)
        
        # 添加新模块
        for module in self.modules:
            # 存储模块索引，方便后续操作
            self.modules_tree.insert('', tk.END, text=module['name'], values=(module['name'],))
    
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
    
    def _set_as_master(self):
        """将选中的模块设为Master"""
        selected_item = self.modules_tree.selection()
        if selected_item:
            module_name = self.modules_tree.item(selected_item[0])['values'][0]
            
            # 查找对应的模块
            for module in self.modules:
                if module['name'] == module_name:
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
                if module['name'] == module_name:
                    self.slave_module = module
                    break
            
            # 更新Slave显示
            self._update_slave_display()
    
    def _update_master_display(self):
        """更新Master相关显示"""
        if self.master_module:
            # 更新输出端口显示
            self.master_ports_text.delete(1.0, tk.END)
            for port in self.master_module['outputs']:
                self.master_ports_text.insert(tk.END, f"{port}\n")
            
            # 更新电路示意图
            self._draw_module_schematic(self.master_canvas, self.master_module)
    
    def _update_slave_display(self):
        """更新Slave相关显示"""
        if self.slave_module:
            # 更新输入端口显示
            self.slave_ports_text.delete(1.0, tk.END)
            for port in self.slave_module['inputs']:
                self.slave_ports_text.insert(tk.END, f"{port}\n")
            
            # 更新电路示意图
            self._draw_module_schematic(self.slave_canvas, self.slave_module)
    
    def _draw_module_schematic(self, canvas, module):
        """绘制模块电路示意图"""
        # 清空画布
        canvas.delete("all")
        
        # 获取画布尺寸
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # 如果画布尺寸为0，设置默认尺寸
        if width == 1 or height == 1:
            width = 300
            height = 200
        
        # 绘制模块矩形
        rect_width = min(width - 40, 200)
        rect_height = min(height - 40, 150)
        x1 = (width - rect_width) // 2
        y1 = (height - rect_height) // 2
        x2 = x1 + rect_width
        y2 = y1 + rect_height
        
        canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2)
        
        # 绘制模块名称
        canvas.create_text((x1 + x2) // 2, y1 + 15, text=module['name'], font=("Arial", 12, "bold"))
        
        # 绘制输入端口
        input_count = len(module['inputs'])
        for i, port in enumerate(module['inputs']):
            y_pos = y1 + 30 + (rect_height - 40) * i / (max(1, input_count - 1))
            # 绘制端口线
            canvas.create_line(x1 - 20, y_pos, x1, y_pos, width=2)
            # 绘制端口名称
            canvas.create_text(x1 - 25, y_pos, text=port, anchor="e", font=("Arial", 10))
        
        # 绘制输出端口
        output_count = len(module['outputs'])
        for i, port in enumerate(module['outputs']):
            y_pos = y1 + 30 + (rect_height - 40) * i / (max(1, output_count - 1))
            # 绘制端口线
            canvas.create_line(x2, y_pos, x2 + 20, y_pos, width=2)
            # 绘制端口名称
            canvas.create_text(x2 + 25, y_pos, text=port, anchor="w", font=("Arial", 10))

if __name__ == "__main__":
    # 检查是否安装了yaml库
    try:
        import yaml
    except ImportError:
        import sys
        print("正在安装必要的依赖库...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
            print("依赖库安装成功")
        except Exception as e:
            print(f"依赖库安装失败: {e}")
            sys.exit(1)
    
    # 创建主窗口并运行应用
    root = tk.Tk()
    app = WGenGUI(root)
    root.mainloop()