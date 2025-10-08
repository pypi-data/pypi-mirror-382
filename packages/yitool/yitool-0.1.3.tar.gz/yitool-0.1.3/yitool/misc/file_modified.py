import os
import glob
from datetime import datetime
from typing import Dict, List, Optional, Sequence
import multiprocessing
import weakref
from abc import ABC
from tornado import ioloop
from tornado import process
from yitool.log import logger
from yitool.shared.modified import Modified, ModifiedModel


class FileModified(Modified):
    """文件变更监听器，用于监听指定目录下的文件变更"""
    
    def __init__(
            self,
            queue: multiprocessing.Queue,
            watch_dirs: List[str],
            file_patterns: Optional[List[str]] = None,
            recursive: bool = False,
            update_times: Dict[str, datetime] = {},
            sorted_update_keys: Optional[Sequence[str]] = None,
        ) -> None:
        """
        初始化文件变更监听器
        
        Args:
            queue: 用于通知变更的队列
            watch_dirs: 要监听的目录列表
            file_patterns: 文件匹配模式列表，例如 ['*.txt', '*.py']，如果为 None 则不过滤
            recursive: 是否递归监听子目录
            update_times: 初始的文件更新时间映射
            sorted_update_keys: 更新键的排序规则
        """
        super().__init__(queue, update_times, sorted_update_keys)
        self._watch_dirs = watch_dirs
        self._file_patterns = file_patterns
        self._recursive = recursive
        
        # 初始化时获取一次文件更新时间
        self._update_times = self.fetch_update_times()
    
    def fetch_update_times(self) -> Dict[str, datetime]:
        """
        获取所有监控文件的最后修改时间
        
        Returns:
            文件路径到最后修改时间的映射
        """
        update_times: Dict[str, datetime] = {}
        
        for watch_dir in self._watch_dirs:
            if not os.path.exists(watch_dir):
                logger.warning(f"监控目录不存在: {watch_dir}")
                continue
            
            if not os.path.isdir(watch_dir):
                logger.warning(f"监控路径不是目录: {watch_dir}")
                continue
            
            try:
                if self._recursive:
                    # 递归查找所有文件
                    for root, _, files in os.walk(watch_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if self._should_process_file(file_path):
                                update_times[file_path] = self._get_file_mtime(file_path)
                else:
                    # 仅查找当前目录下的文件
                    for item in os.listdir(watch_dir):
                        item_path = os.path.join(watch_dir, item)
                        if os.path.isfile(item_path) and self._should_process_file(item_path):
                            update_times[item_path] = self._get_file_mtime(item_path)
            except Exception as e:
                logger.error(f"获取目录 {watch_dir} 下的文件信息失败: {e}")
        
        return update_times
    
    def _should_process_file(self, file_path: str) -> bool:
        """
        判断文件是否应该被处理
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否应该处理该文件
        """
        if self._file_patterns is None:
            return True
        
        # 检查文件是否匹配任何模式
        file_name = os.path.basename(file_path)
        for pattern in self._file_patterns:
            # 简单的通配符匹配
            if self._match_pattern(file_name, pattern):
                return True
        
        return False
    
    def _match_pattern(self, file_name: str, pattern: str) -> bool:
        """
        检查文件名是否匹配模式
        
        Args:
            file_name: 文件名
            pattern: 匹配模式
        
        Returns:
            是否匹配
        """
        # 这里实现简单的通配符匹配，可以根据需要扩展
        if '*' not in pattern and '?' not in pattern:
            return file_name == pattern
        
        # 转换为简单的正则表达式进行匹配
        regex_pattern = pattern.replace('.', '\\.').replace('*', '.*').replace('?', '.')
        import re
        return bool(re.match(f'^{regex_pattern}$', file_name))
    
    def _get_file_mtime(self, file_path: str) -> datetime:
        """
        获取文件的最后修改时间
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件的最后修改时间
        """
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime)
        except Exception as e:
            logger.error(f"获取文件 {file_path} 的修改时间失败: {e}")
            # 返回当前时间作为默认值
            return datetime.now()
    
    def add_watch_dir(self, watch_dir: str) -> None:
        """
        添加要监控的目录
        
        Args:
            watch_dir: 要监控的目录路径
        """
        if watch_dir not in self._watch_dirs:
            self._watch_dirs.append(watch_dir)
            # 立即更新文件时间映射
            new_files = self.fetch_update_times()
            for file_path, mtime in new_files.items():
                if file_path not in self._update_times:
                    self._update_times[file_path] = mtime
    
    def remove_watch_dir(self, watch_dir: str) -> None:
        """
        移除要监控的目录
        
        Args:
            watch_dir: 要移除的监控目录路径
        """
        if watch_dir in self._watch_dirs:
            self._watch_dirs.remove(watch_dir)
            # 移除与该目录相关的所有文件
            dir_prefix = watch_dir.rstrip(os.path.sep) + os.path.sep
            files_to_remove = [f for f in self._update_times if f.startswith(dir_prefix)]
            for file_path in files_to_remove:
                del self._update_times[file_path]
    
    def update_file_patterns(self, file_patterns: Optional[List[str]]) -> None:
        """
        更新文件匹配模式
        
        Args:
            file_patterns: 新的文件匹配模式列表
        """
        self._file_patterns = file_patterns
        # 立即更新文件时间映射
        self._update_times = self.fetch_update_times()