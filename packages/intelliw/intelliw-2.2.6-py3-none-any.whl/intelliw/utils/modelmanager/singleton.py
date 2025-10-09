import threading
from typing import Type, Any, Dict


def singleton(cls: Type) -> Type:
    """
    单例模式装饰器
    确保被装饰的类只有一个实例
    """
    instances: Dict[Type, Any] = {}
    lock = threading.RLock()  # 使用可重入锁

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance