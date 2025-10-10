""":,
kndxhz_tools

A collection of useful tools for various tasks.
"""

__version__ = "0.3"
__author__ = "kndxhz"


def version() -> str:
    """返回版本号"""
    return __version__


def author() -> str:
    """返回作者"""
    return __author__


def get_ip(use_all: bool = False) -> list:
    """


    作用:
        获取当前主机的公网IP地址

    参数:
        use_all - 是否获取全部,False则获取优先地址 - bool (可选,默认值: False)

    返回:
        如果use_all为True,则返回一个包含所有IP地址的列表,否则返回一个包含一个优先地址的字符串
        列表:```[ip.sb,4.ipw.cn,6.ipw.cn,test.ipw.cn]```


    """
    import subprocess

    if use_all:
        ip = []
        ip.append(subprocess.check_output("curl ip.sb", shell=True).decode().strip())
        ip.append(subprocess.check_output("curl 4.ipw.cn", shell=True).decode().strip())
        ip.append(subprocess.check_output("curl 6.ipw.cn", shell=True).decode().strip())
        ip.append(
            subprocess.check_output("curl test.ipw.cn", shell=True).decode().strip()
        )
    else:
        ip = subprocess.check_output("curl test.ipw.cn", shell=True).decode().strip()

    return ip


def write_csv(*data, path: str, mode: str = "w", end: str = "\n") -> bool:
    """
    作用:
        将数据写入CSV文件

    参数:
        data - 要写入的数据 - str 或 list
        path - 要写入的文件路径 - str
        mode - 写入模式 - str (可选,默认值: "w")
        end - 换行符 - str (可选,默认值: "\\n")

    返回:
        写入成功返回True,否则返回False

    示例:```write_csv("1,2,3", "test.csv")```
    """

    try:
        with open(path, mode, newline="") as f:
            if len(data) == 1 and isinstance(data[0], list):
                f.write(",".join(data[0]))
            else:
                f.write(",".join(data) + end)
        return True
    except:
        return False


print(f"""欢迎使用 kndxhz_tools v{__version__}~""")


def run_time(func):
    """
    作用:
        装饰器,记录函数运行时间

    示例:
    ``` python
    @run_time
    def main():
        pass
    main()
    """
    import time

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        name = func.__name__
        end_time = time.time()
        print(f"{name} 函数运行时间: {end_time - start_time}秒")
        return result

    return wrapper


def avg(*args) -> float:
    """
    作用:
        计算品均值

    参数:
        任何数字参数 - 计算平均值

    返回:
        返回平均值

    示例:```avg(77,88,99)```
    """
    return sum(args) / len(args)


if __name__ == "__main__":

    # main()
    pass
