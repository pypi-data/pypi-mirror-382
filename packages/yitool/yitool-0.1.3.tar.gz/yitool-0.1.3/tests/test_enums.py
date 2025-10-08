import pytest
from yitool.enums import YiEnum, DB_TYPE


class TestYiEnum:
    """YiEnum 类的 pytest 测试"""

    @pytest.mark.parametrize("value", ['redis', 'mysql', 'mssql'])
    def test_has_with_existing_string_value(self, value):
        """测试 has 方法：存在的字符串值"""
        assert DB_TYPE.has(value) is True

    @pytest.mark.parametrize("value", ['oracle', 'postgresql', ''])
    def test_has_with_non_existing_string_value(self, value):
        """测试 has 方法：不存在的字符串值"""
        assert DB_TYPE.has(value) is False

    @pytest.mark.parametrize("value", [1, 0])
    def test_has_with_integer_values(self, value):
        """测试 has 方法：整数值（对于字符串枚举应该返回 False）"""
        assert DB_TYPE.has(value) is False

    def test_names_method(self):
        """测试 names 方法：返回所有枚举成员名称"""
        expected_names = ['REDIS', 'MYSQL', 'MSSQL']
        assert DB_TYPE.names() == expected_names

    def test_values_method(self):
        """测试 values 方法：返回所有枚举成员值"""
        expected_values = ['redis', 'mysql', 'mssql']
        assert DB_TYPE.values() == expected_values

    @pytest.mark.parametrize(
        "input_val,expected_enum",
        [
            ('redis', DB_TYPE.REDIS),
            ('mysql', DB_TYPE.MYSQL),
            ('mssql', DB_TYPE.MSSQL),
        ]
    )
    def test_create_with_existing_value(self, input_val, expected_enum):
        """测试 create 方法：使用存在的值创建枚举实例"""
        instance = DB_TYPE.create(input_val)
        assert instance == expected_enum
        assert isinstance(instance, DB_TYPE)

    @pytest.mark.parametrize("invalid_value", ['oracle', '', 1])
    def test_create_with_invalid_values_raises_error(self, invalid_value):
        """测试 create 方法：无效值应当抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            DB_TYPE.create(invalid_value)
        # 统一检查是否包含标准错误信息
        assert f"{invalid_value} is not a valid DB_TYPE" in str(exc_info.value)

# 创建一个包含整数值的枚举用于测试
class NUMBER_TYPE(YiEnum):
    """数字类型枚举"""
    ONE = 1
    TWO = 2
    THREE = 3


class TestYiEnumWithIntegerValues:
    """测试包含整数值的 YiEnum"""

    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_has_with_existing_integer_value(self, value):
        """测试 has 方法：存在的整数值"""
        assert NUMBER_TYPE.has(value) is True

    @pytest.mark.parametrize("value", [0, 4])
    def test_has_with_non_existing_integer_value(self, value):
        """测试 has 方法：不存在的整数值"""
        assert NUMBER_TYPE.has(value) is False

    def test_create_with_existing_integer_value(self):
        """测试 create 方法：使用存在的整数值创建枚举实例"""
        instance = NUMBER_TYPE.create(1)
        assert instance == NUMBER_TYPE.ONE
        assert isinstance(instance, NUMBER_TYPE)