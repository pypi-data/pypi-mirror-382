class ClassUtils:
    """类工具类"""
    
    
    @staticmethod
    def create(cls: type, *args, **kwargs) -> object:
        """创建类的实例"""
        return cls(*args, **kwargs)

    @staticmethod
    def name(obj: object) -> str:
        """获取类名"""
        return obj.__class__.__name__
    
    @staticmethod
    def properties(obj: object) -> list:
        """获取类的所有属性"""
        return [prop for prop in dir(obj) if not prop.startswith("_") and not callable(getattr(obj, prop))]
    
    @staticmethod
    def methods(obj: object) -> list:
        """获取类的所有方法"""
        return [method for method in dir(obj) if not method.startswith("_") and callable(getattr(obj, method))]
    
    @staticmethod
    def has_property(obj: object, property_name: str) -> bool:
        """检查类是否有某个属性"""
        return hasattr(obj, property_name) and not callable(getattr(obj, property_name))
    
    @staticmethod
    def has_method(obj: object, method_name: str) -> bool:
        """检查类是否有某个方法"""
        return hasattr(obj, method_name) and callable(getattr(obj, method_name))

    @staticmethod
    def eval_property(obj: object, property_name: str) -> any:
        """获取类的属性值"""
        if hasattr(obj, property_name):
            return getattr(obj, property_name)
        raise AttributeError(f"{property_name} is not a property of {obj.__class__.__name__}")
    
    @staticmethod
    def eval_method(obj: object, method_name: str, *args, **kwargs) -> any:
        """调用类的方法"""
        method = getattr(obj, method_name)
        if callable(method):
            return method(*args, **kwargs)
        raise AttributeError(f"{method_name} is not a callable method of {obj.__class__.__name__}")
