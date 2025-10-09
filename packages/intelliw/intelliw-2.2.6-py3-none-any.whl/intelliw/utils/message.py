#!/usr/bin/env python
# coding: utf-8

import json
from intelliw.utils import get_json_encoder
from intelliw.config import config

msg_id = 0


class ErrorCode:
    limit_exceeded = '013-501-015001'
    invalid_request = '013-501-015002'


def get_msg_id():
    global msg_id
    msg_id += 1
    return msg_id


####### return msg #########
class HealthCheckResponse:
    def __init__(self, code, typ, msg='', data=None):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data

    def _format(self):
        return {
            "extrainfo": {
                "status": self.code,
                "message": self.msg,
            },
            "data": self.data
        }

    def __str__(self):
        return json.dumps(self._format(), cls=get_json_encoder(), ensure_ascii=False)

    def __call__(self):
        return self._format()


class APIResponse:
    def __init__(self, code, typ, msg='', data=None):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data

    def _format(self):
        result = self.data or self.msg
        if self.code in [ErrorCode.invalid_request, ErrorCode.limit_exceeded] \
                and isinstance(result, str):
            return {'code': self.code, 'message': result}

        if config.API_EXTRAINFO:
            return {
                "extrainfo": {
                    "status": self.code,
                    "message": self.msg,
                },
                "data": result
            }
        else:
            return result

    def __str__(self):
        return json.dumps(self._format(), cls=get_json_encoder(), ensure_ascii=False)

    def __call__(self):
        return self._format()


err_invalid_validate_request = APIResponse(500, "validate", "无效验证请求")


class CommonResponse:
    def __init__(self, code, typ, msg='', data='', **kwargs):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data
        self.other = kwargs

    def _format(self):
        keymap = {
            "id": config.INSTANCE_ID,
            "serviceId": config.SERVICE_ID,
            "msgid": get_msg_id(),
            "token": config.TOKEN,
            "code": self.code,
            "type": self.typ,
            "message": self.msg,
            "data": self.data
        }
        return {**keymap, **self.other}

    def __str__(self):
        return json.dumps(self._format(), cls=get_json_encoder(), ensure_ascii=False)

    def __call__(self):
        return self._format()


ok_infer_online_status = CommonResponse(200, "infer", "status ok")
err_import_alg_invalid_path = CommonResponse(500, "importalg", "无效算法包")
err_import_alg_missing_algorithpy = CommonResponse(
    500, "importalg", "算法包必须包含: algorithm.py")
err_import_alg_missing_algorithyaml = CommonResponse(
    500, "importalg", "算法包必须包含: algorithm.yaml")
err_import_alg_invalid_algorithpy_format = CommonResponse(
    500, "importalg", "algorithm.py 内容不符合规范")
err_import_alg_invalid_algorithyaml_format = CommonResponse(
    500, "importalg", "algorithm.yaml 内容不符合规范")
err_missing_router_func = CommonResponse(
    500, "importalg", 'algorithm.yaml错误, 自定义api对应函数不存在')

err_import_model_missing_modelyaml = CommonResponse(
    500, "importmodel", "模型包必须包含: model.yaml")
err_import_alg_invalid_modelyaml_format = CommonResponse(
    500, "importmodel", "model.yaml 内容不符合规范")
err_import_model_invalid = CommonResponse(500, "importmodel", "模型参数文件无效")

ok_import_algorithm = CommonResponse(200, "importalg", "框架导入算法成功")
ok_import_model = CommonResponse(200, "importmodel", "框架导入模型成功")
err_import_algorithm = CommonResponse(500, "importalg", "框架导入算法失败")
err_import_model = CommonResponse(500, "importmodel", "框架导入模型失败")
err_transform_support_type = \
    CommonResponse(500, "importmodel",
                   "当前特征工程只支持四种类型，pre-train(训练前), pre-predict(推理前), pre-train(推理后)")

ok_train_finish = CommonResponse(200, 'train_finish', '', '')
err_empty_train_data = CommonResponse(500, "train_finish", "训练错误-训练数据为空")
err_empty_val_data = CommonResponse(500, "train_finish", "训练错误-验证数据为空")
err_train = CommonResponse(500, "train_finish", "训练错误-算法程序错误")
err_dataset = CommonResponse(500, "train_finish", '数据集存在问题')
err_function_process = CommonResponse(500, "train_finish", "特征值/数据处理错误")
err_streaming_not_supported = CommonResponse(500, "train_finish", "训练错误-未实现流式训练接口")


ok_custom_finish = CommonResponse(200, 'custom_finish', '', '')
err_custom_process = CommonResponse(500, "custom_finish", "自定义构建算法执行失败")

err_missing_algorithm_mod = CommonResponse(
    500, "importalg", "算法模块文件 algorithm.py 无效")
err_missing_algorithm_class = CommonResponse(
    500, "importalg", "算法模块文件没有定义定义类 Algorithm ")
err_missing_train_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 train 函数")
err_missing_train_parameter = CommonResponse(
    500, "importalg", "算法类 Algorithm 函数 train 参数定义不正确")
err_missing_report_train_info_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 report_train_info 函数")
err_missing_infer_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 infer 函数")
err_missing_infer_parameter = CommonResponse(500,
                                             "importalg",
                                             "算法类 Algorithm 函数 infer 参数定义不正确， 应该为 infer(self, data)")
err_missing_init_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 __init__ 函数")
err_missing_init_parameter = CommonResponse(500,
                                            "importalg",
                                            "算法类 Algorithm 函数 __init__ 参数定义不正确， 应该为 __init__(self, parameters)")
err_missing_load_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 load 函数")
err_missing_load_parameter = CommonResponse(500,
                                            "importalg",
                                            "算法类 Algorithm 函数 load 参数定义不正确， 应该为 load(self, path)")
err_missing_save_method = CommonResponse(
    500, "importalg", "算法模块文件类 Algorithm 缺少 save 函数")
err_missing_save_parameter = CommonResponse(500,
                                            "importalg",
                                            "算法类 Algorithm 函数 save 参数定义不正确， 应该为 save(self, path)")
