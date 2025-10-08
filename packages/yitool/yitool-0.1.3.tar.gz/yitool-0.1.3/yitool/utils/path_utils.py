# -*- coding: utf-8 -*-
from typing import List, Optional
from pathlib import Path

class PathUtils:
    @staticmethod
    def exists(path: str) -> bool:
        return Path(path).exists()
    
    @staticmethod
    def is_file(path: str) -> bool:
        return Path(path).is_file()
    
    @staticmethod
    def is_dir(path: str) -> bool:
        return Path(path).is_dir()
    
    @staticmethod
    def raise_if_not_exists(path: str) -> bool:
        if PathUtils.exists(path):
            return True
        raise FileNotFoundError(f"Path not found: {path}")
    
    @staticmethod
    def is_absolute(path: str) -> bool:
        return Path(path).is_absolute()
    
    @staticmethod
    def absolute(path: str) -> str:
        return str(Path(path).absolute())
    
    @staticmethod
    def filename(path: str) -> str:
        return str(Path(path).name)
    
    @staticmethod
    def join(path: str, *paths: str) -> str:
        return str(Path(path).joinpath(*paths))
    
    @staticmethod
    def subdirs(folder_path: str) -> Optional[List[Path]]:
        """ 获取 folder_path 目录下的所有子目录 """
        folder = Path(folder_path)
        if (not folder.exists()) or (folder.is_dir() == False):
            return None
        
        # 获取文件夹下的所有文件夹
        subdirectories = [subdir.absolute() for subdir in folder.iterdir() if subdir.is_dir()]
        return subdirectories
    
    @staticmethod
    def subfiles(folder_path: str, file_types: Optional[list[str]] =  None) -> Optional[List[Path]]:
        """ 获取 folder_path 目录下的所有子文件
        file_types: 过滤的文件类型列表，例如 ['.txt', '.md']，如果为 None 则不过滤
        """
        folder = Path(folder_path)
        if (not folder.exists()) or folder.is_dir() == False:
            return None
        
        # 获取文件夹下的所有文件和文件夹
        files = [file.absolute() for file in folder.iterdir() if file.is_file()]
        if file_types is None:
            return files
        # 过滤出符合类型的所有文件
        files = [file for file in files if str(file).endswith(file_types)]
        return files