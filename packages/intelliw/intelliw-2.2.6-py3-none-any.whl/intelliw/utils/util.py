#!/usr/bin/env python
# coding: utf-8
import datetime
import inspect
import logging
import math
import string
import traceback
import types
import json
import os
import zipfile
from random import Random
import ctypes
import logging

from intelliw.config import config

logger = logging.getLogger()
random = Random()

try:
    import numpy as np

    np.set_printoptions(threshold=np.inf)
    has_np = True
except ImportError:
    has_np = False


def prepare_algorithm_parameters(alg_ps, value=None):
    value = value if value is not None else {}
    options = {}
    if alg_ps is not None:
        for k, v in enumerate(alg_ps):
            key = v['key'] if 'key' in v else None
            option = v['option'] if 'option' in v else None
            val = v['val'] if 'val' in v else None
            if key is not None:
                value[key] = val
                options[key] = option
                if option is not None and type(option) == dict and 'type' in option:
                    try:
                        val = to_type(val, option['type'])
                    except:
                        pass
                    value[key] = val
    return value, options


def prepare_model_parameters(model_ps, value=None, option=None):
    value = value if value is not None else {}
    if model_ps is not None:
        assert (type(model_ps) is dict)
        for k, v in model_ps.items():
            value[k] = v
            if option is not None and type(option) == dict and option.get(k) is not None and type(
                    option[k]) == dict and 'type' in option[k]:
                try:
                    v = to_type(v, option[k]['type'])
                except:
                    pass
                value[k] = v
    return value


def to_type(val, t: str):
    t = t.lower()
    if t == 'string' or t == 'str':
        return str(val)
    if t == 'enum':
        return str(val)
    if t == 'integer' or t == 'int':
        return int(val)
    if t == 'double' or t == 'float':
        return float(val)
    if t == 'boolean' or t == 'bool':
        if isinstance(val, bool):
            return val
        return val == 1 or val == '1' or val == 'True' or val == 'true'
    if t == 'array(int)' or t == 'array(integer)':
        return list(map(int, val.split(",")))
    if t == 'array(string)' or t == 'array(str)':
        return val.split(",")
    if t == 'array(array(int))' or t == 'array(array(integer))':
        return [list(map(int, filter(lambda n: n != "", val.split(","))))]
    return val


def get_json_encoder():
    global has_np
    if has_np:
        class JsonEncoder(json.JSONEncoder):
            """Convert numpy classes to JSON serializable objects."""

            def default(self, obj):
                if isinstance(obj, (np.integer, np.floating, np.bool_)):
                    return obj.item()
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
                    return obj.__str__()
                else:
                    return super(JsonEncoder, self).default(obj)

        return JsonEncoder
    else:
        return json.JSONEncoder


def generate_random_str(length=16):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def import_code(code, mod=None, name=None):
    if mod is None:
        # create blank module
        name = name if name is not None else generate_random_str()
        mod = types.ModuleType(name)
    exec(code, mod.__dict__)
    return mod


def get_first_element(mod):
    for element_name in dir(mod):
        element = getattr(mod, element_name)
        if inspect.isclass(element):
            return element()
        elif inspect.isfunction(element):
            return element


def is_empty_function(f):
    """Returns true if f is an empty function."""

    def empty_func():
        pass

    def empty_func_with_docstring():
        """Empty function with docstring."""
        pass

    def empty_lambda(): return None

    def empty_lambda_with_docstring(): return None

    empty_lambda_with_docstring.__doc__ = """Empty function with docstring."""

    def constants(f):
        """Return a tuple containing all the constants of a function without:
            * docstring
        """
        return tuple(
            x
            for x in f.__code__.co_consts
            if x != f.__doc__
        )

    return (
            f.__code__.co_code == empty_func.__code__.co_code and
            constants(f) == constants(empty_func)
    ) or (
            f.__code__.co_code == empty_func_with_docstring.__code__.co_code and
            constants(f) == constants(empty_func_with_docstring)
    ) or (
            f.__code__.co_code == empty_lambda.__code__.co_code and
            constants(f) == constants(empty_lambda)
    ) or (
            f.__code__.co_code == empty_lambda_with_docstring.__code__.co_code and
            constants(f) == constants(empty_lambda_with_docstring)
    )


def unzip_file(zipfilename: str, unziptodir=None):
    unziptodir = zipfilename.rstrip(".zip")
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0o755)
    if zipfile.is_zipfile(zipfilename):
        fz = zipfile.ZipFile(zipfilename, 'r')
        for file in fz.namelist():
            fz.extract(file, unziptodir)
    else:
        raise FileExistsError('This is not zip')
    return unziptodir


def get_worker_count(cpus, threads, is_multi_precess):
    worker, thread = 1, number_of_threads(cpus)
    if is_multi_precess:
        worker = number_of_workers(config.CPU_COUNT)

    # 自定义线程数
    if threads:
        try:
            thread = int(threads)
            if worker > 1:
                thread = math.floor(thread / worker)
            thread = min(128, max(1, thread))
        except Exception as e:
            traceback.print_exc()

    return worker, thread


def number_of_workers(core: str = ''):
    core = str(core).lower()
    num_core = 1
    try:
        if core:
            if 'm' in core:
                num_core = 1
            elif core.isdigit():
                num_core = int(core)
            else:
                num_core = math.ceil(float(core))
    except:
        pass
    # docker容器里取的是宿主机的
    # return (multiprocessing.cpu_count() * 2) + 1
    # 最优是 2*core+1
    # 但是服务器和算法程序都太脆弱了， 所以减少点
    # return (2 * num_core) + 1
    return min(8, num_core)


def number_of_threads(core: str = ''):
    core = str(core).lower()
    num_core = 1
    try:
        if core:
            if 'm' in core.lower():
                num_core = 1
            elif core.isdigit():
                num_core = int(core)
            else:
                num_core = math.ceil(float(core))
    except:
        pass
    return min(64, 2 * num_core + 1)


def stop_thread(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        logger.info("invalid thread id")
        # raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def gen_random_str(length=4):
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def string_to_function(func_str, func_name):
    """
    将包含函数定义的字符串转换为实际的函数。

    :param func_str: 包含函数定义的字符串
    :param func_name: 函数的名称
    :return: 动态定义的函数
    """
    # 创建一个字典作为命名空间
    local_namespace = {}

    # 尝试执行字符串代码
    try:
        exec(func_str, globals(), local_namespace)
    except Exception as e:
        print(f"Error executing function string: {e}")
        return None

    # 从命名空间中提取函数
    func = local_namespace.get(func_name)

    if func is None:
        print(f"Function {func_name} is not defined in the provided string.")
        return None

    return func

def use_ipv6_by_env():
    '''
    是否使用ipv6
    :return:
    '''
    return os.environ.get('USE_IPV6', 'false').lower() == 'true' or os.environ.get('useIPv6', 'false').lower() == 'true'


DB_NUM_TYPE = [
    "TINYINT",
    "SMALLINT",
    "MEDIUMIN",
    "INT",
    "INTEGER",
    "BIGINT",
    "NUMERIC",
    "FLOAT",
    "DOUBLE",
    "DECIMAL",
]
