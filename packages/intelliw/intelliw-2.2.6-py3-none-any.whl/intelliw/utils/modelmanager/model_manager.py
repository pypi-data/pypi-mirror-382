import os
import time
import threading
from typing import Any, Optional, Dict

# 导入基础类和单例装饰器
from .base import BaseModelManager
from .singleton import singleton
from .model_loader import APIModelLoader
from .decorators import validate_model, model_update_notification
from .config import ModelManagerConfig

from intelliw.utils.logger import _get_framework_logger

# 配置日志
logger = _get_framework_logger()

@singleton
class ModelManager(BaseModelManager):
    def __init__(self, initial_model_local_path, load_func):
        """初始化模型管理器"""
        logger.info('Initializing ModelManager...')
        self.load_func = load_func
        self.running = False
        self.update_thread = None
        self.model_lock = threading.RLock()

        # 初始化配置管理器
        self.config_manager = ModelManagerConfig()
        self.update_interval = self.config_manager.get('MODEL_UPDATE_INTERVAL')
        self.model_id = self.config_manager.get('TRAININGASSIGNMENT_MODEL_ID')
        self.modelfiles_by_modelid_url = self.config_manager.get('MODELFILES_BY_MODELID_URL')
        self.hot_reload_mode = self.config_manager.get('HOT_RELOAD_MODE')
        
        # 双缓冲模型存储优化：使用list[2]数组和curindex
        self.model_buffer = [None, None]  # 存储两个模型的缓冲区
        self.curindex = 0  # 当前活跃模型的索引
        # 初始化模型存储路径
        self.inited_model_local_path = initial_model_local_path
        self.model_version = None
        self.model_path = None
        self.model_modified_date = None

        logger.info(f'Using TRAINING  MODEL ID: {self.model_id}')

        # 初始化模型加载器
        self.model_loader = APIModelLoader(self.config_manager, load_func=self.load_func)

        # 初始加载模型
        self._initial_load_model()

        # 启动定时更新任务
        if self.hot_reload_mode:
            self._start_update_task()

    def _initial_load_model(self):
        """初始加载模型"""
        try:
            logger.info('Initial loading model...')

            # 配置初始模型版本
            model_path = self.inited_model_local_path
            version = os.environ.get('MODEL_VERSION', 0)
            model_modified_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 加载模型
            model_data = self._load_local_model(model_path)
            if model_data:
                with self.model_lock:
                    self.model_buffer[self.curindex] = model_data
                    self.model_version = version
                    self.config_manager.set('CURRENT_MODEL_VERSION', version)
                    self.config_manager.set('CURRENT_MODEL_MODIFIED_DATE', model_modified_date)
                logger.info(f'Successfully loaded initial model version: {version}, modified_date: {model_modified_date}')
                # 上报状态
                self._report_status('loaded')
            else:
                logger.error('Failed to download initial model')
        except Exception as e:
            logger.error(f'Error during initial model loading: {str(e)}', exc_info=True)

    def _load_new_model(self, model_path: str, version: str, modified_date: str) -> bool:
        """加载新模型到备用缓冲区"""
        try:
            model_data = self._download_and_prepare_model(model_path, version)
            if not model_data:
                return False

            with self.model_lock:
                # 计算缓冲区索引
                old_index = self.curindex
                new_index = (self.curindex + 1) % 2
                # 加载到备用缓冲区
                self.model_buffer[new_index] = model_data
                # 切换缓冲区索引
                self.curindex = new_index
                self.model_version = version
                self.model_modified_date = modified_date
                self.config_manager.set('CURRENT_MODEL_VERSION', version)
                self.config_manager.set('CURRENT_MODEL_MODIFIED_DATE', modified_date)
                time.sleep(5)
                # 释放旧模型内存
                self.model_buffer[old_index] = None
            logger.info(f'Successfully updated to model version: {version}')
            # 上报状态
            self._report_status('updated')
            return True
        except Exception as e:
            logger.error(f'Error loading new model: {str(e)}', exc_info=True)
            return False

    def get_active_model(self) -> Optional[Any]:
        """获取当前活跃模型"""
        # with self.model_lock:
        return self.model_buffer[self.curindex]

    @validate_model
    def _download_and_prepare_model(self, model_path: str, version: str) -> Optional[Any]:
        """下载并准备模型"""
        model_data = self.model_loader.load(model_path, version)
        if model_data:
            # 返回模型
            return model_data
        return None

    @validate_model
    def _load_local_model(self, local_model_path: str) -> Optional[Any]:
        """加载本地模型"""
        model_data = self.model_loader.load_model(local_model_path)
        if model_data:
            # 返回模型
            return model_data
        return None

    def _report_status(self, status: str) -> None:
        """向AI工作坊上报状态变更"""
        try:
            logger.info(f'Reporting status: {status}')
            # 使用本地定义的装饰器替代缺失的al_decorator模块
            from .decorators import train_info_report

            @train_info_report
            def report_status_impl(model_id, version, status):
                # 实际的上报逻辑
                return True

            report_status_impl(self.model_id, self.model_version, status)
            logger.info('Status reported successfully')
        except Exception as e:
            logger.error(f'Error reporting status: {str(e)}', exc_info=True)

    @model_update_notification
    def _check_for_updates(self):
        """检查模型更新"""
        try:
            logger.info('Checking for model updates...')
            update_info = self.model_loader.check_for_updates()

            # 检查是否有更新
            if update_info:
                logger.info(f'New model version available: {update_info["version"]}, last modified: {update_info["modified_date"]}')
                model_path = update_info['path']
                self._load_new_model(model_path, update_info['version'], update_info["modified_date"])
                return update_info
            else:
                logger.info(f'No new updates. Current version: {self.model_version}, modified_date: {self.model_modified_date}')
                return None
        except Exception as e:
            logger.error(f'Error checking for updates: {str(e)}', exc_info=True)
            return None



    def _update_task(self):
        """定时更新任务"""
        while self.running:
            self._check_for_updates()
            # 等待指定间隔
            for _ in range(self.update_interval):
                if not self.running:
                    break
                time.sleep(1)

    def _start_update_task(self):
        """启动定时更新任务"""
        if self.running:
            logger.warning('Update task is already running')
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._update_task, daemon=True)
        self.update_thread.start()
        logger.info('Update task started')

    def get_model_version(self) -> str:
        """获取当前模型版本"""
        return self.model_version

    def get_model(self):
        return self.get_active_model()

    def load_model(self, model_path: str, version: str) -> bool:
        """加载指定路径的模型"""
        return self._load_new_model(model_path, version)

    def check_for_updates(self) -> bool:
        """检查模型更新"""
        update_info = self._check_for_updates()
        return update_info is not None

    def start(self) -> None:
        """启动模型管理器"""
        self._start_update_task()

    def stop(self):
        """停止模型管理器"""
        logger.info('Stopping ModelManager...')
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        logger.info('ModelManager stopped')

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        for key, value in config.items():
            self.config_manager.set(key, value)

        # 更新相关属性
        self.update_interval = self.config_manager.get('MODEL_UPDATE_INTERVAL')
        self.model_id = self.config_manager.get('TRAININGASSIGNMENT_MODEL_ID')

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config_manager.to_dict()


# 单例模式
_model_manager_instance = None

def get_model_manager(initial_model_local_path, load_func) -> ModelManager:
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager(initial_model_local_path, load_func)
    return _model_manager_instance


# 确保在导入时就创建实例
# model_manager = get_model_manager()

# if __name__ == '__main__':
#     # 测试代码
#     model_manager = get_model_manager()
#     try:
#         # 保持程序运行一段时间以观察效果
#         for _ in range(60):
#             print(f'Current model version: {model_manager.get_model_version()}')
#             time.sleep(1)
#     finally:
#         model_manager.stop()