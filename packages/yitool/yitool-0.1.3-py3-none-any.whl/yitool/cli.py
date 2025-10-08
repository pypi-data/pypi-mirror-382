# -*- coding: utf-8 -*-
"""命令行入口"""

import argparse
import sys
import importlib
from os import path
from typing import Optional, List, Dict, Callable
from tornado import options
from yitool.log import logger, setup_logging

# 设置日志
setup_logging()

class Cli:
    """命令行接口类，参考uv命令设计风格"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='yi',
            description='功能丰富的 Python 工具包，让开发更高效、更简单',
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False
        )
        
        # 全局选项
        global_group = self.parser.add_argument_group('Global options')
        global_group.add_argument('-h', '--help', action='store_true', help='显示此命令的简要帮助')
        global_group.add_argument('-v', '--version', action='store_true', help='显示 yi 版本')
        
        # 子命令
        self.subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        
        # 初始化所有子命令
        self._init_subcommands()
        
    def _init_subcommands(self):
        """初始化所有子命令"""
        # 工具模块映射
        utils_commands = {
            'arr': ('arr_utils', '数组/列表处理工具'),
            'class': ('class_utils', '类操作工具'),
            'convert': ('convert_utils', '类型转换工具'),
            'date': ('date_utils', '日期时间工具'),
            'dict': ('dict_utils', '字典处理工具'),
            'env': ('env_utils', '环境变量工具'),
            'fun': ('fun_utils', '函数处理工具'),
            'id': ('id_utils', 'ID 生成工具'),
            'json': ('json_utils', 'JSON 处理工具'),
            'path': ('path_utils', '文件路径工具'),
            'random': ('random_utils', '随机数工具'),
            'str': ('str_utils', '字符串处理工具'),
            'system': ('system_utils', '系统信息工具'),
            'url': ('url_utils', 'URL 处理工具'),
            'yaml': ('yaml_utils', 'YAML 处理工具'),
        }
        
        # 创建通用工具命令
        for cmd_name, (module_name, help_text) in utils_commands.items():
            subparser = self.subparsers.add_parser(cmd_name, help=help_text)
            subparser.add_argument('method', help=f'{module_name} 模块中的方法名')
            subparser.add_argument('args', nargs='*', help='方法参数')
            subparser.add_argument('--kwargs', nargs='*', help='关键字参数，格式为 key=value')
            
        # 创建特殊命令
        self._create_special_commands()
    
    def _create_special_commands(self):
        """创建特殊命令"""
        # 数据库命令
        db_parser = self.subparsers.add_parser('db', help='数据库操作')
        db_parser.add_argument('action', choices=['connect', 'query', 'insert', 'update', 'delete'], help='数据库操作')
        db_parser.add_argument('args', nargs='*', help='操作参数')
        
        # Redis命令
        redis_parser = self.subparsers.add_parser('redis', help='Redis操作')
        redis_parser.add_argument('action', choices=['get', 'set', 'delete', 'keys', 'flush'], help='Redis操作')
        redis_parser.add_argument('args', nargs='*', help='操作参数')
        
        # 帮助命令
        help_parser = self.subparsers.add_parser('help', help='显示命令文档')
        help_parser.add_argument('command', nargs='?', help='要查看帮助的命令')
    
    def __call__(self, *args, **kwds):
        """执行命令行"""
        # 解析命令行参数
        args_parsed = self.parser.parse_args()
        
        # 处理全局选项
        if args_parsed.help:
            if args_parsed.command:
                # 显示特定命令的帮助
                if args_parsed.command in [p.prog.split()[-1] for p in self.subparsers.choices.values()]:
                    self.subparsers.choices[args_parsed.command].print_help()
                else:
                    self.parser.print_help()
            else:
                self.parser.print_help()
            return
        
        if args_parsed.version:
            from yitool.const import __VERSION__
            print(f'yi v{__VERSION__}')
            return
        
        # 处理子命令
        if not args_parsed.command:
            self.parser.print_help()
            return
        
        # 执行对应的命令
        self._execute_command(args_parsed)
    
    def _execute_command(self, args_parsed):
        """执行命令"""
        try:
            if args_parsed.command == 'help':
                self._handle_help_command(args_parsed)
            elif args_parsed.command == 'db':
                self._handle_db_command(args_parsed)
            elif args_parsed.command == 'redis':
                self._handle_redis_command(args_parsed)
            else:
                self._handle_utils_command(args_parsed)
        except Exception as e:
            logger.error(f'命令执行失败: {str(e)}')
            sys.exit(1)
    
    def _handle_help_command(self, args_parsed):
        """处理帮助命令"""
        if args_parsed.command:
            if args_parsed.command in [p.prog.split()[-1] for p in self.subparsers.choices.values()]:
                self.subparsers.choices[args_parsed.command].print_help()
            else:
                self.parser.print_help()
        else:
            self.parser.print_help()
    
    def _handle_db_command(self, args_parsed):
        """处理数据库命令"""
        from yitool.yi_db import YiDB
        
        logger.info(f'执行数据库操作: {args_parsed.action}')
        # 这里实现数据库命令的具体逻辑
        # 示例实现
        print(f'数据库操作: {args_parsed.action}, 参数: {args_parsed.args}')
    
    def _handle_redis_command(self, args_parsed):
        """处理Redis命令"""
        from yitool.yi_redis import YiRedis
        
        logger.info(f'执行Redis操作: {args_parsed.action}')
        # 这里实现Redis命令的具体逻辑
        # 示例实现
        print(f'Redis操作: {args_parsed.action}, 参数: {args_parsed.args}')
    
    def _handle_utils_command(self, args_parsed):
        """处理工具命令"""
        # 获取工具模块名
        utils_mapping = {
            'arr': 'arr_utils',
            'class': 'class_utils',
            'convert': 'convert_utils',
            'date': 'date_utils',
            'dict': 'dict_utils',
            'env': 'env_utils',
            'fun': 'fun_utils',
            'id': 'id_utils',
            'json': 'json_utils',
            'path': 'path_utils',
            'random': 'random_utils',
            'str': 'str_utils',
            'system': 'system_utils',
            'url': 'url_utils',
            'yaml': 'yaml_utils',
        }
        
        module_name = utils_mapping.get(args_parsed.command)
        if not module_name:
            logger.error(f'未知的工具命令: {args_parsed.command}')
            return
        
        # 导入工具模块
        try:
            module = importlib.import_module(f'yitool.utils.{module_name}')
        except ImportError:
            logger.error(f'无法导入模块: {module_name}')
            return
        
        # 获取工具类
        class_name = f'{module_name.split("_")[0].capitalize()}Utils'
        utils_class = getattr(module, class_name, None)
        if not utils_class:
            logger.error(f'在模块 {module_name} 中未找到类 {class_name}')
            return
        
        # 获取方法
        method_name = args_parsed.method
        method = getattr(utils_class, method_name, None)
        if not method or not callable(method):
            logger.error(f'在类 {class_name} 中未找到可调用的方法 {method_name}')
            return
        
        # 解析关键字参数
        kwargs = {}
        if hasattr(args_parsed, 'kwargs') and args_parsed.kwargs:
            for kwarg in args_parsed.kwargs:
                if '=' in kwarg:
                    key, value = kwarg.split('=', 1)
                    kwargs[key] = value
        
        # 执行方法
        logger.info(f'执行工具方法: {module_name}.{class_name}.{method_name}')
        try:
            result = method(*args_parsed.args, **kwargs)
            if result is not None:
                print(result)
        except Exception as e:
            logger.error(f'方法执行失败: {str(e)}')
            raise
    
    @staticmethod
    def parse_config_file(file_path: Optional[str] = None):
        """解析配置文件"""
        if file_path is None or not path.exists(file_path):
            CLI_CONF = 'cli.conf'
            file_path = path.join(path.dirname(__file__), CLI_CONF)
        options.parse_config_file(file_path)


def main():
    """主入口函数"""
    Cli.parse_config_file()
    cli = Cli()
    cli()


if __name__ == "__main__":
    main()