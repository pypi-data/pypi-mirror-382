import os
import time
import json
from functools import wraps
import logging
import zipfile
from typing import Any, Callable, Dict, Optional

from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


def model_cache(timeout: int = 3600):
    """
    模型缓存装饰器
    缓存模型加载结果，减少重复加载

    :param timeout: 缓存超时时间(秒)
    :return: 装饰器函数
    """
    cache = {}
    last_updated = 0

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_updated
            current_time = time.time()

            # 检查缓存是否过期
            if 'model' in cache and current_time - last_updated < timeout:
                logger.debug("Using cached model")
                return cache['model']

            # 加载新模型
            model = func(*args, **kwargs)

            # 更新缓存
            cache['model'] = model
            last_updated = current_time
            logger.debug("Model cache updated")

            return model

        return wrapper

    return decorator


def validate_model(func: Callable) -> Callable:
    """
    模型验证装饰器
    在加载模型后验证模型有效性

    :param func: 被装饰的函数
    :return: 装饰器函数
    """
    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        model = func(self, *args, **kwargs)

        # 验证模型
        # if hasattr(self, 'model_loader') and hasattr(self.model_loader, 'validate'):
        #     if not self.model_loader.validate(model):
        #         raise ValueError("Invalid model loaded")

        return model

    return wrapper


def model_update_notification(func: Callable) -> Callable:
    """
    模型更新通知装饰器
    当模型更新时发送通知

    :param func: 被装饰的函数
    :return: 装饰器函数
    """
    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        result = func(self, *args, **kwargs)

        # 如果有更新，发送通知
        if result and isinstance(result, dict) and 'version' in result:
            logger.info(f"Model updated to version: {result['version']}")
            # 这里可以添加通知逻辑，如发送消息到消息队列等

        return result

    return wrapper


def model_save(func):
    return func

def train_info_report(func):
    return func

def val_info_report(func):
    return func


def zip_model(model_path: str, output_path: str) -> bool:
    """
    压缩模型文件

    :param model_path: 模型文件路径
    :param output_path: 输出zip文件路径
    :return: 是否压缩成功
    """
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(model_path):
                for root, _, files in os.walk(model_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(model_path))
                        zipf.write(file_path, arcname)
            else:
                zipf.write(model_path, os.path.basename(model_path))
        logger.info(f"Model compressed to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error compressing model: {str(e)}")
        return False