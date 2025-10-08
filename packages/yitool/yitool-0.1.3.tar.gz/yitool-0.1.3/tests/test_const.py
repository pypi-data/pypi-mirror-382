# -*- coding: utf-8 -*-
import pytest
from yitool.const import __PKG__, __VERSION__, __ENV__


class TestConst:
    """常量定义的测试类"""

    def test_pkg_constant(self):
        """测试 __PKG__ 常量"""
        assert __PKG__ == 'yitool'
        assert isinstance(__PKG__, str)
    
    def test_version_constant(self):
        """测试 __VERSION__ 常量"""
        assert __VERSION__ == '0.1.0'
        assert isinstance(__VERSION__, str)
        # 确保版本号符合语义化版本规范的基本格式
        parts = __VERSION__.split('.')
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()
    
    def test_env_constant(self):
        """测试 __ENV__ 常量"""
        assert __ENV__ == '/etc/yitech/.env'
        assert isinstance(__ENV__, str)
        # 确保路径格式正确
        assert __ENV__.startswith('/')  # 应该是绝对路径