#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: AI Assistant
Date: 2025-08-29
Description: 数据工厂物化表API接口封装
基于物化表接口文档.md的API规范实现
FilePath: /iw-algo-fx/intelliw/datasets/utils/iwfactory_dr_api.py
"""

import json
from typing import Dict, List, Any, Optional, Union
from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config

logger = _get_framework_logger()


class IwFactoryDrAPI:
    """数据工厂物化表API接口封装类"""
    
    def __init__(self, base_url: str = None, tenant_id: str = None, user_id: str = None, user_url_map: Dict[str, str] = None):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL，如果为None则使用config中的配置
            tenant_id: 租户ID，如果为None则使用config中的配置
            user_id: 用户ID
        """
        self.base_url = base_url or config.DATA_FACTORY_URL

        self.tenant_id = tenant_id or config.TENANT_ID
        self.user_id = user_id
        self.headers = {'service-code': 'iuap-aip-console'}
        
        # API端点映射
        self.endpoints = {
            'std_metadata': '/api/er-std-metadata',  # 表元数据规范
            'physics_table': '/api/er-physics-table',  # 物化建表
            'table_metadata': '/api/er-table-metadata',  # 查看表元数据
            'write_data': '/api/er-write-data',  # 数据批量写入
            'db_tables': '/api/er-db-tables',  # 获取数据源下表集合
            'db_table_columns': '/api/er-db-table-columns',  # 获取数据源下表-列集合
            'select_data': '/api/er-select-data',  # 批量查询数据
        }

        # 用户传入 url 优先使用用户传入的
        self.user_url_map = user_url_map if user_url_map and isinstance(user_url_map, dict) else {}
        if not self.base_url and not self.user_url_map:
            logger.warning('No base_url or user_url_map provided, using default url: %s', config.DATA_FACTORY_URL)

    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        统一的HTTP请求方法
        
        Args:
            method: HTTP方法 ('GET', 'POST')
            endpoint: API端点
            data: 请求数据
            headers: 请求头
            params: URL参数
            
        Returns:
            响应数据字典
        """

        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            url = endpoint 
        elif not self.user_url_map and endpoint in self.user_url_map:
            url = self.user_url_map[endpoint]
        else:
            url = f"{self.base_url}{endpoint}"
        
        # 设置默认请求头
        default_headers = self.headers.copy()
        if self.user_id:
            default_headers['user_id'] = self.user_id

        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = iuap_request.get(
                    url, params=params, headers=default_headers,
                    timeout=config.DATA_SOURCE_READ_TIMEOUT,
                    auth_type=iuap_request.AuthType.YHT
                )
            elif method.upper() == 'POST':
                response = iuap_request.post_json(
                    url, json=data, headers=default_headers,
                    timeout=config.DATA_SOURCE_READ_TIMEOUT,
                    auth_type=iuap_request.AuthType.YHT
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            response.raise_for_status()
            if response.status != 200:
                raise Exception(f"API请求失败，状态码: {response.status}, URL: {url}")
            
            result = response.json
            if result.get('code') != 0:
                raise Exception(f"API返回错误，code: {result.get('code')}, result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"API请求异常: {str(e)}")
            raise
    
    def std_metadata(self, datasource_id: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        表元数据规范API
        
        Args:
            datasource_id: 数据源ID
            columns: 字段列表，每个字段包含：
                - columnEnglishName: 字段英文名称
                - columnDescribe: 字段描述
                - columnType: 字段类型
                - columnLength: 字段长度
                - numericScale: 小数长度
                - columnNullFlag: 是否为空（1是空 0不是空）
                - columnKeyFlag: 是否主键（1是主键 0不是主键）
                
        Returns:
            规范后的字段元数据
        """
        data = {
            "ytenantId": self.tenant_id,
            "datasourceId": datasource_id,
            "columns": columns
        }

        if 'std_metadata' in self.user_url_map:
            endpoint = self.user_url_map['std_metadata']
        else:
            endpoint = self.endpoints['std_metadata']
        
        return self._make_request('POST', endpoint, data=data)
    
    def create_physics_table(self, datasource_id: str, project_name: str, 
                           table_name: str, description: str, 
                           columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        物化建表API
        
        Args:
            datasource_id: 数据源ID
            project_name: 项目英文名称
            table_name: 表名
            description: 表描述
            columns: 字段列表，格式同std_metadata
            
        Returns:
            包含logicTableId的响应数据
        """
        data = {
            "ytenantId": self.tenant_id,
            "projectName": project_name,
            "datasourceId": datasource_id,
            "table": {
                "tableName": table_name,
                "description": description
            },
            "columns": columns
        }

        if 'physics_table' in self.user_url_map:
            endpoint = self.user_url_map['physics_table']
        else:
            endpoint = self.endpoints['physics_table']
        
        return self._make_request('POST', endpoint, data=data)
    
    def get_table_metadata(self, logic_table_id: str) -> Dict[str, Any]:
        """
        查看表元数据API
        
        Args:
            logic_table_id: 逻辑模型ID
            
        Returns:
            表元数据信息
        """
        if 'table_metadata' in self.user_url_map:
            endpoint = self.user_url_map['table_metadata']
        else:
            endpoint = f"{self.endpoints['table_metadata']}/{self.tenant_id}/{logic_table_id}"

        return self._make_request('GET', endpoint)
    
    def write_data(self, datasource_id: str, table_name: str, 
                   column_schema: List[str], model_data: List[List[Any]],
                   logic_table_id: str = None) -> Dict[str, Any]:
        """
        数据批量写入API（支持任意数据源表）
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            column_schema: 字段名列表
            model_data: 数据值列表（二维数组）
            logic_table_id: 逻辑模型ID（可选，优先使用ER表）
            
        Returns:
            写入结果
        """
        data = {
            "ytenantId": self.tenant_id,
            "datasourceId": datasource_id,
            "dataModel": {
                "tableName": table_name,
                "columnSchema": column_schema,
                "modelData": model_data
            }
        }
        
        if logic_table_id:
            data["logicTableId"] = logic_table_id
        
        if 'write_data' in self.user_url_map:
            endpoint = self.user_url_map['write_data']
        else:
            endpoint = self.endpoints['write_data']
        
        return self._make_request('POST', endpoint, data=data)
    
    def get_db_tables(self, datasource_id: str) -> Dict[str, Any]:
        """
        获取数据源下表集合API
        
        Args:
            datasource_id: 数据源ID
            
        Returns:
            表列表
        """
        if 'db_tables' in self.user_url_map:
            endpoint = self.user_url_map['db_tables']
        else:
            endpoint = f"{self.endpoints['db_tables']}/{self.tenant_id}/{datasource_id}"

        return self._make_request('GET', endpoint)
    
    def get_db_table_columns(self, table_id: str) -> Dict[str, Any]:
        """
        获取数据源下表-列集合API
        
        Args:
            table_id: 表ID
            
        Returns:
            列列表
        """

        if 'db_table_columns' in self.user_url_map:
            endpoint = self.user_url_map['db_table_columns']
        else:
            endpoint = f"{self.endpoints['db_table_columns']}/{self.tenant_id}/{table_id}"
        return self._make_request('GET', endpoint)
    
    def select_data(self, datasource_id: str, table_name: str,
                   column_schema: List[str] = None, 
                   page: Dict[str, int] = None,
                   where_condition: List[Dict[str, Any]] = None,
                   where_relation: List[str] = None) -> Dict[str, Any]:
        """
        批量查询数据API
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            column_schema: 展示字段列表（可选，空数组表示获取所有字段）
            page: 分页条件，包含：
                - currentPage: 当前页，从1开始
                - pageSize: 页大小
                - totalCount: 总记录数（可选）
                - totalPage: 总页数（可选）
            where_condition: where条件列表，每个条件包含：
                - columnSchema: 字段名
                - columnValues: 值列表
                - operator: 操作符（=, <>, !=, <, <=, >, >=, like, not like, is null, is not null, in）
            where_relation: 关联关系列表（可选，支持and, or）
            
        Returns:
            查询结果，包含columnSchema和modelData
        """
        data = {
            "ytenantId": self.tenant_id,
            "logicTableId": "",  # 根据文档，空字符串表示任意数据源表
            "datasourceId": datasource_id,
            "dataModel": {
                "tableName": table_name,
                "columnSchema": column_schema or [],
                "page": page or {
                    "currentPage": 1,
                    "pageSize": 1000,
                    "totalCount": 0,
                    "totalPage": 0
                },
                "where": {
                    "condition": where_condition or [],
                    "relation": where_relation or []
                }
            }
        }

        if 'select_data' in self.user_url_map:
            endpoint = self.user_url_map['select_data']
        else:
            endpoint = self.endpoints['select_data']
        
        return self._make_request('POST', endpoint, data=data)
    
    def select_data_paginated(self, datasource_id: str, table_name: str,
                            column_schema: List[str] = None,
                            page_size: int = 1000,
                            current_page: int = 1,
                            where_condition: List[Dict[str, Any]] = None,
                            where_relation: List[str] = None) -> Dict[str, Any]:
        """
        分页查询数据的便捷方法
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            column_schema: 展示字段列表
            page_size: 每页大小
            current_page: 当前页码
            where_condition: where条件
            where_relation: 关联关系
            
        Returns:
            分页查询结果
        """
        page = {
            "currentPage": current_page,
            "pageSize": page_size,
            "totalCount": 0,
            "totalPage": 0
        }
        
        return self.select_data(
            datasource_id=datasource_id,
            table_name=table_name,
            column_schema=column_schema,
            page=page,
            where_condition=where_condition,
            where_relation=where_relation
        )
    
    def select_all_data(self, datasource_id: str, table_name: str,
                       column_schema: List[str] = None,
                       batch_size: int = 1000,
                       where_condition: List[Dict[str, Any]] = None,
                       where_relation: List[str] = None) -> List[List[Any]]:
        """
        获取所有数据的便捷方法（自动分页获取）
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            column_schema: 展示字段列表
            batch_size: 每批获取的数据量
            where_condition: where条件
            where_relation: 关联关系
            
        Returns:
            所有数据的二维数组
        """
        all_data = []
        current_page = 1
        
        while True:
            result = self.select_data_paginated(
                datasource_id=datasource_id,
                table_name=table_name,
                column_schema=column_schema,
                page_size=batch_size,
                current_page=current_page,
                where_condition=where_condition,
                where_relation=where_relation
            )
            
            data_model = result.get('data', {}).get('dataModel', {})
            model_data = data_model.get('modelData', [])
            
            if not model_data:
                break
                
            all_data.extend(model_data)
            
            # 检查是否还有更多数据
            page_info = data_model.get('page', {})
            total_page = page_info.get('totalPage', 1)
            if current_page >= total_page:
                break
                
            current_page += 1
        
        return all_data


# 全局API实例
_iwfactory_api = None


def get_iwfactory_api() -> IwFactoryDrAPI:
    """获取全局IwFactoryDrAPI实例"""
    global _iwfactory_api
    if _iwfactory_api is None:
        _iwfactory_api = IwFactoryDrAPI()
    return _iwfactory_api


def set_iwfactory_api_config(base_url: str = None, tenant_id: str = None, user_id: str = None):
    """设置全局API配置"""
    global _iwfactory_api
    _iwfactory_api = IwFactoryDrAPI(base_url, tenant_id, user_id)


# 便捷函数封装
def std_metadata(datasource_id: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """表元数据规范API的便捷函数"""
    return get_iwfactory_api().std_metadata(datasource_id, columns)


def create_physics_table(datasource_id: str, project_name: str, 
                        table_name: str, description: str, 
                        columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """物化建表API的便捷函数"""
    return get_iwfactory_api().create_physics_table(
        datasource_id, project_name, table_name, description, columns)


def get_table_metadata(logic_table_id: str) -> Dict[str, Any]:
    """查看表元数据API的便捷函数"""
    return get_iwfactory_api().get_table_metadata(logic_table_id)


def write_data(datasource_id: str, table_name: str, 
               column_schema: List[str], model_data: List[List[Any]],
               logic_table_id: str = None) -> Dict[str, Any]:
    """数据批量写入API的便捷函数"""
    return get_iwfactory_api().write_data(
        datasource_id, table_name, column_schema, model_data, logic_table_id)


def get_db_tables(datasource_id: str) -> Dict[str, Any]:
    """获取数据源下表集合API的便捷函数"""
    return get_iwfactory_api().get_db_tables(datasource_id)


def get_db_table_columns(table_id: str) -> Dict[str, Any]:
    """获取数据源下表-列集合API的便捷函数"""
    return get_iwfactory_api().get_db_table_columns(table_id)


def select_data(datasource_id: str, table_name: str,
               column_schema: List[str] = None, 
               page: Dict[str, int] = None,
               where_condition: List[Dict[str, Any]] = None,
               where_relation: List[str] = None) -> Dict[str, Any]:
    """批量查询数据API的便捷函数"""
    return get_iwfactory_api().select_data(
        datasource_id, table_name, column_schema, page, where_condition, where_relation)


def select_all_data(datasource_id: str, table_name: str,
                   column_schema: List[str] = None,
                   batch_size: int = 1000,
                   where_condition: List[Dict[str, Any]] = None,
                   where_relation: List[str] = None) -> List[List[Any]]:
    """获取所有数据的便捷函数"""
    return get_iwfactory_api().select_all_data(
        datasource_id, table_name, column_schema, batch_size, where_condition, where_relation)


if __name__ == "__main__":
    # 测试代码
    import os
    
    # 设置测试配置
    os.environ.setdefault('DATA_FACTORY_URL', 'http://localhost:8080')
    os.environ.setdefault('TENANT_ID', 'test_tenant')
    
    # 创建API实例
    api = IwFactoryDrAPI()
    
    # 测试表元数据规范
    test_columns = [
        {
            "columnEnglishName": "id",
            "columnDescribe": "用户编号",
            "columnType": "INT",
            "columnLength": 11,
            "numericScale": 0,
            "columnNullFlag": 1,
            "columnKeyFlag": 1
        },
        {
            "columnEnglishName": "name",
            "columnDescribe": "用户名称",
            "columnType": "VARCHAR",
            "columnLength": 50,
            "numericScale": 0,
            "columnNullFlag": 1,
            "columnKeyFlag": 0
        }
    ]
    
    try:
        result = api.std_metadata("test_datasource", test_columns)
        print("表元数据规范测试成功:", result)
    except Exception as e:
        print("表元数据规范测试失败:", str(e))
    
    print("IwFactoryDrAPI 初始化完成")