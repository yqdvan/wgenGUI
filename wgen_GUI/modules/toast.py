import tkinter as tk

class Toast:
    def __init__(self, root, message, duration=2000, position='bottom'):
        """
        创建一个类似Android Toast的提示框
        
        参数:
            root: 主窗口
            message: 要显示的消息
            duration: 显示时长(毫秒)
            position: 显示位置('top'/'bottom'/'center')
        """
        self.toast = tk.Toplevel(root)
        # 设置为无标题栏窗口
        self.toast.overrideredirect(True)
        # 设置透明度
        self.toast.attributes('-alpha', 0.8)
        # 创建标签显示消息
        label = tk.Label(self.toast, text=message, 
                         bg='#99CCFF', fg='black', 
                         padx=20, pady=10, 
                         font=('SimHei', 10))
        label.pack()
        
        # 计算窗口位置
        root.update_idletasks()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        
        toast_width = self.toast.winfo_reqwidth()
        toast_height = self.toast.winfo_reqheight()
        
        if position == 'bottom':
            x = root_x + (root_width - toast_width) // 2
            y = root_y + root_height - toast_height - 50
        elif position == 'top':
            x = root_x + (root_width - toast_width) // 2
            y = root_y + 50
        else:  # center
            x = root_x + (root_width - toast_width) // 2
            y = root_y + (root_height - toast_height) // 2
        
        # 调试打印坐标信息
        print(f"Toast位置: x={x}, y={y}, 尺寸: {toast_width}x{toast_height} 内容: {message}")
        # 设置窗口位置和大小
        self.toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        # 强制更新窗口位置（解决某些环境下位置不生效的问题）
        self.toast.update_idletasks()
        # 设置窗口层级，使其显示在最上层
        self.toast.attributes('-topmost', True)
        # 设置定时器，在指定时间后销毁窗口
        self.toast.after(duration, self.destroy)
    
    def destroy(self):
        self.toast.destroy()

# 测试代码
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Toast组件测试")
    root.geometry("400x300")
    
    def show_toast_bottom():
        Toast(root, "底部提示\n123\naaa", duration=3000, position='bottom')
    
    def show_toast_top():
        Toast(root, "顶部提示\n123\naaa", duration=2000, position='top')
    
    def show_toast_center():
        Toast(root, "居中提示\n123\naaa", duration=4000, position='center')
    
    btn_bottom = tk.Button(root, text="显示底部提示", command=show_toast_bottom)
    btn_bottom.pack(pady=10)
    
    btn_top = tk.Button(root, text="显示顶部提示", command=show_toast_top)
    btn_top.pack(pady=10)
    
    btn_center = tk.Button(root, text="显示居中提示", command=show_toast_center)
    btn_center.pack(pady=10)
    
    root.mainloop()