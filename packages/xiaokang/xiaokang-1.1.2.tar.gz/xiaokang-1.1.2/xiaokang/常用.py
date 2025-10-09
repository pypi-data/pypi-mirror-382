import datetime
import json
import sys
import time


def xk():
    """
    打印 函数介绍"""
    print(
        '''
报错信息(返回类型: str = 'str', 保存到文件: str = ''):
    """
    捕获异常并返回报错信息
    返回类型: 输入返回结果的数据类型
    保存到文件: 输入报错信息保存的文件名，若为空则不保存
    """

时间_文件():
    """
    返回可用于文件命名的时间
    """

时间_正常():
    """
    返回正常的时间
    """


时间_日志():
    """
    返回日志时间，存在时间戳
    """

'''
    )


def 报错信息(返回类型: str = "str", 保存到文件: str = ""):
    """
    捕获异常并返回报错信息
    ---
    返回类型: 输入返回结果的数据类型
    保存到文件: 输入报错信息保存的文件名，若为空则不保存
    """
    except_type, except_value, except_traceback = sys.exc_info()
    exc_dict = {
        "报错类型": str(except_type),
        "报错信息": str(except_value),
        "报错文件": except_traceback.tb_frame.f_code.co_filename,
        "报错行数": except_traceback.tb_lineno,
    }
    if 保存到文件:
        with open(保存到文件, "a", encoding="utf-8") as f:
            f.write("\n" * 2 + time.strftime("%Y-%m-%d %H:%M:%S\n") + str(exc_dict) + "\n" * 2)
    if 返回类型 == "str":
        return str(exc_dict)
    elif 返回类型 == "dict":
        return exc_dict
    elif 返回类型 == "json":
        return json.dumps(exc_dict, ensure_ascii=False, indent=4, separators=(",", ":"))
    else:
        return str(exc_dict)


def 时间_文件():
    """
    返回可用于文件命名的时间
    """
    return time.strftime("%Y-%m-%d_%H-%M-%S")


def 时间_正常():
    """
    返回正常的时间
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")


def 时间_日志():
    """
    返回日志时间，存在时间戳
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
