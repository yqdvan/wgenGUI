# wgen_GUI 完整文档

wgen_GUI是一个基于Python的GUI程序，用于展示多个Verilog文件的端口情况，并支持多个Verilog模块的互联操作。

## 功能特点

- 展示多个Verilog模块的输入输出端口信息
- 支持将任意模块设置为Master或Slave
- 可视化显示模块的电路示意图
- 可调节的界面布局
- 支持YAML格式的配置文件
- 支持多个Verilog模块的互联操作
- 提供撤销功能（Ctrl+Z）
- 快速创建连接的快捷键支持（空格键）

## 环境要求

- Python 3.11.x
- tkinter（通常是Python标准库的一部分）
- pyyaml

## 安装说明

1. 克隆或下载本项目到本地

2. 在Linux系统上，可能需要单独安装tkinter
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   
   # CentOS/RHEL
   sudo yum install python3-tkinter
   ```

注意：pyyaml依赖已存放在项目本地的`wgen_GUI/lib`目录下，无需额外安装。

## 使用方法

### 启动程序

在项目根目录下运行：

```bash
# Linux/Mac
python wgen_GUI/wgen_GUI.py

# Windows
python wgen_GUI\wgen_GUI.py
```

### 启动选择

程序启动后，会显示启动选择对话框：
- **是**：选择保存的数据库文件，继续上一次工作
- **否**：打开配置文件初始化数据库
- **取消**：关闭程序

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

### 模块操作

1. **设置Master/Slave**
   - 在左侧模块列表中右键点击任意模块
   - 选择"Set as Master"将模块设为主模块
   - 选择"Set as Slave"将模块设为从模块

2. **端口连接**
   - 设置Master模块后，右侧面板上方左侧显示该模块的输出端口
   - 设置Slave模块后，右侧面板上方右侧显示该模块的输入端口
   - 选择端口后，使用空格键快速创建连接

3. **多端口选择**
   - 支持同时选择多个端口进行连接
   - 在多端口选择界面中，可以添加/删除行
   - 提示文字："Line 1 is MSB(high), Last is LSB(low)"表示第一行是最高位，最后一行是最低位

## 界面说明

### 整体布局

程序界面分为以下几个主要部分：

1. **左侧面板**
   - 模块列表：显示所有加载的Verilog模块
   - 层次结构视图：显示模块的层次结构

2. **右侧面板**
   - Master区域：显示主模块的输出端口和电路示意图
   - Slave区域：显示从模块的输入端口和电路示意图

3. **多端口选择界面**
   - 表格：显示选择的端口和位范围
   - 按钮框架：包含添加/删除行按钮和提示文字

### 多端口选择界面组件

#### 按钮框架
```python
# 创建添加/删除行按钮 - 上下排列
button_frame = ttk.Frame(main_frame, width=100)
button_frame.pack(side=tk.RIGHT, padx=(10, 10), pady=10, fill=tk.NONE)
```

- **width**: 设置框架宽度为100像素
- **side**: 放置在父容器的右侧
- **padx**: 左右外边距均为10像素
- **pady**: 上下外边距均为10像素
- **fill**: 不填充父容器的额外空间

#### 提示文字
```python
# 添加提示文字
tips_str = "Tips:\n Line 1 is MSB(high),\n Last is LSB(low)."
tip_label = ttk.Label(button_frame, text=tips_str, justify=tk.LEFT, wraplength=120)
tip_label.pack(pady=(5, 10), padx=5)
```

- **text**: 显示的提示内容
- **justify**: 文本左对齐
- **wraplength**: 当文本长度超过120像素时自动换行
- **pady**: 上下内边距分别为5像素和10像素
- **padx**: 左右内边距均为5像素

#### 添加行按钮
```python
add_button = ttk.Button(button_frame, text="Add Row", command=add_row)
add_button.pack(fill=tk.X, pady=(5, 5), padx=5)
```

- **text**: 按钮显示的文字
- **command**: 点击按钮时调用的函数
- **fill**: 水平填充按钮框架
- **pady**: 上下内边距均为5像素
- **padx**: 左右内边距均为5像素

#### 删除行按钮
```python
delete_button = ttk.Button(button_frame, text="Delete Row", command=delete_row)
delete_button.pack(fill=tk.X, pady=(0, 5), padx=5)
```

- **text**: 按钮显示的文字
- **command**: 点击按钮时调用的函数
- **fill**: 水平填充按钮框架
- **pady**: 上方内边距为0像素，下方内边距为5像素
- **padx**: 左右内边距均为5像素

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| 空格键 | 创建连接 |
| Ctrl+Z | 撤销操作 |

## 项目结构

```
wgenGUI/
├── README.md           # 项目说明文档
├── example_config.yaml # 示例配置文件
└── wgen_GUI/           # 主程序目录
    ├── wgen_GUI.py     # 主GUI程序
    ├── icon.ppm        # 程序图标
    └── modules/        # 模块目录
        ├── verilog_parser.py          # Verilog文件解析器
        ├── verilog_models.py          # Verilog模型定义
        ├── file_handler.py            # 文件处理
        ├── toast.py                   # 提示信息组件
        ├── wgen_config_generator.py   # 配置生成器
        ├── splash_screen.py           # 启动画面
        └── code_generator_interface.py # 代码生成器接口
```

## 核心模块说明

### wgen_GUI.py

主GUI程序，包含以下主要功能：
- 程序初始化和界面创建
- 模块的加载和管理
- 端口的显示和操作
- 连接的创建和管理
- 快捷键处理
- 撤销功能

### verilog_parser.py

Verilog文件解析器，用于解析Verilog文件并提取模块信息和端口信息。

### verilog_models.py

定义了Verilog相关的模型类：
- VerilogModuleCollection：模块集合
- VerilogModule：Verilog模块
- VerilogPort：模块端口
- VerilogConnection：端口连接
- VerilogMergeConnection：合并连接

### file_handler.py

文件处理模块，用于读取和保存配置文件和数据库文件。

### toast.py

提示信息组件，用于显示临时的提示信息。

### wgen_config_generator.py

配置生成器，用于生成Verilog配置文件。

### splash_screen.py

启动画面模块，用于显示程序启动时的加载画面。

## 开发说明

### 数据结构设计

#### 核心数据结构

1. **VerilogPort**
   - 表示Verilog模块的端口，包含名称、方向、位宽等属性
   - 存储端口的连接信息，包括源端口和目标端口列表
   - 支持位宽范围的描述和连接关系的管理

2. **VerilogModule**
   - 表示Verilog模块，包含模块名称、文件路径、端口列表等属性
   - 管理模块间的包含关系和层级结构
   - 支持端口的增删改查操作

3. **VerilogConnection**
   - 表示端口之间的连接关系
   - 管理源端口和目标端口的位宽匹配
   - 支持复杂的端口连接配置

4. **VerilogMergeConnection**
   - 表示多个源端口合并到一个目标端口的连接关系
   - 管理多个源端口的位宽分配和合并逻辑

5. **VerilogModuleCollection**
   - 表示模块集合，用于管理整个项目的所有模块
   - 提供模块的添加、查找、删除等操作
   - 支持模块层级结构的维护

#### 数据结构关系

##### 1. VerilogPort

**核心属性**
- `name`: 端口名称
- `direction`: 端口方向（'input'、'output'或'inout'）
- `father_module`: 端口所属的模块实例
- `width`: 端口位宽，格式为 `{'high': int, 'low': int}`
- `source`: 输入信号的源头端口（在v2.0.0后被connection替代）
- `connection`: 存储端口的连接对象（VerilogConnection或VerilogMergeConnection）
- `destinations`: 存储多个目标端口的列表

**核心方法**
- `get_port_info()`: 获取端口信息，返回格式为 "端口类型, 模块名.端口名, 端口位宽"
- `get_width_value()`: 计算并返回端口的位宽值（high - low + 1）
- `get_bit_range()`: 获取端口的位宽范围
- `is_input()/is_output()/is_inout()`: 判断端口类型的便捷方法

##### 2. VerilogModule

**核心属性**
- `name`: 模块实例名称
- `file_path`: 模块所在文件路径
- `module_def_name`: 模块定义名称
- `ports`: 存储模块端口的列表
- `parameters`: 存储模块参数的字典
- `includes`: 存储包含的模块对象列表
- `top_module`: 指向顶级模块的引用
- `need_gen`: 是否需要生成该模块的Verilog代码

**核心方法**
- `add_port()`: 向模块添加单个端口
- `add_ports()`: 向模块添加多个端口
- `get_ports_by_direction()`: 根据方向获取端口列表
- `get_input_ports()/get_output_ports()/get_inout_ports()`: 获取特定类型的端口
- `get_port()`: 根据端口名称查找端口对象
- `get_connections_summary()`: 获取模块的连接摘要信息

##### 3. VerilogConnection

**核心属性**
- `source_port`: 源端口实例
- `dest_port`: 目标端口实例
- `source_bit_range`: 源端口使用的位范围
- `dest_bit_range`: 目标端口使用的位范围
- `source_module_name`: 源端口所属模块名称
- `dest_module_name`: 目标端口所属模块名称

**核心方法**
- `_check_range()`: 验证连接的位范围是否有效
- `_validate_bit_range()`: 验证位范围是否在端口位宽范围内
- `__str__()`: 返回连接的字符串表示，用于日志和显示

##### 4. VerilogMergeConnection (继承自VerilogConnection)

**核心属性**
- `type`: 合并类型（默认为'joint'）
- `source_port_list`: 存储多个源端口的列表
- `source_range_list`: 存储多个源端口位范围的列表
- `gui_data_list`: 存储GUI相关数据的列表

**核心方法**
- `_check_range()`: 重写父类方法，验证所有源端口的位范围
- `__str__()`: 重写父类方法，返回合并连接的字符串表示

##### 5. VerilogModuleCollection

**核心属性**
- `modules`: 存储所有模块的列表
- `connections`: 存储所有连接的列表
- `tie_0_port`: 系统Tie-0端口（常0信号）
- `tie_1_port`: 系统Tie-1端口（常1信号）
- `system_module`: 系统模块，包含Tie-0和Tie-1端口

**核心方法**
- `tie01_for_port()`: 将Tie-0或Tie-1端口连接到指定端口
- `get_all_connections_info()`: 获取所有连接的信息
- `get_connections_by_instance_name()`: 根据实例名获取连接信息
- `get_unconnected_ports_info()`: 获取所有未连接的端口信息

##### 数据结构间的关系

- **VerilogModule与VerilogPort**: 一对多关系，一个模块包含多个端口
- **VerilogPort与VerilogPort**: 通过source和destinations属性建立连接关系
- **VerilogPort与VerilogConnection/VerilogMergeConnection**: 端口通过connection属性引用连接对象
- **VerilogModule与VerilogModule**: 通过includes和top_module属性建立模块间的包含和层级关系
- **VerilogModuleCollection与VerilogModule**: 一对多关系，一个模块集合包含多个模块
- **VerilogModuleCollection与VerilogConnection**: 一对多关系，一个模块集合包含多个连接

### UI界面调用逻辑

#### 程序启动流程

1. **初始化阶段**
   - 创建WGenGUI类实例，初始化版本号、解析器、文件处理器等核心组件
   - 设置界面主题和初始窗口大小
   - 绑定快捷键事件（空格键创建连接、Ctrl+Z撤销操作）

2. **启动对话框**
   - 显示启动选择对话框，让用户选择继续上一次工作或打开新的配置文件
   - 根据用户选择执行相应操作：打开数据库或配置文件

3. **界面布局创建**
   - 调用`_create_layout()`方法创建主界面布局
   - 设置菜单、工具栏、模块列表、电路图画布等界面元素

#### 核心功能调用流程

1. **模块加载流程**
   - 用户选择配置文件或数据库文件
   - 文件处理器读取文件内容
   - Verilog解析器解析模块信息
   - 创建并初始化VerilogModule和VerilogPort实例
   - 将模块添加到模块集合中并显示在界面上

2. **连接创建流程**
   - 用户选择源模块和目标模块的端口
   - 点击"创建连接"按钮或按空格键
   - 程序验证端口方向和位宽是否匹配
   - 创建VerilogConnection或VerilogMergeConnection实例
   - 更新端口的连接关系并在画布上显示连接

3. **撤销操作流程**
   - 用户按Ctrl+Z触发撤销操作
   - 程序从历史记录栈中恢复上一个状态
   - 更新界面显示和模块连接关系

4. **配置生成流程**
   - 用户点击"生成配置"按钮
   - 程序收集所有模块和连接信息
   - 配置生成器生成Verilog配置文件
   - 将生成的配置文件保存到用户指定的位置

## 常见问题

1. **程序启动失败**
   - 检查Python版本是否符合要求
   - 检查是否安装了必要的依赖库
   - 检查是否有错误的配置文件

2. **模块加载失败**
   - 检查Verilog文件是否存在
   - 检查Verilog文件格式是否正确
   - 检查配置文件中的模块路径是否正确

3. **连接创建失败**
   - 检查端口是否存在
   - 检查端口类型是否匹配
   - 检查位范围是否正确

## 更新日志

### 最新修改

1. **在Add Row按钮上方添加了提示文字**
   ```python
   tips_str = "Tips:\n Line 1 is MSB(high),\n Last is LSB(low)."
   tip_label = ttk.Label(button_frame, text=tips_str, justify=tk.LEFT, wraplength=120)
   tip_label.pack(pady=(5, 10), padx=5)
   ```

2. **调整了按钮框架与左侧列表视图的距离**
   ```python
   button_frame.pack(side=tk.RIGHT, padx=(10, 10), pady=10, fill=tk.NONE)
   ```

## 许可证

[MIT License](LICENSE)