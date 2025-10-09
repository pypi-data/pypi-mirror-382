import os
import json
import yaml
from typing import Dict, Any, Optional

from intelliw.utils.logger import _get_framework_logger


from .base import ConfigManager
logger = _get_framework_logger()


class ModelManagerConfig(ConfigManager):
    def __init__(self):
        # 初始化配置字典
        modelfiles_by_modelid_url = f'{os.environ.get("domain.url")}/{os.getenv("YMS_CONSOLE_APP_CODE")}/self/rest/api/trainingInstanceModelFiles'
        self._config = {
            'MODELFILES_BY_MODELID_URL': os.environ.get('MODELFILES_BY_MODELID_URL', modelfiles_by_modelid_url),
            'MODEL_UPDATE_INTERVAL': int(os.environ.get('MODEL_UPDATE_INTERVAL', '300')),  # 默认5分钟
            'REQUEST_TIMEOUT': int(os.environ.get('REQUEST_TIMEOUT', '10')),  # 默认10秒
            'TRAININGASSIGNMENT_MODEL_ID': os.environ.get('TRAININGASSIGNMENT_MODEL_ID'),
            'MODEL_LOAD_TIMEOUT': int(os.environ.get('MODEL_LOAD_TIMEOUT', '30')),
            'MODEL_UPDATE_TIMEOUT': int(os.environ.get('MODEL_UPDATE_TIMEOUT', '30')),
            'CURRENT_MODEL_VERSION': None,
            'CURRENT_MODEL_MODIFIED_DATE': None,
            'HOT_RELOAD_MODE': os.environ.get('HOT_RELOAD_MODE', 'false').lower() == 'true',
        }

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置

        :param config_path: 配置文件路径
        :return: 配置字典
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.endswith('.json'):
                        file_config = json.load(f)
                    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        file_config = yaml.safe_load(f)
                    else:
                        raise ValueError(f"Unsupported config file format: {config_path}")

                # 更新配置
                for key, value in file_config.items():
                    self._config[key] = value

                logger.info(f"Config loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {str(e)}")

        # 从环境变量更新配置
        for key in self._config:
            if key in os.environ:
                # 尝试转换类型
                try:
                    current_value = self._config[key]
                    logger.info(f"Updating config {key} from environment variable, old value: {current_value}")
                    if isinstance(current_value, int):
                        self._config[key] = int(os.environ[key])
                    elif isinstance(current_value, float):
                        self._config[key] = float(os.environ[key])
                    elif isinstance(current_value, bool):
                        self._config[key] = os.environ[key].lower() == 'true'
                    else:
                        self._config[key] = os.environ[key]
                except ValueError as e:
                    logger.warning(f"Failed to convert environment variable {key} to appropriate type: {str(e)}")
                    self._config[key] = os.environ[key]

        return self._config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        :param key: 配置键
        :param default: 默认值
        :return: 配置值
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        :param key: 配置键
        :param value: 配置值
        """
        self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        :return: 配置字典
        """
        return self._config.copy()


# # 创建配置实例
# config = ModelManagerConfig()
# # 加载配置
# config.load_config()