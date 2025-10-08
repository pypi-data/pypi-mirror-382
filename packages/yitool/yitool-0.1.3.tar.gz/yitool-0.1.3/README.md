# @yitech/yitool 工具包

<div align="center">
  <img src="https://via.placeholder.com/200" alt="yitool Logo" style="max-width: 200px;" />
  <h1>yitool</h1>
  <p>功能丰富的 Python 工具包，让开发更高效、更简单</p>
  <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python Version" />
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
    <img src="https://img.shields.io/badge/test-passed-brightgreen" alt="Test Status" />
    <img src="https://img.shields.io/badge/coverage-high-blueviolet" alt="Code Coverage" />
  </div>
</div>

## 快速开始

### 安装

使用 pip 安装（推荐开发模式）：

```bash
# 直接安装
pip install .

# 开发模式安装（推荐）
pip install -e .
```

使用 uv 安装（更快速的包管理器）：

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 使用 uv 安装 yitool
uv pip install -e .
```

### 基本使用示例

```python
# 导入并配置日志
from yitool import log
log.setup_logging(
    level=log.logging.INFO,
    log_file='app.log',   # 可选，日志文件路径
    rotation='10 MB',     # 可选，日志轮转配置
    retention='7 days'    # 可选，日志保留时间
)

# 使用日志功能
log.info("欢迎使用 yitool 工具包！")
log.debug("这是一条调试信息")

# 初始化 Redis 连接
from yitool import yi_redis
redis_client = yi_redis.YiRedis.from_env()  # 从环境变量加载配置
log.info(f"Redis 连接成功")

# 设置和获取键值
redis_client.set("greeting", "Hello, yitool!")
greeting = redis_client.get("greeting")
log.info(f"获取到的问候语: {greeting}")

# 使用工具函数
from yitool.utils import str_utils
camel_case = str_utils.StrUtils.camelize("hello_world")
log.info(f"驼峰命名转换: hello_world -> {camel_case}")
```

## 项目介绍

yitool 是一个精心设计的 Python 工具包，旨在提供丰富、实用的工具函数和类，简化日常开发工作，提高开发效率。该工具包集成了数据库操作、缓存管理、文件处理、字符串转换、系统信息获取等多种功能模块，可以满足各种开发场景的需求。

### 为什么选择 yitool？

- **一站式解决方案**：提供从数据库操作到文件处理、从缓存管理到系统信息获取的全方位工具
- **开箱即用**：无需复杂配置，简单导入即可使用
- **类型安全**：完整的类型注解，提供更好的IDE支持和代码提示
- **丰富的文档**：每个功能都有详细的文档和使用示例
- **灵活扩展**：良好的架构设计，便于根据需求进行扩展
- **持续维护**：定期更新和完善，确保代码质量和稳定性

### 主要特点

- **模块化设计**：清晰的模块划分，便于使用和维护
- **丰富的工具集**：涵盖开发中的常见需求
- **易于扩展**：良好的架构设计，便于自定义扩展
- **完整的测试**：全面的单元测试，确保代码质量
- **类型提示**：完善的类型注解，提升开发体验
- **增强的错误处理**：详细的异常信息和日志记录，便于调试
- **环境友好**：支持从环境变量和配置文件加载设置，便于不同环境部署

## 功能列表

### 核心工具模块

| 模块名称 | 文件位置 | 主要功能 | 使用场景 |
|---------|----------|---------|---------|
| **数据库操作** | `yi_db.py` | 基于 SQLAlchemy 的高级封装，简化数据库连接、查询和事务管理，支持数据框操作 | 数据库应用开发、数据处理、ORM操作 |
| **Redis 操作** | `yi_redis.py` | 基于 redis-py 的扩展封装，提供更便捷的 Redis 操作接口，支持缓存、发布/订阅等功能 | 缓存管理、分布式锁、消息队列、会话存储 |
| **日志管理** | `log.py` | 基于 rich 的增强日志系统，提供美观、功能强大的日志输出，支持多级别日志控制和文件日志 | 应用日志记录、调试、监控 |
| **环境配置** | `utils/env_utils.py` | 环境变量和配置文件管理工具，支持从 `.env` 文件加载配置 | 多环境配置管理、敏感信息保护 |

### 工具函数集

**基础数据处理**

| 模块名称 | 文件位置 | 主要功能 |
|---------|----------|---------|
| **数组/列表处理** | `utils/arr_utils.py` | 数组去重、合并、分割、查找、排序等实用操作 |
| **字典处理** | `utils/dict_utils.py` | 字典合并、深拷贝、扁平化、结构化、差异比较等实用函数 |
| **字符串处理** | `utils/str_utils.py` | 字符串格式化、转换、验证、命名规范转换等工具函数 |
| **转换工具** | `utils/convert_utils.py` | 不同数据类型之间的相互转换，提供安全的数据类型转换 |

**文件与配置**

| 模块名称 | 文件位置 | 主要功能 |
|---------|----------|---------|
| **文件操作** | `utils/file_utils.py` | 文件读写、复制、移动、删除、压缩解压等功能 |
| **文件路径** | `utils/path_utils.py` | 路径解析、创建、检查、规范化等工具函数 |
| **JSON 处理** | `utils/json_utils.py` | JSON 文件和数据的增强处理，支持复杂数据结构 |
| **YAML 处理** | `utils/yaml_utils.py` | YAML 文件和数据的处理，支持配置文件读写 |
| **加密工具** | `utils/crypto_utils.py` | 哈希计算、编码解码、加密解密等安全相关功能 |

**日期与时间**

| 模块名称 | 文件位置 | 主要功能 |
|---------|----------|---------|
| **日期时间** | `utils/date_utils.py` | 日期时间格式化、转换、计算、时区处理等工具 |

**系统与网络**

| 模块名称 | 文件位置 | 主要功能 |
|---------|----------|---------|
| **系统信息** | `utils/system_utils.py` | 获取系统信息、网络信息、进程管理、性能监控等功能 |
| **URL 处理** | `utils/url_utils.py` | URL 解析、构建、编码解码、验证等工具 |

**高级功能**

| 模块名称 | 文件位置 | 主要功能 |
|---------|----------|---------|
| **类操作** | `utils/class_utils.py` | 类属性和方法操作、动态属性、单例模式等高级特性 |
| **函数工具** | `utils/fun_utils.py` | 函数装饰器、重试机制、性能监控、异步支持等高级功能 |
| **ID 生成** | `utils/id_utils.py` | 唯一 ID 生成工具，支持 UUID、雪花算法、自定义 ID 等 |
| **随机数生成** | `utils/random_utils.py` | 安全随机数、随机字符串、随机选择等功能 |

### 共享组件

- **发布/订阅模式** (`pubsub.py`): 基于线程的发布/订阅模式实现，支持事件驱动编程
- **订阅者模式** (`subscriber.py`): 基于 Tornado IOLoop 的异步订阅者实现
- **定时任务** (`cron.py`): 强大的定时任务调度器，支持复杂的 cron 表达式
- **栈结构** (`stack.py`): 线程安全的栈数据结构实现
- **任务存储** (`job_store.py`): 异步任务存储和调度系统

## 安装指南

### 方式一：使用 uv（推荐）

uv 是一个快速的 Python 包管理器，推荐用于安装 yitool：

```bash
# 安装 uv 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或者使用 pip
pip install uv

# 安装 yitool 包
uv pip install .

# 开发模式安装（推荐用于开发环境）
uv pip install -e .
```

### 方式二：使用 pip

```bash
# 直接安装
pip install .

# 开发模式安装
pip install -e .
```

## 环境配置

项目支持通过 `.env` 文件进行配置。复制 `env.example` 到 `.env` 并根据需要修改配置项：

```bash
cp env.example .env
# 使用您喜欢的编辑器编辑 .env 文件
vi .env
```

### 主要环境变量配置

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

```

## 使用示例

### 1. 数据库操作示例

```python
from yitool.yi_db import YiDB
import polars as pl

# 从环境变量创建数据库实例
# db = YiDB.from_env()

# 或手动创建实例
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://username:password@host:port/database')
db = YiDB(engine)

# 连接数据库
if db.connect():
    print("数据库连接成功")
    
    # 执行查询并返回 DataFrame
    df = db.read('SELECT * FROM users LIMIT 10')
    print(df)
    
    # 使用 Polars DataFrame 进行插入
    new_data = pl.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    db.insert('users', new_data)
    
    # 执行事务
    with db.transaction():
        db.execute('UPDATE users SET status = :status WHERE id = :id', {'status': 1, 'id': 1})
        db.execute('INSERT INTO audit_log (action, user_id) VALUES (:action, :user_id)', 
                  {'action': 'update', 'user_id': 1})
    
    # 关闭连接
    db.close()
else:
    print("数据库连接失败")
```

### 2. Redis 操作示例

```python
from yitool.yi_redis import YiRedis

# 从环境变量创建实例（推荐）
# redis_client = YiRedis.from_env()

# 或手动创建实例
redis_client = YiRedis(
    host='localhost',
    port=6379,
    db=0,
    password='your_password'
)

# 设置带过期时间的值
redis_client.set('key', 'value', expire=3600)  # 1小时后过期

# 获取值
value = redis_client.get('key')
print(value)  # 输出: value

# 哈希操作
redis_client.hset('user:1', 'name', 'John')
redis_client.hset('user:1', 'age', 30)
user_info = redis_client.hgetall('user:1')
print(user_info)  # 输出: {'name': 'John', 'age': '30'}

# 列表操作
redis_client.lpush('tasks', 'task1', 'task2')
task = redis_client.rpop('tasks')
print(task)  # 输出: task1

# 发布/订阅
redis_client.publish('notifications', 'New message')

# 清除匹配模式的键
count = redis_client.clear('cache:*')
print(f'清除了 {count} 个缓存键')
```

### 3. 日志使用示例

```python
from yitool.log import logger, setup_logging
import logging

# 配置日志
setup_logging(
    level=logging.DEBUG,  # 日志级别
    log_file='app.log',   # 日志文件（可选）
    rotation='10 MB',     # 日志轮转（可选）
    retention='7 days'    # 日志保留时间（可选）
)

# 记录不同级别的日志
logger.debug('这是一条调试信息')
logger.info('这是一条普通信息')
logger.warning('这是一条警告信息')
logger.error('这是一条错误信息')
logger.critical('这是一条严重错误信息')

# 记录异常信息
try:
    1/0
except Exception as e:
    logger.exception('发生异常')  # 自动记录异常栈信息

# 使用丰富的格式化功能
user = {'id': 1, 'name': 'John'}
logger.info('用户信息: %s', user)  # 自动美化输出
```

### 4. 工具函数使用示例

```python
# 字符串处理
def str_utils_example():
    from yitool.utils.str_utils import StrUtils
    
    # 驼峰命名转换
    camel_case = StrUtils.camelize('hello_world')  # 'helloWorld'
    snake_case = StrUtils.decamelize('helloWorld')  # 'hello_world'
    pascal_case = StrUtils.pascalize('hello_world')  # 'HelloWorld'
    
    # 字符串验证
    is_email = StrUtils.is_email('test@example.com')  # True
    is_url = StrUtils.is_url('https://example.com')  # True
    
    # 字符串格式化
    formatted = StrUtils.format_case('hello_world', 'pascal')  # 'HelloWorld'
    print(f"字符串处理示例: {camel_case}, {snake_case}, {pascal_case}")

# 字典处理
def dict_utils_example():
    from yitool.utils.dict_utils import DictUtils
    
    # 深拷贝字典
    original = {'a': 1, 'b': {'c': 2}}
    copy = DictUtils.deep_copy(original)
    
    # 合并字典
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    merged = DictUtils.merge(dict1, dict2)  # {'a': 1, 'b': 3, 'c': 4}
    
    # 扁平化字典
    nested = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    flat = DictUtils.flatten(nested)  # {'a': 1, 'b.c': 2, 'b.d.e': 3}
    
    print(f"字典处理示例: {merged}, {flat}")

# 日期时间处理
def date_utils_example():
    from yitool.utils.date_utils import DateUtils
    import datetime
    
    # 获取当前时间
    now = DateUtils.now()
    
    # 格式化日期
    formatted = DateUtils.format(now, '%Y-%m-%d %H:%M:%S')
    
    # 解析日期字符串
    parsed = DateUtils.parse('2023-01-01 12:00:00')
    
    # 日期计算
    tomorrow = DateUtils.add_days(now, 1)
    days_diff = DateUtils.diff_days(now, tomorrow)  # 1
    
    print(f"日期处理示例: 现在={formatted}, 明天={DateUtils.format(tomorrow)}")

# 运行示例
def run_examples():
    str_utils_example()
    dict_utils_example()
    date_utils_example()

if __name__ == "__main__":
    run_examples()
```

### 5. 系统工具使用示例

```python
from yitool.utils.system_utils import SystemUtils

# 获取系统信息
def system_info_example():
    # 操作系统信息
    os_info = SystemUtils.get_os_info()
    print(f"操作系统: {os_info['system']} {os_info['version']}")
    
    # Python 解释器信息
    python_info = SystemUtils.get_python_info()
    print(f"Python 版本: {python_info['version']} ({python_info['implementation']})")
    
    # CPU 信息
    cpu_info = SystemUtils.get_cpu_info()
    print(f"CPU 核心数: {cpu_info['physical_cores']} 物理核心, {cpu_info['total_cores']} 总核心")
    
    # 内存信息
    memory_info = SystemUtils.get_memory_info()
    total_gb = memory_info['total'] / (1024**3)  # 转换为 GB
    used_gb = memory_info['used'] / (1024**3)
    print(f"内存使用: {used_gb:.2f}/{total_gb:.2f} GB ({memory_info['percent']}%)")
    
    # 磁盘信息
    disk_info = SystemUtils.get_disk_info('/')
    disk_total_gb = disk_info['total'] / (1024**3)
    disk_used_gb = disk_info['used'] / (1024**3)
    print(f"磁盘使用: {disk_used_gb:.2f}/{disk_total_gb:.2f} GB ({disk_info['percent']}%)")
    
    # IP 地址信息
    ip_addresses = SystemUtils.get_ip_addresses()
    print("网络接口 IP 地址:")
    for if_name, ip in ip_addresses:
        print(f"  {if_name}: {ip}")

if __name__ == "__main__":
    system_info_example()
```

## 项目结构

```
yitool/
├── __init__.py         # 包初始化文件
├── __main__.py         # 命令行入口
├── cli.py              # 命令行接口
├── cli.conf            # 命令行配置
├── yi_db.py            # 数据库操作工具
├── yi_redis.py         # Redis 操作工具
├── log.py              # 日志管理工具
├── const.py            # 常量定义
├── enums.py            # 枚举类型定义
├── exceptions.py       # 自定义异常类
├── db/                 # 数据库相关模块
│   ├── __init__.py
│   └── db.py           # 数据库核心功能实现
├── utils/              # 工具函数集合
│   ├── __init__.py
│   ├── _humps.py       # 内部使用的命名转换工具
│   ├── arr_utils.py    # 数组/列表处理工具
│   ├── class_utils.py  # 类操作工具
│   ├── convert_utils.py # 类型转换工具
│   ├── date_utils.py   # 日期时间工具
│   ├── dict_utils.py   # 字典处理工具
│   ├── env_utils.py    # 环境变量工具
│   ├── fun_utils.py    # 函数处理工具
│   ├── id_utils.py     # ID 生成工具
│   ├── json_utils.py   # JSON 处理工具
│   ├── path_utils.py   # 文件路径工具
│   ├── random_utils.py # 随机数工具
│   ├── str_utils.py    # 字符串处理工具
│   ├── system_utils.py # 系统信息工具
│   ├── url_utils.py    # URL 处理工具
│   └── yaml_utils.py   # YAML 处理工具
├── shared/             # 共享组件
│   ├── __init__.py
│   ├── cron.py         # 定时任务调度器
│   ├── modified.py     # 修饰器集合
│   ├── pubsub.py       # 发布/订阅模式实现
│   ├── stack.py        # 栈数据结构
│   └── subscriber.py   # 订阅者模式实现
└── misc/               # 杂项功能
    ├── __init__.py
    └── job_store.py    # 任务存储系统
```

## 运行测试

项目包含完整的单元测试套件，确保代码质量和功能正确性：

```bash
# 运行所有测试
pytest

# 详细模式运行测试
pytest -v

# 运行特定文件的测试
pytest tests/test_yi_db.py

# 运行特定模块的测试
pytest tests/utils/

# 生成测试覆盖率报告
pytest --cov=yitool tests/
```

## 常见问题

### 1. 安装时出现依赖错误

**问题**：安装过程中出现依赖包版本冲突或安装失败。

**解决方案**：
- 使用 uv 包管理器可以解决大多数依赖冲突问题：`uv pip install -e .`
- 确保您的 Python 版本符合要求（>=3.10）
- 尝试先更新 pip：`pip install --upgrade pip`

### 2. 数据库连接失败

**问题**：无法连接到数据库，出现连接错误。

**解决方案**：
- 检查 `.env` 文件中的数据库配置是否正确
- 确保数据库服务正在运行
- 验证数据库用户权限是否正确
- 检查网络连接和防火墙设置

### 3. Redis 操作超时

**问题**：执行 Redis 操作时出现超时错误。

**解决方案**：
- 检查 Redis 服务器是否正在运行
- 验证 Redis 连接配置是否正确
- 检查网络连接状况
- 考虑增加超时时间配置

### 4. 导入错误

**问题**：导入 yitool 模块时出现错误。

**解决方案**：
- 确保已正确安装 yitool 包
- 检查 Python 路径配置
- 尝试使用开发模式重新安装：`pip install -e .`

## 贡献指南

我们欢迎社区贡献，共同改进 yitool 工具包。贡献的方式包括但不限于：

1. **报告问题**：在项目仓库中提交 Issue，描述问题的详细情况
2. **修复 Bug**：解决已报告的问题，提交 Pull Request
3. **添加功能**：实现新功能或改进现有功能
4. **完善文档**：修正文档错误，补充使用示例

### 代码规范

- 遵循 PEP 8 代码风格指南
- 使用类型提示提升代码可读性
- 为新函数和类添加详细的文档字符串
- 确保所有测试通过

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 联系方式

如有问题或建议，请联系项目维护者：

- Tony Chen
- Email: chruit@outlook.com
- 项目地址：https://gitee.com/yi_tech/yitool
