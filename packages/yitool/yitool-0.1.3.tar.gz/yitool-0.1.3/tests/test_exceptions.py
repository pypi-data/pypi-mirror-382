# -*- coding: utf-8 -*-
import pytest
from yitool.exceptions import YiToolException


class TestYiToolException:
    """YiToolException 异常类的测试类"""

    def test_exception_inheritance(self):
        """测试 YiToolException 继承自 Exception"""
        assert issubclass(YiToolException, Exception)
    
    def test_exception_raising(self):
        """测试 YiToolException 可以被抛出和捕获"""
        with pytest.raises(YiToolException):
            raise YiToolException("Test exception message")
    
    def test_exception_message(self):
        """测试 YiToolException 的异常消息"""
        exception_message = "Test custom exception message"
        try:
            raise YiToolException(exception_message)
        except YiToolException as e:
            assert str(e) == exception_message
    
    def test_exception_without_message(self):
        """测试 YiToolException 可以不带消息抛出"""
        with pytest.raises(YiToolException):
            raise YiToolException()
        
        # 捕获不带消息的异常并检查其字符串表示
        try:
            raise YiToolException()
        except YiToolException as e:
            assert str(e) == ""  # 或者其他默认字符串
    
    def test_exception_with_multiple_arguments(self):
        """测试 YiToolException 可以接受多个参数"""
        # 由于 YiToolException 直接继承自 Exception，它应该能处理多个参数
        with pytest.raises(YiToolException):
            raise YiToolException("Error", "Code: 404", "Not Found")
        
        # 捕获带多个参数的异常并检查其字符串表示
        try:
            raise YiToolException("Error", "Code: 404")
        except YiToolException as e:
            assert "Error" in str(e)
            assert "Code: 404" in str(e)