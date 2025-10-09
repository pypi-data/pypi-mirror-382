from xiaokang.常用 import 报错信息, xk, 时间_文件, 时间_正常, 时间_日志


def test_报错信息():
    try:
        print("1" + 1)
    except:
        print(报错信息("json"))


def test_xk():
    xk()


def 打印时间文件():
    print(时间_文件())


def 打印时间正常():
    print(时间_正常())


def 打印时间日志():
    print(时间_日志())


test_xk()
