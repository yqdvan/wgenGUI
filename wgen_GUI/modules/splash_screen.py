import tkinter as tk
from tkinter import ttk

class SplashScreen:
    """
    软件启动窗口类
    显示软件banner、名称和加载进度信息
    """
    def __init__(self, root, version_str):
        """
        初始化启动窗口
        
        参数:
            root: Tkinter根窗口对象
        """
        self.root = root
        # 设置窗口样式
        root.overrideredirect(True)  # 无边框窗口
        root.attributes('-topmost', True)  # 置顶显示
        
        # 设置窗口大小和位置
        width, height = 500, 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # 设置窗口背景
        root.configure(bg='#2c3e50')
        
        # 创建banner文本
        self.banner = """
██╗    ██╗ ██████╗ ███████╗███╗   ██╗     ██████╗ ██╗   ██╗██╗
██║    ██║██╔════╝ ██╔════╝████╗  ██║    ██╔════╝ ██║   ██║██║
██║ █╗ ██║██║  ███╗█████╗  ██╔██╗ ██║    ██║  ███╗██║   ██║██║
██║███╗██║██║   ██║██╔══╝  ██║╚██╗██║    ██║   ██║██║   ██║██║
╚███╔███╔╝╚██████╔╝███████╗██║ ╚████║    ╚██████╔╝╚██████╔╝██║
╚══╝╚══╝  ╚═════╝ ╚══════╝╚═╝  ╚═══╝     ╚═════╝  ╚═════╝ ╚═╝
        """
        
        # 创建banner标签
        banner_label = tk.Label(root, text=self.banner, font=('Courier New', 10), fg='#ecf0f1', bg='#2c3e50', justify='center')
        banner_label.pack(pady=20)
        
        # 创建软件名称标签
        title_label = tk.Label(root, text="Wiring Generator GUI", font=('Arial', 16, 'bold'), fg='#3498db', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # 创建版本标签
        version_label = tk.Label(root, text=f"Version {version_str}", font=('Arial', 10), fg='#95a5a6', bg='#2c3e50')
        version_label.pack()
        
        # 创建加载信息标签
        self.loading_label = tk.Label(root, text="正在加载...", font=('Arial', 9), fg='#1abc9c', bg='#2c3e50')
        self.loading_label.pack(side='bottom', pady=15)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, length=400, mode='indeterminate')
        self.progress_bar.pack(side='bottom', pady=5)
        self.progress_bar.start()
    
    def update_loading_text(self, text):
        """
        更新加载信息文本
        
        参数:
            text: 新的加载信息文本
        """
        self.loading_label.config(text=text)
        self.root.update()
        
    def stop(self):
        """
        安全停止进度条动画，避免窗口销毁后进度条定时器仍在运行
        """
        try:
            self.progress_bar.stop()
        except Exception:
            pass  # 忽略可能的错误，如窗口已销毁