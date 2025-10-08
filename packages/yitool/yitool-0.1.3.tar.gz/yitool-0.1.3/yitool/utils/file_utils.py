# -*- coding: utf-8 -*-
from typing import Union, Optional, List, BinaryIO
import os
import shutil
import gzip
import zipfile
from pathlib import Path
from yitool.utils.path_utils import PathUtils


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def read_text(path: str, encoding: str = 'utf-8') -> str:
        """读取文本文件内容
        
        Args:
            path: 文件路径
            encoding: 文件编码
        
        Returns:
            文件内容字符串
            
        Raises:
            FileNotFoundError: 如果文件不存在
            IOError: 如果读取文件时发生错误
        """
        PathUtils.raise_if_not_exists(path)
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_text(path: str, content: str, encoding: str = 'utf-8', append: bool = False) -> bool:
        """写入文本内容到文件
        
        Args:
            path: 文件路径
            content: 要写入的内容
            encoding: 文件编码
            append: 是否追加内容
        
        Returns:
            操作是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def read_bytes(path: str) -> bytes:
        """读取二进制文件内容
        
        Args:
            path: 文件路径
        
        Returns:
            文件内容的字节数据
            
        Raises:
            FileNotFoundError: 如果文件不存在
            IOError: 如果读取文件时发生错误
        """
        PathUtils.raise_if_not_exists(path)
        with open(path, 'rb') as f:
            return f.read()
    
    @staticmethod
    def write_bytes(path: str, content: bytes, append: bool = False) -> bool:
        """写入二进制内容到文件
        
        Args:
            path: 文件路径
            content: 要写入的字节数据
            append: 是否追加内容
        
        Returns:
            操作是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            mode = 'ab' if append else 'wb'
            with open(path, mode) as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def copy(source: str, target: str, overwrite: bool = True) -> bool:
        """复制文件或目录
        
        Args:
            source: 源文件或目录路径
            target: 目标文件或目录路径
            overwrite: 是否覆盖已存在的文件
        
        Returns:
            操作是否成功
        """
        try:
            if os.path.isfile(source):
                # 确保目标目录存在
                target_dir = os.path.dirname(target)
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                if os.path.exists(target):
                    if overwrite:
                        os.remove(target)
                    else:
                        return False
                
                shutil.copy2(source, target)
            else:
                # 复制目录
                if os.path.exists(target):
                    if overwrite:
                        shutil.rmtree(target)
                    else:
                        return False
                
                shutil.copytree(source, target)
            return True
        except Exception:
            return False
    
    @staticmethod
    def move(source: str, target: str, overwrite: bool = True) -> bool:
        """移动文件或目录
        
        Args:
            source: 源文件或目录路径
            target: 目标文件或目录路径
            overwrite: 是否覆盖已存在的文件
        
        Returns:
            操作是否成功
        """
        try:
            # 确保目标目录存在
            target_dir = os.path.dirname(target) if os.path.isfile(source) else target
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            if os.path.exists(target):
                if overwrite:
                    if os.path.isfile(target):
                        os.remove(target)
                    else:
                        shutil.rmtree(target)
                else:
                    return False
            
            shutil.move(source, target)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete(path: str) -> bool:
        """删除文件或目录
        
        Args:
            path: 文件或目录路径
        
        Returns:
            操作是否成功
        """
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_dir(path: str) -> bool:
        """创建目录
        
        Args:
            path: 目录路径
        
        Returns:
            操作是否成功
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def size(path: str) -> int:
        """获取文件大小（字节）
        
        Args:
            path: 文件路径
        
        Returns:
            文件大小（字节）
            
        Raises:
            FileNotFoundError: 如果文件不存在
        """
        PathUtils.raise_if_not_exists(path)
        if os.path.isfile(path):
            return os.path.getsize(path)
        else:
            total_size = 0
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size
    
    @staticmethod
    def list_files(dir_path: str, recursive: bool = False, file_types: Optional[list[str]] = None) -> List[str]:
        """列出目录中的文件
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归列出子目录中的文件
            file_types: 过滤的文件类型列表，例如 ['.txt', '.md']，如果为 None 则不过滤
        
        Returns:
            文件路径列表
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return []
        
        result = []
        
        if recursive:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_types is None or any(file_path.endswith(ext) for ext in file_types):
                        result.append(file_path)
        else:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    if file_types is None or any(item_path.endswith(ext) for ext in file_types):
                        result.append(item_path)
        
        return result
    
    @staticmethod
    def gzip_compress(source_path: str, target_path: Optional[str] = None) -> bool:
        """GZip 压缩文件
        
        Args:
            source_path: 源文件路径
            target_path: 目标压缩文件路径，如果为 None 则默认为源文件路径 + '.gz'
        
        Returns:
            操作是否成功
        """
        try:
            if not PathUtils.exists(source_path) or not PathUtils.is_file(source_path):
                return False
            
            if target_path is None:
                target_path = f"{source_path}.gz"
            
            with open(source_path, 'rb') as f_in:
                with gzip.open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def gzip_decompress(source_path: str, target_path: Optional[str] = None) -> bool:
        """GZip 解压缩文件
        
        Args:
            source_path: 源压缩文件路径
            target_path: 目标文件路径，如果为 None 则默认为去掉 .gz 后缀的路径
        
        Returns:
            操作是否成功
        """
        try:
            if not PathUtils.exists(source_path) or not PathUtils.is_file(source_path):
                return False
            
            if target_path is None:
                if source_path.endswith('.gz'):
                    target_path = source_path[:-3]
                else:
                    target_path = f"{source_path}.out"
            
            with gzip.open(source_path, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def zip_compress(source_path: str, target_path: str, include_parent: bool = True) -> bool:
        """ZIP 压缩文件或目录
        
        Args:
            source_path: 源文件或目录路径
            target_path: 目标压缩文件路径
            include_parent: 当压缩目录时，是否包含父目录
        
        Returns:
            操作是否成功
        """
        try:
            if not PathUtils.exists(source_path):
                return False
            
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(source_path):
                    # 压缩单个文件
                    zipf.write(source_path, os.path.basename(source_path))
                else:
                    # 压缩目录
                    for root, _, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if include_parent:
                                arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                            else:
                                arcname = os.path.relpath(file_path, source_path)
                            zipf.write(file_path, arcname)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def zip_decompress(source_path: str, target_dir: str) -> bool:
        """ZIP 解压缩文件
        
        Args:
            source_path: 源压缩文件路径
            target_dir: 目标目录路径
        
        Returns:
            操作是否成功
        """
        try:
            if not PathUtils.exists(source_path) or not PathUtils.is_file(source_path):
                return False
            
            # 确保目标目录存在
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            with zipfile.ZipFile(source_path, 'r') as zipf:
                zipf.extractall(target_dir)
            
            return True
        except Exception:
            return False