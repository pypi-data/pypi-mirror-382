import os
import time
import threading
import unittest
from unittest.mock import patch, MagicMock, Mock
import tempfile
import json

# 导入重构后的模型管理器和相关模块
from .model_manager import get_model_manager, ModelManager
from .model_loader import APIModelLoader
from .config import ConfigManager, ModelManagerConfig


class TestModelManager(unittest.TestCase):
    def setUp(self):
        # 保存原始环境变量
        self.original_env = os.environ.copy()
        # 设置测试环境变量
        os.environ['MODEL_ID'] = 'test_model'
        os.environ['MODEL_UPDATE_INTERVAL'] = '10'
        os.environ['CONSOLE_API_URL'] = 'http://test-console-api.com'
        os.environ['OSS_API_URL'] = 'http://test-oss-api.com'
        os.environ['MODEL_LOAD_TIMEOUT'] = '5'

        # 创建临时配置文件用于测试
        self.temp_config_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = os.path.join(self.temp_config_dir.name, 'test_config.json')
        with open(self.temp_config_path, 'w') as f:
            json.dump({
                'MODEL_ID': 'test_model_from_file',
                'MODEL_UPDATE_INTERVAL': 5
            }, f)

        # 重置模型管理器单例实例
        from .model_manager import _model_manager_instance
        _model_manager_instance = None

        # 保存原始的单例装饰器
        from intelliw.utils.modelmanager.singleton import singleton
        self.original_singleton = singleton

        # 定义一个临时的非单例装饰器
        def non_singleton(cls):
            return cls

        # 替换单例装饰器
        import intelliw.utils.modelmanager.singleton
        intelliw.utils.modelmanager.singleton.singleton = non_singleton

        # 重新加载ModelManager模块以应用新的装饰器
        import importlib
        import intelliw.utils.modelmanager.model_manager
        importlib.reload(intelliw.utils.modelmanager.model_manager)

        global ModelManager, get_model_manager
        from intelliw.utils.modelmanager.model_manager import ModelManager, get_model_manager

        # 模拟配置管理器，使用ModelManagerConfig作为spec因为它实现了to_dict方法
        self.mock_config_manager = Mock(spec=ModelManagerConfig)
        self.mock_config_manager.get.side_effect = lambda key: {
            'TRAININGASSIGNMENT_MODEL_ID': 'test_model',
            'MODEL_UPDATE_INTERVAL': 10,
            'MODELFILES_BY_MODELID_URL': 'http://test-console-api.com',
            'MODEL_LOAD_TIMEOUT': 5,
            'REQUEST_TIMEOUT': 10,
            'MODEL_UPDATE_TIMEOUT': 10,
            'CURRENT_MODEL_VERSION': None
        }.get(key)
        self.mock_config_manager.to_dict.return_value = {
            'TRAININGASSIGNMENT_MODEL_ID': 'test_model',
            'MODEL_UPDATE_INTERVAL': 10,
            'CONSOLE_API_URL': 'http://test-console-api.com',
            'OSS_API_URL': 'http://test-oss-api.com',
            'MODEL_LOAD_TIMEOUT': 5
        }

        # 模拟模型加载器
        self.mock_model_loader = Mock(spec=APIModelLoader)
        self.model_data = {'weights': [1.0, 2.0, 3.0], 'biases': [0.1, 0.2]}
        self.mock_model_loader.check_for_updates.return_value = {
            'path': 'test_model_path',
            'version': 'v1.0'
        }
        self.mock_model_loader.load.return_value = self.model_data

    def tearDown(self):
        # 恢复原始环境变量
        os.environ.clear()
        os.environ.update(self.original_env)

        # 清理临时目录
        self.temp_config_dir.cleanup()

        # 恢复原始的单例装饰器
        import intelliw.utils.modelmanager.singleton
        intelliw.utils.modelmanager.singleton.singleton = self.original_singleton

        # 重新加载ModelManager模块以应用原始装饰器
        import importlib
        import intelliw.utils.modelmanager.model_manager
        importlib.reload(intelliw.utils.modelmanager.model_manager)
        # 停止模型管理器
        try:
            model_manager = get_model_manager()
            model_manager.stop()
        except:
            pass

    def test_singleton(self):
        """测试单例模式"""
        manager1 = get_model_manager(None)
        manager2 = get_model_manager(None)
        self.assertIs(manager1, manager2)

    def test_initial_load_model(self):
        """测试初始加载模型"""
        # 创建模拟配置管理器
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key: {
            'TRAININGASSIGNMENT_MODEL_ID': 'test_model',
            'MODEL_UPDATE_INTERVAL': 10
        }.get(key)

        # 创建模拟模型加载器
        mock_model_loader = MagicMock()

        # 模拟check_for_updates返回有效的更新信息
        update_info = {
            'path': 'test_model_path',
            'version': 'v1.0'
        }
        mock_model_loader.check_for_updates.return_value = update_info

        # 模拟load返回原始数据
        raw_model_data = {'test': 'model'}
        mock_model_loader.load.return_value = raw_model_data

        # 直接创建ModelManager实例，绕过单例和构造函数
        model_manager = object.__new__(ModelManager)

        # 手动设置实例属性
        model_manager.model_buffer = [None, None]
        model_manager.curindex = 0
        model_manager.model_version = None
        model_manager.model_lock = threading.RLock()
        model_manager.running = False
        model_manager.update_thread = None
        model_manager.config_manager = mock_config
        model_manager.update_interval = 10
        model_manager.model_id = 'test_model'
        model_manager.model_loader = mock_model_loader

        # 只调用_initial_load_model进行测试
        model_manager._initial_load_model()

        # 验证模型加载器方法被正确调用
        mock_model_loader.check_for_updates.assert_called_once()
        mock_model_loader.load.assert_called_once_with(update_info['path'])

        # 验证模型版本和数据
        self.assertEqual(model_manager.get_model_version(), 'v1.0')
        
        # 验证模型数据经过了prepare_model_params处理
        from intelliw.utils.modelmanager.utils import prepare_model_params
        processed_data = prepare_model_params(raw_model_data)
        self.assertEqual(model_manager.get_active_model(), processed_data)

        # 单独测试_start_update_task
        model_manager._start_update_task()
        self.assertTrue(model_manager.running)
        self.assertIsNotNone(model_manager.update_thread)
        self.assertTrue(model_manager.update_thread.is_alive())

    def test_check_for_updates_no_update(self):
        """测试检查更新（无更新）"""
        # 配置mock返回值
        self.mock_model_loader.check_for_updates.return_value = {
            'path': 'test_model_path',
            'version': 'v1.0'
        }

        # 初始化模型管理器
        model_manager = get_model_manager(None)
        model_manager.model_version = 'v1.0'  # 手动设置当前版本
        model_manager.model_loader = self.mock_model_loader

        # 调用检查更新方法
        result = model_manager._check_for_updates()

        # 验证没有更新
        self.assertEqual(model_manager.get_model_version(), 'v1.0')
        self.assertIsNone(result)

    def test_check_for_updates_with_update(self):
        """测试检查更新（有更新）"""
        # 配置mock返回值
        self.mock_model_loader.check_for_updates.return_value = {
            'path': 'new_model_path',
            'version': 'v2.0'
        }
        new_model_data = {'weights': [4.0, 5.0, 6.0], 'biases': [0.3, 0.4]}
        self.mock_model_loader.load.return_value = new_model_data

        # 初始化模型管理器
        model_manager = get_model_manager(None)
        model_manager.model_version = 'v1.0'  # 手动设置当前版本
        model_manager.model_buffer = [{'old': 'model'}, None]
        model_manager.curindex = 0
        model_manager.model_loader = self.mock_model_loader

        # 调用检查更新方法
        result = model_manager._check_for_updates()

        # 验证更新成功
        self.assertEqual(model_manager.get_model_version(), 'v2.0')
        self.assertEqual(model_manager.get_active_model(), new_model_data)
        self.assertEqual(result['version'], 'v2.0')

    def test_stop(self):
        """测试停止模型管理器"""
        # 创建一个ModelManager实例
        model_manager = ModelManager(None)
        model_manager.model_loader = self.mock_model_loader
        model_manager.config_manager = self.mock_config_manager
        
        # 启动更新任务
        model_manager._start_update_task()
        
        # 确保线程已启动
        time.sleep(0.1)
        
        # 停止模型管理器
        model_manager.stop()
        
        # 等待线程结束
        if model_manager.update_thread:
            model_manager.update_thread.join(timeout=5)  # 设置超时以避免无限等待
        
        # 验证线程已停止
        self.assertFalse(model_manager.running)
        if model_manager.update_thread:
            self.assertFalse(model_manager.update_thread.is_alive())

    def test_config_management(self):
        """测试配置管理功能"""
        model_manager = get_model_manager(None)
        model_manager.config_manager = self.mock_config_manager

        # 测试获取配置
        self.assertEqual(model_manager.get_config()['TRAININGASSIGNMENT_MODEL_ID'], 'test_model')
        self.assertEqual(model_manager.get_config()['MODEL_UPDATE_INTERVAL'], 10)

        # 测试设置配置
        model_manager.set_config({
            'TRAININGASSIGNMENT_MODEL_ID': 'new_test_model',
            'MODEL_UPDATE_INTERVAL': 30
        })

        # 验证配置更新
        self.mock_config_manager.set.assert_any_call('TRAININGASSIGNMENT_MODEL_ID', 'new_test_model')
        self.mock_config_manager.set.assert_any_call('MODEL_UPDATE_INTERVAL', 30)

    def test_get_model_manager_function(self):
        """测试get_model_manager函数"""
        manager = get_model_manager(None)
        self.assertIsInstance(manager, ModelManager)


if __name__ == '__main__':
    unittest.main()