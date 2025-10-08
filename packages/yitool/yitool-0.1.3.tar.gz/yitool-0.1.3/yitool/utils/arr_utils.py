from functools import reduce


class ArrUtils(object):
    """数组工具类"""

    @staticmethod
    def is_empty(arr: list) -> bool:
        """判断数组是否为空"""
        return arr is None or len(arr) == 0

    @staticmethod
    def safe(arr: list) -> list:
        """安全获取数组，避免 None，返回空数组"""
        return arr or []

    @staticmethod
    def unique(arr: list) -> list:
        """获取数组的唯一值列表，保持原有顺序"""
        if ArrUtils.is_empty(arr):
            return []
        return list(dict.fromkeys(arr))

    @staticmethod
    def flatten(arr: list) -> list:
        """将嵌套数组展开为一维数组"""
        if ArrUtils.is_empty(arr):
            return []
        flat_list = []
        for item in arr:
            if isinstance(item, list):
                flat_list.extend(ArrUtils.flatten(item))
            else:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def chunk(arr: list, size: int) -> list:
        """将数组分割为指定大小的块"""
        if ArrUtils.is_empty(arr) or size <= 0:
            return []
        return [arr[i:i + size] for i in range(0, len(arr), size)]

    @staticmethod
    def intersection(arr1: list, arr2: list) -> list:
        """获取两个数组的交集"""
        if ArrUtils.is_empty(arr1) or ArrUtils.is_empty(arr2):
            return []
        set2 = set(arr2)
        return list(set(item for item in arr1 if item in set2))

    @staticmethod
    def difference(arr1: list, arr2: list) -> list:
        """获取两个数组的差集"""
        if ArrUtils.is_empty(arr1):
            return []
        if ArrUtils.is_empty(arr2):
            return arr1
        set2 = set(arr2)
        return [item for item in arr1 if item not in set2]

    @staticmethod
    def union(arr1: list, arr2: list) -> list:
        """获取两个数组的并集"""
        return ArrUtils.unique((arr1 or []) + (arr2 or []))

    @staticmethod
    def contains(arr: list, item) -> bool:
        """判断数组是否包含指定元素"""
        if ArrUtils.is_empty(arr):
            return False
        return item in arr

    @staticmethod
    def index_of(arr: list, item) -> int:
        """获取元素在数组中的索引，未找到返回 -1"""
        if ArrUtils.is_empty(arr):
            return -1
        try:
            return arr.index(item)
        except ValueError:
            return -1

    @staticmethod
    def last_index_of(arr: list, item) -> int:
        """获取元素在数组中的最后一个索引，未找到返回 -1"""
        if ArrUtils.is_empty(arr):
            return -1
        for i in range(len(arr) - 1, -1, -1):
            if arr[i] == item:
                return i
        return -1

    @staticmethod
    def reverse(arr: list) -> list:
        """反转数组"""
        if ArrUtils.is_empty(arr):
            return []
        return list(reversed(arr))

    @staticmethod
    def sort(arr: list, reverse: bool = False) -> list:
        """对数组进行排序"""
        if ArrUtils.is_empty(arr):
            return []
        try:
            return sorted(arr, reverse=reverse)
        except Exception:
            raise ValueError("Array contains non-comparable elements, cannot sort.")

    @staticmethod
    def filter(arr: list, func: callable) -> list:
        """使用指定函数过滤数组"""
        if ArrUtils.is_empty(arr):
            return []
        return list(filter(func, arr))

    @staticmethod
    def map(arr: list, func: callable) -> list:
        """使用指定函数映射数组"""
        if ArrUtils.is_empty(arr):
            return []
        return list(map(func, arr))

    @staticmethod
    def reduce(arr: list, func: callable, initial=None):
        """使用指定函数归约数组"""
        if ArrUtils.is_empty(arr):
            return initial
        if initial is not None:
            return reduce(func, arr, initial)
        return reduce(func, arr)

    @staticmethod
    def join(arr: list, delimiter: str = ',') -> str:
        """将数组元素连接为字符串，使用指定的分隔符"""
        if ArrUtils.is_empty(arr):
            return ''
        return delimiter.join(str(item) for item in arr)