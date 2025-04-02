# 学生生日查询工具

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

通过学号批量查询学生生日的自动化工具，基于学校登录系统实现。

## 功能特性

- ✅ 多线程并发查询（最高支持10线程）
- ✅ 自动验证学号有效性
- ✅ 智能日期范围生成（按年级偏移计算）
- ✅ 支持手动输入或文件批量导入
- ✅ 自动重试机制（网络错误时重试3次）
- ✅ 详细的日志记录系统

## 使用说明

### 安装依赖
```bash
pip install requests
```

### 运行程序
```bash
python birthday_finder.py
```

### 输入方式选择
1. **手动输入**：直接输入单个学号
2. **文件输入**：提供包含学号列表的文本文件（默认读取`login.txt`）

### 输出示例
```
查询结果：
20000901
20010315
未找到生日
无效学号
```

## 文件格式要求
- 输入文件应为纯文本文件
- 每行一个学号，例如：
  ```
  20230001
  20230002
  20230003
  ```

## 技术实现
- 基于`requests`的HTTP会话管理
- 使用`concurrent.futures`实现线程池
- 动态密码生成（`Kskq%YYYYMMDD`格式）
- 自动处理网络超时和重试

## 许可证
本项目采用 **GNU General Public License v3.0** 开源协议。