import os
import time
import requests
import threading
from typing import Any, Optional, Dict
import zipfile
import shutil

from .base import ModelLoader
from intelliw.utils.iuap_request import get as request_get
from intelliw.utils.iuap_request import get_modelfiles_by_modelid
from intelliw.utils.logger import _get_framework_logger
from intelliw.utils.storage_service import StorageService
logger = _get_framework_logger()

class APIModelLoader(ModelLoader):
    """
    从API加载模型的加载器
    """

    def __init__(self, config_manager: 'ConfigManager', load_func):
        """
        初始化API模型加载器

        :param config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self._lock = threading.RLock()
        self._last_checked = 0
        self.load_func = load_func
        self.model_tmp_dir = "./model_tmp"
        os.makedirs(self.model_tmp_dir, exist_ok=True)

    def parse_latest_modelfile_info(self, resp_json):
        if resp_json is None:
            return None
        # todo
        resp_data = resp_json.get("data", {})
        resp_content = resp_data.get("content", [])
        if len(resp_content) > 0:
            modelfile_info = {}
            modelfile_info['version'] = resp_content[0].get("instanceVersion")
            modelfile_info['path'] = resp_content[0].get("modelPath")
            modelfile_info['lastModifiedDate'] = resp_content[0].get("lastModifiedDate", 0)
            return modelfile_info
        return None

    def load(self, model_path: str, version: str) -> Any:
        """
        从API加载模型

        :param model_path: 模型路径
        :return: 加载的模型
        """
        try:

            logger.info(f"Download model from {model_path}")
            local_download_path=f'{self.model_tmp_dir}/tmp_model_v_{version}_{int(time.time() * 1e6)}'
            downloader = StorageService(
                model_path, "download")
            downloader.download(local_download_path, stream=True)
            
            if not os.path.exists(local_download_path):
                raise Exception(f"Failed to download model from {model_path}, version: {version}")

            logger.info(f"Successfully loaded model: {model_path}, version: {version}")
            #  加载模型

            target_model_path = local_download_path
            if zipfile.is_zipfile(local_download_path):
                # 创建临时目录来解压ZIP文件
                extract_dir = local_download_path + "_extracted"
                os.makedirs(extract_dir, exist_ok=True)
                
                # 解压ZIP文件到临时目录
                with zipfile.ZipFile(local_download_path) as zip_file:
                    zip_file.extractall(extract_dir)
                
                target_model_path = extract_dir
            
            model = self.load_model(target_model_path)
            if not model:
                logger.error(f"Failed to load model: {model_path}, version: {version}")
            logger.info(f"Successfully validated model: {model_path}, version: {version}")
            try:
                # 如果存在解压目录，删除它  
                if 'extract_dir' in locals() and os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                    logger.info(f"Deleted temporary directory: {extract_dir}")
                
                # 删除下载的原始文件
                if os.path.exists(local_download_path):
                    if os.path.isfile(local_download_path):
                        os.remove(local_download_path)
                    elif os.path.isdir(local_download_path):
                        shutil.rmtree(local_download_path)
                    logger.info(f"Deleted temporary file: {local_download_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary files: {str(e)}")
            return model

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def load_model(self, model_path: str) -> Any:
        """
        加载模型

        :param model_path: 模型路径
        :return: 加载的模型
        """
        try:
            model = self.load_func(model_path)
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None

    def validate(self, model: Any) -> bool:
        """
        验证模型有效性

        :param model: 模型对象
        :return: 是否有效
        """
        if not model:
            return False

        return True

    def check_for_updates(self) -> Optional[Dict[str, str]]:
        """
        检查模型更新

        :return: 包含新模型路径和版本的字典，如果没有更新则返回None
        """
        try:
            # 检查时间间隔
            update_interval = self.config_manager.get('MODEL_UPDATE_INTERVAL', 300)
            current_time = time.time()

            # 如果距离上次检查时间不足更新间隔，则跳过
            with self._lock:
                if current_time - self._last_checked < update_interval:
                    return None
                self._last_checked = current_time

            
            # 请求接口
            url = self.config_manager.get('MODELFILES_BY_MODELID_URL')
            model_id = self.config_manager.get('TRAININGASSIGNMENT_MODEL_ID')
            # 设置超时
            timeout = self.config_manager.get('MODEL_UPDATE_TIMEOUT', 30)
            resp_json = get_modelfiles_by_modelid(url, model_id, timeout)
            # 解析接口， 获取最新的模型文件信息
            latest_modelfile_info = self.parse_latest_modelfile_info(resp_json)
            if not latest_modelfile_info:
                logger.info(f"No models found in update response, response: {resp_json}")
                return None
            
            logger.info(f"latest_modelfile_info: {latest_modelfile_info}")

            current_version = self.config_manager.get('CURRENT_MODEL_VERSION')
            current_modified_date = self.config_manager.get('CURRENT_MODEL_MODIFIED_DATE')

            # 如果没有当前版本或者版本不同, 版本相同但修改时间更新，则认为有更新
            if not current_version \
                or latest_modelfile_info['version'] != current_version \
                or latest_modelfile_info['lastModifiedDate'] > current_modified_date:
                logger.info(f"Found new model version: {latest_modelfile_info['version']}, new modified date: {latest_modelfile_info['lastModifiedDate']}")
                return {
                    'path': latest_modelfile_info['path'],
                    'version': latest_modelfile_info['version'],
                    "modified_date": latest_modelfile_info['lastModifiedDate'],
                }

            logger.info("No new model updates available")
            return None

        except Exception as e:
            logger.error(f"Error checking for model updates: {str(e)}")
            return None