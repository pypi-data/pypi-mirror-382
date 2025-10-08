# -*- coding: utf-8 -*-
import logging
from os import path
from typing import Optional, Union
from tornado import options, log as tornado_log
from rich.console import Console
from rich.logging import RichHandler
from yitool.const import __PKG__


logger = logging.getLogger(__PKG__)
"""yitool的全局日志对象，基于rich的增强日志系统"""

def setup_logging(
    terminal_width: Union[int, None] = None, 
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None
) -> None:
    """配置日志系统，支持终端美化输出和文件日志
    
    功能特点：
    - 基于rich库的彩色日志输出
    - 支持堆栈跟踪的美化显示
    - 可配置日志文件、轮转和保留策略
    - 自动显示时间、路径和行号信息
    
    Args:
        terminal_width: 终端输出宽度，控制日志显示格式
        level: 日志级别，如logging.DEBUG, logging.INFO, logging.WARNING等
        log_file: 日志文件路径，设置后会同时输出到文件
        rotation: 日志轮转策略，如'10 MB', '1 day'
        retention: 日志保留时间，如'7 days'
    
    Example:
        >>> setup_logging(
        ...     level=logging.DEBUG,  # 日志级别
        ...     log_file='app.log',   # 日志文件（可选）
        ...     rotation='10 MB',     # 日志轮转（可选）
        ...     retention='7 days'    # 日志保留时间（可选）
        ... )
    """
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建rich处理器用于终端输出
    console = Console(width=terminal_width) if terminal_width else None
    rich_handler = RichHandler(
        show_time=True,           # 显示时间戳
        rich_tracebacks=True,     # 美化异常堆栈
        tracebacks_show_locals=True, # 显示本地变量
        markup=True,              # 支持标记语法
        show_path=True,           # 显示文件路径和行号
        console=console,
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        try:
            # 确保日志目录存在
            log_dir = path.dirname(log_file)
            if log_dir and not path.exists(log_dir):
                import os
                os.makedirs(log_dir, exist_ok=True)
                
            # 创建文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=int(rotation.replace(' MB', '')) * 1024 * 1024 if rotation and 'MB' in rotation else 10*1024*1024,
                backupCount=7 if not retention else int(retention.replace(' days', ''))
            )
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}")
    
    # 设置日志级别并关闭传播
    logger.setLevel(level)
    logger.propagate = False
    
    # 记录日志配置信息
    log_level_name = logging.getLevelName(level)
    logger.debug(f"Logging system initialized with level: {log_level_name}")

# 导出常用的日志级别常量，方便用户使用
def debug(msg, *args, **kwargs):
    """记录调试信息"""
    return logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    """记录一般信息"""
    return logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    """记录警告信息"""
    return logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    """记录错误信息"""
    return logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    """记录严重错误信息"""
    return logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
    """记录异常信息，自动包含堆栈跟踪"""
    return logger.exception(msg, *args, **kwargs)
    