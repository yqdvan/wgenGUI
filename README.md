# wgen_GUI

wgen_GUI是一个基于Python的GUI程序，用于展示多个Verilog文件的端口情况，并支持多个Verilog模块的互联操作。

## 功能特点

- 展示多个Verilog模块的输入输出端口信息
- 支持将任意模块设置为Master或Slave
- 可视化显示模块的电路示意图
- 可调节的界面布局
- 支持YAML格式的配置文件

## 环境要求

- Python 3.x
- tkinter（通常是Python标准库的一部分）
- pyyaml

## 安装说明

1. 克隆或下载本项目到本地

2. 安装必要的依赖库
   ```bash
   pip install pyyaml
   ```

3. 在Linux系统上，可能需要单独安装tkinter
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   
   # CentOS/RHEL
   sudo yum install python3-tkinter
   ```

## 使用方法

### 快速启动

在项目根目录下运行启动脚本：

```bash
# Linux/Mac
python run_wgen_gui.py

# Windows
python run_wgen_gui.py
```

### 配置文件格式

程序支持YAML格式的配置文件，用于指定Verilog模块名与文件路径的映射关系。配置文件示例：

```yaml
# wgen_GUI配置文件

modules:
  - name: module_A
    path: /path/to/module_A.v
  - name: module_B
    path: /path/to/module_B.v
```

### 程序使用步骤

1. 启动程序后，会自动弹出文件选择对话框，要求您选择一个配置文件
2. 选择配置文件后，程序会解析文件并在左侧面板的模块列表中显示所有模块
3. 在模块列表中，右键点击任意模块，可以选择将其设为Master或Slave
4. 设置Master后，右侧面板的上方左侧会显示该模块的输出端口，下方左侧会显示其电路示意图
5. 设置Slave后，右侧面板的上方右侧会显示该模块的输入端口，下方右侧会显示其电路示意图

## 注意事项

- 当前版本处于测试阶段，Verilog解析器返回固定的测试端口列表（input: aa_in, bb_in; output: cc_out, dd_out）
- 程序支持在Windows和Linux平台上运行
- 所有界面区域的大小都可以通过拖动分隔线进行调节

## 开发说明

- `wgen_GUI/modules/verilog_parser.py` - Verilog文件解析器类
- `wgen_GUI/wgen_GUI.py` - 主GUI程序
- `run_wgen_gui.py` - 启动脚本

## 许可证

[MIT License](LICENSE)