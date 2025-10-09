'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2025-08-29 15:30:00
LastEditors: AI Assistant
Description: 数据工厂物化表数据源获取数据
FilePath: /iw-algo-fx/intelliw/datasets/datasource_iwfactory_dr_data.py
'''
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
import json
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, DataSourceType, \
    DatasetSelector
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config
from intelliw.datasets.utils.iwfactory_dr_api import IwFactoryDrAPI

logger = _get_framework_logger()


def err_handler(request, exception):
    print("请求出错,{}".format(exception))


class DataSourceIwFactoryDrData(AbstractDataSource):
    """
    数据工场物化表数据源
    """

    def __init__(self, data_address, data_meta_address, datasoure_id, table_id, table_name, user_id, fields=None, data_filter_condition = None, tenant_id=None):
        """
        语义模型数据源
        :param data_address:   获取数据 url
        :param fields: 获取数据表字段
        :param table_id:   表Id
        """
        self.data_address = data_address
        self.data_meta_address = data_meta_address
        self.table_id = table_id
        self.user_id = user_id
        self.fields = fields
        self.datasoure_id = datasoure_id
        self.table_name = table_name
        self.__total = None
        self.__meta = []
        self.tenant_id = tenant_id if tenant_id is not None else config.TENANT_ID
        
        user_url_map = {
            'select_data': self.data_address,  # 批量查询数据
            'table_metadata': self.data_meta_address,  # 查询元数据
        }

        self.iwfactory_dr_api = IwFactoryDrAPI(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            user_url_map=user_url_map
            )

        self.conditions = None
        self.where_condition = []
        if data_filter_condition is None or len(data_filter_condition) == 0:
            data_filter_condition = config.DATA_FILTER_CONDITION
            try:
                self.conditions = json.loads(data_filter_condition).get('conditions')
                self.where_condition = self._build_conditions()
                logger.info("parse data_filter_condition success, config is %s, where_condition is %s", data_filter_condition, self.where_condition)
            except Exception as e:
                self.conditions = None
                self.where_condition = []

    def total(self):
        """获取数据总行数"""
        if self.__total is not None:
            return self.__total

        try:
            # 使用新的API接口获取数据总数和元数据
            
            # 构建查询条件
            where_condition = self.where_condition
            
            # 使用分页查询，获取第一页的数据来获取总数
            result = self.iwfactory_dr_api.select_data_paginated(
                datasource_id=self.datasoure_id,
                table_name=self.table_name,
                column_schema=[],  # 空数组表示获取所有字段
                page_size=1,
                current_page=1,
                where_condition=where_condition
            )
            
            # 获取数据模型
            data_model = result.get('data', {}).get('dataModel', {})
            page_info = data_model.get('page', {})
            
            # 获取总数
            count = page_info.get('totalCount', 0)
            if isinstance(count, int):
                self.__total = count
            else:
                self.__total = 0
            
        except Exception as e:
            msg = f"获取行数失败: {str(e)}, datasource_id: {self.datasoure_id}, table_name: {self.table_name}"
            raise DataSourceReaderException(msg)
            
        return self.__total
    
    def get_meta(self):
        if self.__meta is not None and len(self.__meta) > 0:
            return self.__meta
        try:
            # 获取字段元数据
            result = self.iwfactory_dr_api.get_table_metadata(self.table_id)
            
            # 获取字段元数据
            column_schema = result.get('data', {}).get('columns', [])
            
            # 构建字段元数据信息
            tmp_meta = []
            for col in column_schema:
                tmp_meta.append({
                    "code": col.get('columnEnglishName', ''),
                    "label": col.get('columnEnglishName', ''),
                    "type": col.get('columnType', 'varchar')  # 默认类型，实际类型需要根据数据推断
                })
            
            self.__meta = tmp_meta
            return self.__meta
        except Exception as e:
            msg = f"获取元数据失败: {str(e)}, datasource_id: {self.datasoure_id}, table_name: {self.table_name}"
            raise DataSourceReaderException(msg)
    
    def _build_conditions(self):
        """将旧的过滤条件格式转换为新的API格式"""
        if not self.conditions:
            return []
        
        new_conditions = []
        for condition in self.conditions:
            # 转换旧的condition格式到新的格式
            operator_mapping = {
                'between': 'between',
                '=': '=',
                '>': '>',
                '<': '<',
                '>=': '>=',
                '<=': '<=',
                '!=': '!=',
                '<>': '!=',
                'like': 'like',
                'not like': 'not like',
                'is null': 'is null',
                'is not null': 'is not null',
                'in': 'in'
            }
            
            op = condition.get('op', '=')
            name = condition.get('name', '')
            
            new_condition = {
                "columnName": name,
                "operator": operator_mapping.get(op, op)
            }
            
            # 处理不同操作符的值
            if op == 'between':
                # between操作符需要两个值
                new_condition["columnValues"] = [condition.get('v1'), condition.get('v2')]
            elif op == 'in':
                # in操作符支持多个值
                values = condition.get('v1', '')
                if isinstance(values, str):
                    values = [v.strip() for v in values.split(',')]
                new_condition["columnValues"] = values
            elif op in ['is null', 'is not null']:
                # 空值检查不需要值
                new_condition.pop("columnValues", None)
            else:
                # 其他操作符使用单个值
                new_condition["columnValues"] = [condition.get('v1')]
            
            new_conditions.append(new_condition)
        
        return new_conditions
    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.data_address, self.datasoure_id, self.table_id, self.table_name, self.fields,self.iwfactory_dr_api, self.total(), self.get_meta(), self.user_id, pagesize, transform_function, self.where_condition)

    class __Reader:
        def __init__(self, data_address, datasoure_id, table_id, table_name, fields, iwfactory_dr_api: IwFactoryDrAPI, total, meta, user_id, pagesize=5000, transform_function=None, where_condition: list = None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            self.logger = _get_framework_logger()
            self.data_address = data_address
            self.datasoure_id = datasoure_id
            self.table_id = table_id
            self.table_name = table_name
            self.fields = fields
            self.iwfactory_dr_api = iwfactory_dr_api
            self.origin_page_size = pagesize
            self.page_size = max(100, pagesize)
            self.page_size = pagesize
            self.page_num = 1
            self.total_page_num = 1
            self.total_read = 0
            self.total_rows = total
            self.user_id = user_id
            self.meta = meta
            self.worker = min(3, max(1, os.cpu_count()))
            self.transform_function = transform_function
            self.where_condition = where_condition
            logger.info(f'数据获取中: 启用的获取线程 {self.worker} 条')

        def get_data_bar(self):
            """数据拉取进度条"""
            try:
                proportion = round(
                    (self.total_read / self.total_rows) * 100, 2)
                logger.info(
                    f"数据获取中: {self.total_read}/{self.total_rows}, 进度{proportion}%")
            except:
                pass

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def reset(self, fields: list=None, page_size: int=None):
            """ 迭代重置 """
            self.page_num = 1
            self.total_page_num = 1
            self.total_read = 0
            self.fields = fields
            if page_size:
                self.page_size = page_size
            else:
                self.page_size = self.origin_page_size
            logger.info(f'数据读取重置, page_num: {self.page_num}, total_read: {self.total_read}, fields: {self.fields}, page_size: {self.page_size}') 

        def get_meta(self):
            """获取元数据"""
            return self.meta
        
        def get_total_rows(self):
            """获取总数据行数"""
            return self.total_rows

        

        def __next__(self):
            if self.total_read >= self.total_rows:
                logger.info('数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                raise StopIteration

            self.get_data_bar()
            self.total_page_num = (self.total_rows - 1) // self.page_size + 1
            try:
                with ThreadPoolExecutor(max_workers=self.worker) as executor:
                    futures, data_result = [], []
                    for i in range(self.worker):
                        if self.page_num > self.total_page_num:
                            break
                        futures.append(executor.submit(
                            self._read_page, self.page_num, self.page_size, self.datasoure_id, self.table_name, self.where_condition
                        ))
                        self.page_num += 1

                    for f in futures:
                        data_result.extend(f.result())
                    self.total_read += len(data_result)
                    if len(data_result) == 0:
                        logger.info(
                            '数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                        raise StopIteration

                    return_data = {"result": data_result, "meta": self.meta}
                    if self.transform_function is not None:
                        return_data = self.transform_function(return_data)
                    return return_data
            except Exception as e:
                logger.exception(
                    f"数据工厂模型数据源读取失败, data_address: [{self.table_id}]")
                raise DataSourceReaderException(f'数据工厂模型数据源读取失败: {e}')

        def _get_meta(self, meta):
            if self.meta == []:
                self.meta = meta
            return self.meta

        def _data_process(self, result):
            assert result is not None, "数据工厂模型数据接口未返回任何有效数据"
            data = result["data"]
            assert data is not None, f"接口返回无数据, 请联系数据负责人：{result}"
            if len(data) > 0:
                self._get_meta(data['meta'])
            return data['result']

        def _data_process_new(self, result):
            """处理新的物化表API响应格式"""
            assert result is not None, "物化表数据接口未返回任何有效数据"
            assert result.get("code") == 0, f"接口返回错误, code: {result.get('code')}, msg: {result.get('msg')}"
            
            data = result.get("data")
            assert data is not None, f"接口返回无数据, 请联系数据负责人：{result}"
            
            data_model = data.get("dataModel")
            assert data_model is not None, f"接口返回格式错误, 无dataModel字段: {data}"
            
            # 获取列schema和模型数据
            # column_schema = data_model.get("columnSchema", [])
            model_data = data_model.get("modelData", [])
            
            return model_data

        def _read_page(self, page_index, page_size, datasoure_id, table_name, where_condition: list = []):
            """
            使用新的API接口获取分页数据
            :param page_index: 页码，从 1 开始
            :param page_size:  每页大小
            :return:
            """
            try:
                # 构建字段列表
                column_schema = self.fields if self.fields is not None else None
                
                # 使用分页查询
                result = self.iwfactory_dr_api.select_data_paginated(
                    datasource_id=datasoure_id,
                    table_name= table_name,
                    column_schema=column_schema,
                    page_size=page_size,
                    current_page=page_index,
                    where_condition=where_condition
                )
                logger.info(f"result: {result}")
                return self._data_process_new(result)
                
            except Exception as e:
                logger.error(f"分页获取数据失败: {str(e)}")
                raise DataSourceReaderException(f'分页获取数据失败: {e}')


DatasetSelector.register_func(DataSourceType.IW_FACTORY_DR_DATA, DataSourceIwFactoryDrData, {
    "data_address": "INPUT_ADDR",
    "data_meta_address": "INPUT_DATA_META_ADDR",
    "datasoure_id": "INPUT_MODEL_ID",
    "table_id": "TABLE_ID",
    "table_name": "TABLE_NAME",
    "user_id": "USER_ID",
    })
