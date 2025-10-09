from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseModelManager(ABC):
    """
    模型管理器基础抽象类
    定义模型管理器的核心接口
    """

    @abstractmethod
    def get_model_version(self) -> str:
        """获取当前模型版本"""
        pass

    @abstractmethod
    def get_active_model(self) -> Any:
        """获取当前激活的模型"""
        pass

    @abstractmethod
    def load_model(self, model_path: str, version: str) -> bool:
        """
        加载指定路径的模型

        :param model_path: 模型路径
        :param version: 模型版本
        :return: 是否加载成功
        """
        pass

    @abstractmethod
    def check_for_updates(self) -> bool:
        """
        检查模型更新

        :return: 是否有更新
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """启动模型管理器"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """停止模型管理器"""
        pass

    @abstractmethod
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        设置配置

        :param config: 配置字典
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        pass


class ModelLoader(ABC):
    """
    模型加载器基础抽象类
    定义不同类型模型的加载接口
    """

    @abstractmethod
    def load(self, model_path: str, load_func) -> Any:
        """
        加载模型

        :param model_path: 模型路径
        :return: 加载的模型
        """
        pass

    @abstractmethod
    def validate(self, model: Any) -> bool:
        """
        验证模型有效性

        :param model: 模型对象
        :return: 是否有效
        """
        pass


class ConfigManager(ABC):
    """
    配置管理器基础抽象类
    """

    @abstractmethod
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置

        :param config_path: 配置文件路径
        :return: 配置字典
        """
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        :param key: 配置键
        :param default: 默认值
        :return: 配置值
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        :param key: 配置键
        :param value: 配置值
        """
        pass