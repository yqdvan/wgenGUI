# 离线环境配置说明

本文档详细说明如何在无网络的离线环境中运行和调试wgenGUI项目。

## 项目依赖分析

通过分析，项目使用了以下非标准库依赖：

| 依赖库 | 版本 | 用途 | 来源 |
|-------|------|------|------|
| PyYAML | 6.0.3 | YAML文件解析 | 第三方库 |

> 注：除了PyYAML外，项目主要使用Python标准库：tkinter, os, sys, json, copy, datetime等

## 离线环境配置

### 已完成的配置

✅ **第三方库本地化**：所有第三方依赖已复制到`lib`目录中

✅ **导入路径修改**：已修改所有使用第三方库的文件，确保从`lib`目录导入

✅ **环境测试脚本**：提供了离线环境验证工具

### lib目录结构

```
lib/
├── _yaml/          # YAML C扩展模块
├── pyyaml-6.0.3.dist-info/  # PyYAML元数据
└── yaml/           # YAML主模块
    ├── __init__.py
    ├── _yaml.cp311-win_amd64.pyd  # 编译后的C扩展
    └── 其他Python模块文件
```

## 离线环境使用方法

### 1. 复制项目到离线环境

将整个`wgen_GUI`目录（包含`lib`子目录）复制到目标离线环境中。

### 2. 验证离线环境配置

在离线环境中运行以下命令验证配置是否正确：

```bash
# 基本测试
python test_offline_import.py

# 严格离线测试（模拟没有系统安装PyYAML的情况）
python test_strict_offline.py
```

如果测试通过，说明离线环境配置正确。

### 3. 运行项目

```bash
python wgen_GUI.py
```

## 维护说明

### 添加新的第三方依赖

如果需要添加新的第三方依赖到离线环境：

1. **在联网环境下载依赖**：
   ```bash
   pip install <package_name> -t lib/
   ```

2. **修改导入语句**：
   在使用该依赖的Python文件中添加以下代码：
   ```python
   import sys
   import os
   
   # 添加lib目录到Python路径
   sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
   
   # 然后导入第三方库
   import <package_name>
   ```

3. **更新README**：更新本说明文档中的依赖列表

### 常见问题解决

1. **导入错误**：
   - 检查`lib`目录是否存在且包含所需的库
   - 确认导入路径设置正确
   - 检查Python版本兼容性

2. **C扩展模块错误**：
   - 如果在不同操作系统间迁移，可能需要重新下载针对目标平台编译的C扩展模块
   - 可以使用纯Python版本的库（如果可用）

3. **版本兼容性**：
   - 确保`lib`目录中的库版本与项目兼容
   - 记录并更新依赖版本信息

## 测试工具说明

项目提供了两个测试脚本：

- **test_offline_import.py**：基本导入测试，验证依赖是否可用
- **test_strict_offline.py**：严格测试，模拟纯净的离线环境（移除site-packages路径）

这些测试脚本可以帮助验证离线环境配置是否正确。

---

配置完成日期：2024年
配置状态：已验证可用